const API = "http://localhost:8000";

function showToast(msg, type = "success") {
    const t = document.getElementById("toast");
    t.textContent = msg;
    t.className = `toast ${type}`;
    clearTimeout(t._timer);
    t._timer = setTimeout(() => { t.className = "toast hidden"; }, 4000);
}

function showLoader(msg = "Processing…") {
    document.getElementById("loader").classList.remove("hidden");
    document.getElementById("loader-msg").textContent = msg;
}
function hideLoader() {
    document.getElementById("loader").classList.add("hidden");
}

document.getElementById("show-register").addEventListener("click", (e) => {
    e.preventDefault();
    document.getElementById("login-card").classList.add("hidden");
    document.getElementById("register-card").classList.remove("hidden");
});

document.getElementById("show-login").addEventListener("click", (e) => {
    e.preventDefault();
    document.getElementById("register-card").classList.add("hidden");
    document.getElementById("login-card").classList.remove("hidden");
});

document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    showLoader("Logging in...");
    try {
        const res = await fetch(`${API}/api/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Login failed");

        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("student_id", data.student_id);
        localStorage.setItem("student_name", email.split('@')[0]);
        window.location.href = "index.html";
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        hideLoader();
    }
});

document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("reg-name").value;
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;

    showLoader("Creating account...");
    try {
        const res = await fetch(`${API}/api/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, password })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Registration failed");

        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("student_id", data.student_id);
        localStorage.setItem("student_name", name);
        window.location.href = "index.html";
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        hideLoader();
    }
});
