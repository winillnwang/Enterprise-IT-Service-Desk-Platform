async function refreshLayoutAccessToken() {
  const refreshToken = localStorage.getItem("refresh_token");

  if (!refreshToken) {
    return null;
  }

  const response = await fetch("/api/auth/refresh/", {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      refresh: refreshToken,
    }),
  });

  if (!response.ok) {
    localStorage.removeItem("access_token");

    localStorage.removeItem("refresh_token");

    return null;
  }

  const data = await response.json();

  localStorage.setItem("access_token", data.access);

  return data.access;
}

async function layoutApiFetch(url) {
  let accessToken = localStorage.getItem("access_token");

  if (!accessToken) {
    window.location.href = "/login/";

    return null;
  }

  let response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (response.status === 401) {
    accessToken = await refreshLayoutAccessToken();

    if (!accessToken) {
      window.location.href = "/login/";

      return null;
    }

    response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  }

  return response;
}

function getRoleLabel(role) {
  const labels = {
    employee: "一般員工",

    it_engineer: "IT 工程師",

    it_manager: "IT 管理者",

    admin: "系統管理員",
  };

  return labels[role] || role;
}

function showRoleNavigation(user) {
  const itRoles = ["it_engineer", "it_manager", "admin"];

  const managerRoles = ["it_manager", "admin"];

  document.querySelectorAll("[data-it-only]").forEach((element) => {
    element.style.display = itRoles.includes(user.role) ? "" : "none";
  });

  document.querySelectorAll("[data-manager-only]").forEach((element) => {
    element.style.display = managerRoles.includes(user.role) ? "" : "none";
  });
}

async function loadLayoutUser() {
  const response = await layoutApiFetch("/api/auth/me/");

  if (!response || !response.ok) {
    window.location.href = "/login/";

    return null;
  }

  const user = await response.json();

  const roleLabel = getRoleLabel(user.role);

  const sidebarUser = document.getElementById("sidebar-user");

  if (sidebarUser) {
    sidebarUser.textContent = `${user.username}｜${roleLabel}`;
  }

  const topbarUser = document.getElementById("topbar-user");

  if (topbarUser) {
    topbarUser.textContent = `${user.username}｜${roleLabel}`;
  }

  showRoleNavigation(user);

  return user;
}

function logout() {
  localStorage.removeItem("access_token");

  localStorage.removeItem("refresh_token");

  window.location.href = "/login/";
}

const logoutButton = document.getElementById("sidebar-logout");

if (logoutButton) {
  logoutButton.addEventListener("click", logout);
}

const mobileMenuButton = document.getElementById("mobile-menu");

if (mobileMenuButton) {
  mobileMenuButton.addEventListener("click", function () {
    document.body.classList.toggle("sidebar-open");
  });
}

document.addEventListener("DOMContentLoaded", loadLayoutUser);
