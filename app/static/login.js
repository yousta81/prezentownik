const form = document.getElementById("loginForm");
const emailInput = document.getElementById("email"); // Assuming an id="email"
const passwordInput = document.getElementById("password"); // Assuming an id="password"
const message = document.getElementById("message");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

    const response = await fetch("/login", {
        method: "POST",
        body: formData  // <-- BEZ JSON, BEZ HEADERS
    });

    if (!response.ok) {
        message.innerHTML = "Błędny email lub hasło";
        return;
    }

    window.location.href = "/";
});