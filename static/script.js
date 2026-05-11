// static/script.js

let current = null;

// -----------------------
// LOAD STUDENTS
// -----------------------
function loadStudents() {

    fetch("/api/students")
    .then(r => r.json())

    .then(data => {

        const container =
            document.getElementById("students");

        container.innerHTML = "";

        data.forEach(s => {

            const div =
                document.createElement("div");

            div.className = "student";

            div.innerHTML = `
                <img src="https://api.dicebear.com/7.x/bottts/svg?seed=${s.name}">

                <div class="studentInfo">

                    <span>
                        ${s.name} ${s.surname}
                    </span>

                    <button onclick="editStudent(${s.id}, '${s.name}', '${s.surname}')">
                        ✏️
                    </button>

                </div>
            `;

            div.onclick = () => {
                current = s;
                openChat(s);
            };

            container.appendChild(div);

        });

    });

}

loadStudents();

// -----------------------
// OPEN CHAT
// -----------------------
function openChat(student) {

    document.getElementById("chatName").innerText =
        `${student.name} ${student.surname}`;

    document.getElementById("messages").innerHTML = "";

    document.getElementById("chatModal")
        .classList.remove("hidden");
}

// -----------------------
// CLOSE CHAT
// -----------------------
function closeChat() {

    document.getElementById("chatModal")
        .classList.add("hidden");
}

// -----------------------
// SEND MESSAGE
// -----------------------
function send() {

    const msg =
        document.getElementById("msg").value;

    if (!current || !msg)
        return;

    const messages =
        document.getElementById("messages");

    messages.innerHTML += `
        <div class="myMessage">
            ${msg}
        </div>
    `;

    document.getElementById("msg").value = "";

    fetch(`/api/chat/${current.id}`, {

        method: "POST",

        headers: {
            "Content-Type":"application/json"
        },

        body: JSON.stringify({
            message: msg
        })

    })

    .then(r => r.json())

    .then(d => {

        messages.innerHTML += `
            <div class="aiMessage">
                ${d.reply}
            </div>
        `;

        messages.scrollTop =
            messages.scrollHeight;

    });

}

// -----------------------
// DARK MODE
// -----------------------
function toggleTheme() {

    document.body.classList.toggle("dark");

}

// -----------------------
// ADD STUDENT
// -----------------------
function addStudent() {

    const name =
        document.getElementById("newName").value;

    const surname =
        document.getElementById("newSurname").value;

    const personality =
        document.getElementById("newPersonality").value;

    fetch("/api/students", {

        method: "POST",

        headers: {
            "Content-Type":"application/json"
        },

        body: JSON.stringify({
            name,
            surname,
            personality
        })

    })

    .then(r => r.json())

    .then(() => {

        loadStudents();

        document.getElementById("newName").value = "";
        document.getElementById("newSurname").value = "";
        document.getElementById("newPersonality").value = "";

    });

}

// -----------------------
// EDIT STUDENT
// -----------------------
function editStudent(id, oldName, oldSurname) {

    event.stopPropagation();

    const name =
        prompt("New name:", oldName);

    const surname =
        prompt("New surname:", oldSurname);

    const personality =
        prompt("New personality:");

    if (!name || !surname)
        return;

    fetch(`/api/students/${id}`, {

        method: "PUT",

        headers: {
            "Content-Type":"application/json"
        },

        body: JSON.stringify({
            name,
            surname,
            personality
        })

    })

    .then(r => r.json())

    .then(() => {

        loadStudents();

    });

}