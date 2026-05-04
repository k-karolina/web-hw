let current = null;

fetch("/api/students")
.then(r => r.json())
.then(data => {
    const container = document.getElementById("students");

    data.forEach(s => {
        const div = document.createElement("div");
        div.className = "student";

        div.innerHTML = `
            <img src="https://api.dicebear.com/7.x/bottts/svg?seed=${s.name}">
            <span>${s.name} ${s.surname}</span>
        `;

        div.onclick = () => {
            current = s;
            openChat(s);
        };

        container.appendChild(div);
    });
});

function openChat(student) {
    document.getElementById("chatName").innerText =
        student.name + " " + student.surname;

    document.getElementById("chatModal").classList.remove("hidden");
}

function closeChat() {
    document.getElementById("chatModal").classList.add("hidden");
}

function send() {
    const msg = document.getElementById("msg").value;
    if (!current) return;

    fetch(`/api/chat/${current.id}`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({message: msg})
    })
    .then(r => r.json())
    .then(d => {
        document.getElementById("messages").innerHTML +=
        `<div><b>You:</b> ${msg}</div>
         <div><b>${current.name}:</b> ${d.reply}</div>`;
    });
}

function toggleTheme() {
    document.body.classList.toggle("dark");
}