import sqlite3
import random

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS requests")

cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    skills_offered TEXT,
    skills_wanted TEXT,
    domain TEXT,
    whatsapp TEXT,
    linkedin TEXT,
    verified INTEGER,
    trust_score INTEGER
)
""")

cursor.execute("""
CREATE TABLE requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_user TEXT,
    to_user TEXT,
    skill TEXT,
    status TEXT
)
""")

cse = ["python","ml","data science","web dev","react","node","flask","sql"]
ece = ["control systems","signals","dsp","electronics","embedded","iot"]

first_names = ["Rahul","Priya","Amit","Sneha","Karan","Neha","Rohit","Ananya",
         "Vikram","Pooja","Aditya","Meera","Sahil","Divya","Harsh",
         "Arjun","Kavya","Rakesh","Nisha","Manoj","Aishwarya","Deepak",
         "Varun","Shreya","Naveen","Tejas","Lakshmi","Gokul","Pranav","Ishita"]
last_names = ["Sharma", "Verma", "Gupta", "Kumar", "Singh", "Das", "Patel", "Reddy", "Rao", "Nair", "Iyer", "Yadav", "Jain", "Chopra", "Chauhan", "Bhat"]

def pick(skills):
    return ", ".join(random.sample(skills, random.randint(2,3)))

users = []

cse = ["python","ml","data science","web dev","react","node","flask","sql"]
ece = ["control systems","signals","dsp","electronics","embedded","iot"]
all_skills_str = ", ".join(cse + ece)
cse_skills_str = ", ".join(cse)
ece_skills_str = ", ".join(ece)

# Ensure only the 3 specific group members are verified
group_members = [
    ("Ankit", pick(cse), pick(cse + ece), "CSE", "916303171521", "https://www.linkedin.com/in/ankit-bharatula"),
    ("Madhusai", pick(cse), pick(cse + ece), "CSE", "918106649793", "https://www.linkedin.com/in/madhu-sai-kancham-2784b8329"),
    ("Saketh", pick(ece), pick(cse + ece), "ECE", "919030695136", "https://www.linkedin.com/in/k-shanmukha-saketh-930944376")
]

for name, offered, wanted, domain, whatsapp, linkedin in group_members:
    users.append((name, offered, wanted, domain, whatsapp, linkedin, 1, 100))

# Generate 150 unverified dummy profiles to expand the database
for i in range(150):
    domain = "CSE" if random.random() > 0.4 else "ECE"
    offered = pick(cse if domain=="CSE" else ece)
    wanted = pick(cse + ece)
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    users.append((
        f"{first_name} {last_name}",
        offered,
        wanted,
        domain,
        f"9198{random.randint(10000000, 99999999)}",
        f"https://linkedin.com/in/{first_name.lower()}{last_name.lower()}{i}",
        0,
        random.randint(60, 95)
    ))

cursor.executemany("""
INSERT INTO users (name, skills_offered, skills_wanted, domain, whatsapp, linkedin, verified, trust_score)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", users)

conn.commit()
conn.close()

print("Database ready")