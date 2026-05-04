from flask import Flask, jsonify, request, render_template
import psycopg2
import os
import requests

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# -----------------------
# LOCAL FALLBACK DATA
# -----------------------
students_local = [
        {"id": 1, "name": "Daniel", "surname": "Barta", "personality": "Funny sarcastic chill guy"},
    {"id": 2, "name": "Matúš", "surname": "Bucko", "personality": "Smart quiet logical"},
    {"id": 3, "name": "Adrian", "surname": "Červenka", "personality": "Energetic talkative"},
    {"id": 4, "name": "Martin", "surname": "Deglovič", "personality": "Calm slightly lazy"},
    {"id": 5, "name": "Samuel", "surname": "Haring", "personality": "Competitive gamer"},
    {"id": 6, "name": "Matúš", "surname": "Holečka", "personality": "Helpful friendly"},
    {"id": 7, "name": "Martin", "surname": "Jelínek", "personality": "Sporty active"},
    {"id": 8, "name": "Tomáš", "surname": "Jurčák", "personality": "Meme lover funny"},
    {"id": 9, "name": "Milan", "surname": "Kokina", "personality": "Serious focused"},
    {"id": 10, "name": "Patrik", "surname": "Korba", "personality": "Chill relaxed"},
    {"id": 11, "name": "Marcus", "surname": "Martiš", "personality": "Confident leader type"},
    {"id": 12, "name": "Samuel", "surname": "Martiš", "personality": "Quiet smart"},
    {"id": 13, "name": "Marko", "surname": "Mihalička", "personality": "Chaotic funny"},
    {"id": 14, "name": "Rastislav", "surname": "Paták", "personality": "Logical thinker"},
    {"id": 15, "name": "Matej", "surname": "Randziak", "personality": "Supportive friendly"},
    {"id": 16, "name": "Dávid", "surname": "Škula", "personality": "Gaming addicted"},
    {"id": 17, "name": "Samuel", "surname": "Uhrík", "personality": "Sarcastic witty"},
    {"id": 18, "name": "Janka", "surname": "Vargová", "personality": "Kind caring"},
    {"id": 19, "name": "Lukáš", "surname": "Vindiš", "personality": "Sporty competitive"},
]

# -----------------------
# DB CONNECT
# -----------------------
def get_db():
    if not DATABASE_URL:
        return None
    return psycopg2.connect(DATABASE_URL)

# -----------------------
# FRONTEND
# -----------------------
@app.route("/")
def home():
    return render_template("index.html")

# -----------------------
# STUDENTS
# -----------------------
@app.route("/api/students")
def students():
    conn = get_db()

    if not conn:
        return jsonify(students_local)

    cur = conn.cursor()
    cur.execute("SELECT id, name, surname FROM students")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {"id": r[0], "name": r[1], "surname": r[2]}
        for r in rows
    ])

# -----------------------
# CHAT AI
# -----------------------
@app.route("/api/chat/<int:student_id>", methods=["POST"])
def chat(student_id):
    message = request.json["message"]

    conn = get_db()

    if conn:
        cur = conn.cursor()
        cur.execute("SELECT name, personality FROM students WHERE id=%s", (student_id,))
        student = cur.fetchone()
        cur.close()
        conn.close()
    else:
        student = next((s for s in students_local if s["id"] == student_id), None)

    if not student:
        return {"error": "not found"}, 404

    name, personality = student

    if not OPENAI_API_KEY:
        return {"reply": f"{name}: {message}"}

    prompt = f"""
You are a student named {name}.
Personality: {personality}

Rules:
- short casual replies
- no AI mention
- act like real teenager
"""

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ]
        }
    )

    try:
        reply = response.json()["choices"][0]["message"]["content"]
    except:
        reply = "AI error"

    return {"reply": reply}


if __name__ == "__main__":
    app.run(debug=True)