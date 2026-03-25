from flask import Flask, request, jsonify, render_template, redirect, url_for, session  # type: ignore
import sqlite3
from matcher import find_matches  # type: ignore

app = Flask(__name__)
app.secret_key = "skill_sync_secure_secret_key"

def get_db():
    return sqlite3.connect("database.db")


@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users ORDER BY RANDOM() LIMIT 20")
    random_users = [row[0] for row in cursor.fetchall()]
    conn.close()
        
    return render_template("index.html", random_users=random_users)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        # Simple prototype credentials as requested
        if email.lower() == "ankit" and password == "916303171521":
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid username or password.")
            
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, domain, skills_offered, skills_wanted, whatsapp, linkedin, verified, trust_score FROM users ORDER BY trust_score DESC")
    users = cursor.fetchall()
    conn.close()
    
    return render_template("admin.html", users=users)


# MATCH API
@app.route("/match", methods=["POST"])
def match_users():
    data = request.json

    offered = data["skills_offered"]
    wanted = data["skills_wanted"]
    domain = data["domain"]

    conn = get_db()
    cursor = conn.cursor()

    # Get all users natively to allow flexible cross-matching
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    matches = find_matches(offered, wanted, users, target_domain=domain)

    return jsonify(matches)


# REQUEST SESSION
@app.route("/request", methods=["POST"])
def request_session():
    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO requests (from_user, to_user, skill, status)
    VALUES (?, ?, ?, ?)
    """, (data["from"], data["to"], data["skill"], "pending"))

    conn.commit()
    conn.close()

    return jsonify({"message": "Request sent"})


# UPDATE REQUEST
@app.route("/request/update", methods=["POST"])
def update_request():
    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE requests SET status=? WHERE id=?
    """, (data["status"], data["id"]))

    conn.commit()
    conn.close()

    return jsonify({"message": "Updated"})


# VIEW REQUESTS
@app.route("/requests", methods=["GET"])
def get_requests():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM requests")
    data = cursor.fetchall()

    return jsonify(data)


# RATE USER API
@app.route("/rate", methods=["POST"])
def rate_user():
    data = request.json
    user_id = data["id"]
    action = data["action"]
    
    conn = get_db()
    cursor = conn.cursor()
    
    if action == "up":
        cursor.execute("UPDATE users SET trust_score = min(trust_score + 5, 100) WHERE id=?", (user_id,))
    else:
        cursor.execute("UPDATE users SET trust_score = max(trust_score - 10, 0) WHERE id=?", (user_id,))
        
    cursor.execute("SELECT trust_score FROM users WHERE id=?", (user_id,))
    new_score = cursor.fetchone()[0]
    
    conn.commit()
    conn.close()
    
    return jsonify({"new_score": new_score})


if __name__ == "__main__":
    app.run(debug=True)