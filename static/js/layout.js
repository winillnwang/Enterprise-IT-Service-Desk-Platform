(function () {
    async function loadCurrentUser() {
        const token = localStorage.getItem("access_token");
        if (!token) return;
        const response = await fetch("/api/auth/me/", { headers: { Authorization: `Bearer ${token}` } });
        if (!response.ok) return;
        const user = await response.json();
        const label = `${user.username}｜${user.role}`;
        ["sidebar-user", "topbar-user"].forEach((id) => { const node = document.getElementById(id); if (node) node.textContent = label; });
        // 前端只控制選單顯示，真正權限仍由後端 API 驗證。
        if (user.role === "employee") { document.querySelectorAll("[data-it-only], [data-coming-soon]").forEach((node) => node.remove()); }
    }
    function logout() { localStorage.removeItem("access_token"); localStorage.removeItem("refresh_token"); window.location.href = "/login/"; }
    document.addEventListener("DOMContentLoaded", () => {
        loadCurrentUser().catch(() => {});
        document.getElementById("sidebar-logout")?.addEventListener("click", logout);
        document.getElementById("mobile-menu")?.addEventListener("click", () => document.body.classList.toggle("sidebar-open"));
        document.querySelectorAll("[data-coming-soon]").forEach((node) => node.addEventListener("click", (event) => event.preventDefault()));
    });
})();
