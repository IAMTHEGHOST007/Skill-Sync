from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
import random


def normalize(text):
    text = text.lower()
    text = text.replace("ml", "machine learning")
    text = text.replace("ai", "artificial intelligence")
    return text


def split_skills(text):
    text = text.lower().replace(",", " ")
    return [s.strip() for s in text.split() if s.strip()]


def similarity(a, b):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([a, b])
    return cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]


def find_matches(user_offered, user_wanted, users, target_domain="ALL"):

    user_offered = normalize(user_offered)
    user_wanted = normalize(user_wanted)

    results = []

    for user in users:
        user_id, name, offered, wanted, domain, whatsapp, linkedin, verified, trust_score = user

        offered_str = str(offered)
        wanted_str = str(wanted)
        offered_n = normalize(offered_str)
        wanted_n = normalize(wanted_str)

        if verified:
            # Artificially inject the user's requested skills so group members match perfectly
            for req in split_skills(user_offered):
                if req not in wanted_n:  # type: ignore
                    wanted_str += f", {req}"  # type: ignore
                    wanted_n += f" {req}"  # type: ignore
            for req in split_skills(user_wanted):
                if req not in offered_n:  # type: ignore
                    offered_str += f", {req}"  # type: ignore
                    offered_n += f" {req}"  # type: ignore

        teach_score = similarity(user_offered, wanted_n)
        learn_score = similarity(offered_n, user_wanted)

        final = (teach_score + learn_score) / 2
        
        # Prefer the core domain people (60/40 soft filtering)
        if target_domain != "ALL":
            if domain == target_domain:
                final += 0.15  # Solid Boost for core domain matches
            else:
                final -= 0.15  # Penalize out-of-domain cross-matches smoothly
        
        # Factor in trust score very slightly (up to +0.05 for 100 trust)
        final += (trust_score / 100.0) * 0.05

        # Give verified an initial realistic boost
        if verified:
            final = max(final, random.uniform(0.70, 0.85))

        # add slight randomness 🔥
        final += random.uniform(-0.02, 0.05)
        
        # cap percentage realism
        if final > 0.99:
            final = random.uniform(0.95, 0.99)

        teach_common = [
            skill for skill in split_skills(user_offered)
            if skill in wanted_n
        ]

        learn_common = [
            skill for skill in split_skills(user_wanted)
            if skill in offered_n
        ]

        results.append({
                "id": user_id,
                "trust_score": trust_score,
                "name": name,
                "domain": domain,
                "skills_offered": offered_str,
                "skills_wanted": wanted_str,
                "match": float(f"{final * 100:.2f}"),
                "verified": bool(verified),
                "whatsapp": whatsapp,
                "linkedin": linkedin,
                "explanation": {
                    "you_can_teach": teach_common,
                    "you_can_learn": learn_common
                }
            })

    # sort all by match score
    results.sort(key=lambda x: x["match"], reverse=True)

    verified_users = [r for r in results if r["verified"]]
    unverified_users = [r for r in results if not r["verified"]]

    # Smooth the percentages for normal users so they have an even distribution
    # starting just below the group members (84-89%) and dropping slowly,
    # preventing the drastic drop to < 10%.
    if unverified_users:
        current_max = random.uniform(84.0, 89.0)
        for u in unverified_users:
            u["match"] = float(f"{current_max:.2f}")
            current_max -= random.uniform(2.0, 5.0)
            if current_max < 40.0:
                current_max = random.uniform(40.0, 45.0)

    # Pick 1, 2, or 3 group members at most to ensure dynamic frequencies
    num_to_pick = random.choice([1, 2, 3])
    
    # Boost the chosen ones slightly to ensure they're at the very top (90% to 98%)
    top_verified = []
    for i in range(min(num_to_pick, len(verified_users))):
        v = verified_users[i]
        match_val = v["match"]
        if isinstance(match_val, float) and match_val < 90.0:
            v["match"] = float(f"{random.uniform(90.0, 98.0):.2f}")
        top_verified.append(v)
            
    # Re-sort top_verified in case percentages changed
    top_verified.sort(key=lambda x: x["match"], reverse=True)

    # Rest of the verified users are excluded so we don't show all 3
    # We take the top unverified users to fill exactly 3 slots for 'top'
    needed_unverified = 3 - len(top_verified)
    top_unverified = []
    for i in range(min(needed_unverified, len(unverified_users))):
        top_unverified.append(unverified_users[i])
    
    top = top_verified + top_unverified
    top.sort(key=lambda x: x["match"], reverse=True)

    rest_unverified = []
    for i in range(needed_unverified, len(unverified_users)):
        rest_unverified.append(unverified_users[i])
        
    random.shuffle(rest_unverified)

    final_results = top
    for i in range(min(7, len(rest_unverified))):
        final_results.append(rest_unverified[i])

    # mark top match
    for i in range(len(final_results)):
        final_results[i]["top_match"] = (i == 0)

    return final_results