let current = null;

fetch("/api/students")
.then(r => r.json())
.then(data => {
    const list = document.getElementById("list");

    data.forEach(s => {
        const li = document.createElement("li");
        li.innerText = s.name + " " + s.surname;

        li.onclick = () => {
            current = s;
            document.getElementById("chatTitle").innerText = s.name;
        };

        list.appendChild(li);
    });
});

function send() {
    const msg = document.getElementById("msg").value;

    fetch(`/api/chat/${current.id}`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({message: msg})
    })
    .then(r => r.json())
    .then(d => {
        document.getElementById("messages").innerHTML +=
        `<div><b>${current.name}:</b> ${d.reply}</div>`;
    });
}

function addStudent() {
    fetch("/api/students", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            name: name.value,
            surname: surname.value,
            personality: personality.value
        })
    }).then(() => location.reload());
}

function toggleTheme() {
    document.body.classList.toggle("dark");
}