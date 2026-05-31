from flask import Flask, jsonify, request, render_template
import psycopg2
import os
import requests

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = "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"
# -----------------------
# LOCAL DATA
# -----------------------
students_data = [

    {
        "id": 1,
        "name": "Daniel",
        "surname": "Barta",
        "age": 20,
        "personality": "Funny sarcastic chill guy"
    },

    {
        "id": 2,
        "name": "Matúš",
        "surname": "Bucko",
        "age": 22,
        "personality": "Smart quiet logical"
    },

    {
        "id": 3,
        "name": "Adrian",
        "surname": "Červenka",
        "age": 21,
        "personality": "Energetic talkative"
    },

    {
        "id": 4,
        "name": "Martin",
        "surname": "Deglovič",
        "age": 23,
        "personality": "Calm slightly lazy"
    },

    {
        "id": 5,
        "name": "Samuel",
        "surname": "Haring",
        "age": 20,
        "personality": "Competitive gamer"
    },

    {
        "id": 6,
        "name": "Matúš",
        "surname": "Holečka",
        "age": 20,
        "personality": "Helpful friendly"
    },

    {
        "id": 7,
        "name": "Martin",
        "surname": "Jelínek",
        "age": 22,
        "personality": "Sporty active"
    },

    {
        "id": 8,
        "name": "Tomáš",
        "surname": "Jurčák",
        "age": 21,
        "personality": "Meme lover funny"
    },

    {
        "id": 9,
        "name": "Milan",
        "surname": "Kokina",
        "age": 23,
        "personality": "Serious focused"
    },

    {
        "id": 10,
        "name": "Patrik",
        "surname": "Korba",
        "age": 20,
        "personality": "Chill relaxed"
    },

    {
        "id": 11,
        "name": "Marcus",
        "surname": "Martiš",
        "age": 22,
        "personality": "Confident leader type"
    },

    {
        "id": 12,
        "name": "Samuel",
        "surname": "Martiš",
        "age": 20,
        "personality": "Quiet smart"
    },

    {
        "id": 13,
        "name": "Marko",
        "surname": "Mihalička",
        "age": 21,
        "personality": "Chaotic funny"
    },

    {
        "id": 14,
        "name": "Rastislav",
        "surname": "Paták",
        "age": 22,
        "personality": "Logical thinker"
    },

    {
        "id": 15,
        "name": "Matej",
        "surname": "Randziak",
        "age": 22,
        "personality": "Supportive friendly"
    },

    {
        "id": 16,
        "name": "Dávid",
        "surname": "Škula",
        "age": 20,
        "personality": "Gaming addicted"
    },

    {
        "id": 17,
        "name": "Samuel",
        "surname": "Uhrík",
        "age": 21,
        "personality": "Sarcastic witty"
    },

    {
        "id": 18,
        "name": "Janka",
        "surname": "Vargová",
        "age": 21,
        "personality": "Kind caring"
    },

    {
        "id": 19,
        "name": "Lukáš",
        "surname": "Vindiš",
        "age": 22,
        "personality": "Sporty competitive"
    }
]

# -----------------------
# CUSTOM SORT
# -----------------------
def custom_sort(data, mode):

    arr = data[:]

    n = len(arr)

    for i in range(n):

        for j in range(0, n - i - 1):

            a = arr[j]
            b = arr[j + 1]

            swap = False

            # NAME A-Z
            if mode == "name":

                if a["name"].lower() > b["name"].lower():
                    swap = True

            # YOUNGEST FIRST
            elif mode == "youngest":

                if a["age"] > b["age"]:
                    swap = True

            # OLDEST FIRST
            elif mode == "oldest":

                if a["age"] < b["age"]:
                    swap = True

            if swap:

                arr[j], arr[j + 1] = arr[j + 1], arr[j]

    return arr

# -----------------------
# DB
# -----------------------
def get_db():

    if not DATABASE_URL:
        return None

    return psycopg2.connect(DATABASE_URL)

# -----------------------
# HOME
# -----------------------
@app.route("/")
def home():

    return render_template("index.html")

# -----------------------
# GET STUDENTS
# -----------------------
@app.route("/api/students")
def get_students():

    sort_mode = request.args.get("sort", "name")

    conn = get_db()

    if not conn:

        sorted_students = custom_sort(
            students_data,
            sort_mode
        )

        return jsonify(sorted_students)

    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, surname, age, personality
        FROM students
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    students = [

        {
            "id": r[0],
            "name": r[1],
            "surname": r[2],
            "age": r[3],
            "personality": r[4]
        }

        for r in rows
    ]

    students = custom_sort(students, sort_mode)

    return jsonify(students)

# -----------------------
# ADD STUDENT
# -----------------------
@app.route("/api/students", methods=["POST"])
def add_student():

    data = request.json

    conn = get_db()

    if not conn:

        new_id = len(students_data) + 1

        students_data.append({

            "id": new_id,

            "name": data["name"],

            "surname": data["surname"],

            "age": int(data["age"]),

            "personality": data["personality"]
        })

        return {"status": "added"}

    cur = conn.cursor()

    cur.execute("""

        INSERT INTO students
        (name, surname, age, personality)

        VALUES (%s, %s, %s, %s)

    """, (

        data["name"],
        data["surname"],
        int(data["age"]),
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

    if not conn:

        for s in students_data:

            if s["id"] == student_id:

                s["name"] = data["name"]
                s["surname"] = data["surname"]
                s["age"] = int(data["age"])
                s["personality"] = data["personality"]

        return {"status": "edited"}

    cur = conn.cursor()

    cur.execute("""

        UPDATE students

        SET
            name=%s,
            surname=%s,
            age=%s,
            personality=%s

        WHERE id=%s

    """, (

        data["name"],
        data["surname"],
        int(data["age"]),
        data["personality"],
        student_id

    ))

    conn.commit()

    cur.close()
    conn.close()

    return {"status": "edited"}

# -----------------------
# CHAT
# -----------------------
@app.route("/api/chat/<int:student_id>", methods=["POST"])
def chat(student_id):

    data = request.get_json()

    if not data:
        return {
            "reply": "No message received."
        }

    message = data.get("message", "").strip()

    if not message:
        return {
            "reply": "Empty message."
        }

    conn = get_db()

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
            return {
                "reply": "Student not found."
            }, 404

        name = student[0]
        personality = student[1]

    else:

        student = next(
            (s for s in students_data if s["id"] == student_id),
            None
        )

        if not student:
            return {
                "reply": "Student not found."
            }, 404

        name = student["name"]
        personality = student["personality"]

    prompt = f"""
You are a student named {name}.

Personality:
{personality}

Rules:
- casual replies
- short messages
- act like a teenager
- text naturally
- never mention AI
- stay in character
"""

    try:

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",

            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },

            json={
                "model": "llama-3.1-8b-instant",

                "messages": [
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],

                "temperature": 0.8,
                "max_tokens": 100
            },

            timeout=30
        )

        result = response.json()

        print(result)

        if "choices" not in result:
            return {
                "reply": "AI error"
            }

        reply = result["choices"][0]["message"]["content"]

        return {
            "reply": reply
        }

    except Exception as e:

        print("CHAT ERROR:", e)

        return {
            "reply": "AI error"
        }

# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":

    app.run(debug=True)

