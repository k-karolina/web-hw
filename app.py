# app.py

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
    {"id": 19, "name": "Lukáš", "surname": "Vindiš", "personality": "Sporty competitive"}
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
# GET STUDENTS
# -----------------------
@app.route("/api/students")
def students():

    conn = get_db()

    # LOCAL MODE
    if not conn:
        return jsonify(students_local)

    # DATABASE MODE
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, surname
        FROM students
        ORDER BY id
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {
            "id": r[0],
            "name": r[1],
            "surname": r[2]
        }
        for r in rows
    ])

# -----------------------
# ADD STUDENT
# -----------------------
@app.route("/api/students", methods=["POST"])
def add_student():

    data = request.json

    conn = get_db()

    # LOCAL
    if not conn:

        new_id = len(students_local) + 1

        students_local.append({
            "id": new_id,
            "name": data["name"],
            "surname": data["surname"],
            "personality": data["personality"]
        })

        return {"status": "added"}

    # DATABASE
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO students
        (name, surname, personality)
        VALUES (%s, %s, %s)
    """, (
        data["name"],
        data["surname"],
        data["personality"]
    ))

    conn.commit()

    cur.close()
    conn.close()

    return {"status": "added"}

# -----------------------
# EDIT STUDENT
# -----------------------
@app.route("/api/students/<int:student_id>", methods=["PUT"])
def edit_student(student_id):

    data = request.json

    conn = get_db()

    # LOCAL
    if not conn:

        for s in students_local:

            if s["id"] == student_id:
                s["name"] = data["name"]
                s["surname"] = data["surname"]
                s["personality"] = data["personality"]

        return {"status": "edited"}

    # DATABASE
    cur = conn.cursor()

    cur.execute("""
        UPDATE students
        SET
            name=%s,
            surname=%s,
            personality=%s
        WHERE id=%s
    """, (
        data["name"],
        data["surname"],
        data["personality"],
        student_id
    ))

    conn.commit()

    cur.close()
    conn.close()

    return {"status": "edited"}

# -----------------------
# CHAT AI
# -----------------------
@app.route("/api/chat/<int:student_id>", methods=["POST"])
def chat(student_id):

    data = request.json
    message = data["message"]

    conn = get_db()

    # DATABASE MODE
    if conn:

        cur = conn.cursor()

        cur.execute("""
            SELECT name, personality
            FROM students
            WHERE id=%s
        """, (student_id,))

        student = cur.fetchone()

        cur.close()
        conn.close()

        if not student:
            return {"error": "not found"}, 404

        name = student[0]
        personality = student[1]

    # LOCAL MODE
    else:

        student = next(
            (s for s in students_local if s["id"] == student_id),
            None
        )

        if not student:
            return {"error": "not found"}, 404

        name = student["name"]
        personality = student["personality"]

    # NO AI KEY
    if not OPENAI_API_KEY:

        return {
            "reply": f"{name}: lol im running without ai key rn"
        }

    prompt = f"""
You are a student named {name}.

Personality:
{personality}

Rules:
- casual replies
- short messages
- no AI mention
- act like teenager
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
                {
                    "role": "system",
                    "content": prompt
                },

                {
                    "role": "user",
                    "content": message
                }
            ]
        }
    )

    try:
        reply = response.json()["choices"][0]["message"]["content"]

    except:
        reply = "AI error"

    return {"reply": reply}

# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)