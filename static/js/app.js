/* ============================================
   SSC-MS — Core Application Logic
   Auth · API · Modals · Toasts · Navigation
   ============================================ */

// ─── AUTH HELPERS ─────────────────────────────────
function getToken() {
  return localStorage.getItem("accessToken");
}

function setTokens(access, refresh) {
  localStorage.setItem("accessToken", access);
  if (refresh) localStorage.setItem("refreshToken", refresh);
}

function clearTokens() {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  localStorage.removeItem("userName");
  localStorage.removeItem("userRole");
}

function isLoggedIn() {
  return !!getToken();
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: "Bearer " + getToken(),
  };
}

// ─── API FETCH WRAPPER ──────────────────────────
async function apiFetch(url, options = {}) {
  const defaults = { headers: authHeaders() };
  const config = {
    ...defaults,
    ...options,
    headers: { ...defaults.headers, ...(options.headers || {}) },
  };
  const response = await fetch(url, config);
  if (response.status === 401) {
    // Try to refresh token
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      config.headers["Authorization"] = "Bearer " + getToken();
      return fetch(url, config);
    } else {
      clearTokens();
      window.location.href = "/";
      throw new Error("Session expired");
    }
  }
  return response;
}

async function tryRefreshToken() {
  const refresh = localStorage.getItem("refreshToken");
  if (!refresh) return false;
  try {
    const r = await fetch("/api/token/refresh/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (r.ok) {
      const data = await r.json();
      localStorage.setItem("accessToken", data.access);
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

// ─── LOGIN ──────────────────────────────────────
async function doLogin() {
  const u = document.getElementById("login-username");
  const p = document.getElementById("login-password");
  const errBox = document.getElementById("login-error");
  if (!u || !p) return;

  const username = u.value.trim();
  const password = p.value.trim();

  if (errBox) errBox.classList.remove("show");
  if (!username || !password) {
    if (errBox) {
      errBox.textContent = "Please enter both username and password.";
      errBox.classList.add("show");
    }
    return;
  }

  try {
    const res = await fetch("/api/login/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (res.ok) {
      const data = await res.json();
      setTokens(data.access, data.refresh);
      localStorage.setItem("userName", username);
      // Decode JWT to extract role
      try {
        const payload = JSON.parse(atob(data.access.split(".")[1]));
        if (payload.role) localStorage.setItem("userRole", payload.role);
      } catch (e) {
        // JWT parsing failed, will get role from API later
      }
      window.location.href = "/";
    } else {
      if (errBox) {
        errBox.textContent = "Invalid credentials. Please try again.";
        errBox.classList.add("show");
      }
    }
  } catch (err) {
    if (errBox) {
      errBox.textContent = "Network error. Please try again.";
      errBox.classList.add("show");
    }
  }
}

function doLogout() {
  clearTokens();
  window.location.href = "/";
}

// ─── TOAST NOTIFICATIONS ────────────────────────
function showToast(message, type = "success", title = null) {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const icons = { success: "✅", error: "❌", info: "ℹ️" };
  const titles = { success: "Success", error: "Error", info: "Info" };

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || "📌"}</span>
    <div class="toast-message">
      <strong>${title || titles[type] || "Notice"}</strong>
      ${message}
    </div>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 4000);
}

// ─── MODAL MANAGEMENT ───────────────────────────
function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.add("show");
    document.body.style.overflow = "hidden";
  }
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.remove("show");
    document.body.style.overflow = "";
    // Reset form inside
    const form = modal.querySelector("form");
    if (form) form.reset();
  }
}

// Close modal on overlay click
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal-overlay")) {
    e.target.classList.remove("show");
    document.body.style.overflow = "";
  }
});

// Close modal on Escape
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    document.querySelectorAll(".modal-overlay.show").forEach((m) => {
      m.classList.remove("show");
      document.body.style.overflow = "";
    });
  }
});

// ─── FORM SUBMISSION ────────────────────────────
async function submitForm(event, endpoint, modalId) {
  event.preventDefault();
  const form = event.target;
  const data = Object.fromEntries(new FormData(form).entries());

  // Default to STAFF role for user creation
  if (endpoint === "accounts/register") {
    data["role"] = "STAFF";
  }

  try {
    const res = await apiFetch("/api/" + endpoint + "/", {
      method: "POST",
      body: JSON.stringify(data),
    });

    if (res.ok) {
      closeModal(modalId);
      const actionMap = {
        energy: "Energy record added",
        water: "Water record added",
        waste: "Waste record added",
        "accounts/register": "Staff user created",
      };
      showToast(actionMap[endpoint] || "Action completed!", "success");
      // Refresh dashboard if we're on the dashboard
      if (typeof loadDashboardData === "function") {
        loadDashboardData();
      }
      // Refresh data table if we're on a records page
      if (typeof loadRecordsData === "function") {
        loadRecordsData();
      }
    } else {
      const errData = await res.json().catch(() => null);
      let msg = "Please check your input and permissions.";
      if (errData) {
        if (errData.detail) msg = errData.detail;
        else if (typeof errData === "object") {
          const firstKey = Object.keys(errData)[0];
          if (firstKey) {
            const val = errData[firstKey];
            msg = Array.isArray(val) ? val[0] : val;
          }
        }
      }
      showToast(msg, "error");
    }
  } catch (err) {
    showToast("Network error. Please try again.", "error");
  }
}

// ─── SIDEBAR TOGGLE ─────────────────────────────
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  if (sidebar) sidebar.classList.toggle("open");
  if (overlay) overlay.classList.toggle("show");
}

// ─── REFRESH PAGE ───────────────────────────────
function refreshPage() {
  if (typeof loadDashboardData === "function") loadDashboardData();
  else if (typeof loadRecordsData === "function") loadRecordsData();
  else location.reload();
}

// ─── EXPORT CSV ─────────────────────────────────
async function exportCSV(endpoint) {
  try {
    const monthFilter = document.getElementById("month-filter")?.value || "";
    let url = `/api/${endpoint}/export_csv/`;
    if (monthFilter) url += `?month_filter=${monthFilter}`;

    // We fetch with auth because the API requires IsAuthenticated for these methods
    const res = await apiFetch(url);
    if (!res.ok) throw new Error("Export failed");

    const blob = await res.blob();
    const windowUrl = window.URL || window.webkitURL;
    const downloadUrl = windowUrl.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = `${endpoint}_export_${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    windowUrl.revokeObjectURL(downloadUrl);

    showToast(
      `${endpoint.charAt(0).toUpperCase() + endpoint.slice(1)} records exported successfully!`,
      "success",
    );
  } catch (e) {
    showToast("Failed to export data.", "error");
  }
}

// ─── PAGE INIT ──────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  // Hide loader
  const loader = document.getElementById("page-loader");

  // Check login status
  if (isLoggedIn()) {
    // Show logout button
    const logoutBtn = document.getElementById("btn-logout");
    if (logoutBtn) logoutBtn.style.display = "flex";

    // Update user info in sidebar
    const name = localStorage.getItem("userName") || "User";
    const role = localStorage.getItem("userRole") || "STAFF";
    const avatar = document.getElementById("user-avatar");
    const displayName = document.getElementById("user-display-name");
    const roleDisplay = document.getElementById("user-role");
    if (avatar) avatar.textContent = name.charAt(0).toUpperCase();
    if (displayName) displayName.textContent = name;
    if (roleDisplay) roleDisplay.textContent = role;

    // If we're on a page that requires login, continue
    // (handled per page)
  }

  // Hide loader after 300ms
  setTimeout(() => {
    if (loader) loader.classList.add("hidden");
  }, 300);
});

// ─── ANIMATED COUNTER ───────────────────────────
function animateCounter(element, target, decimals = 1, duration = 1200) {
  const start = 0;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = start + (target - start) * eased;
    element.textContent = current.toFixed(decimals);
    if (progress < 1) requestAnimationFrame(update);
  }

  requestAnimationFrame(update);
}

// ─── DELETE RECORD ──────────────────────────────
async function deleteRecord(endpoint, id) {
  if (!confirm("Are you sure you want to delete this record?")) return;

  try {
    const res = await apiFetch(`/api/${endpoint}/${id}/`, {
      method: "DELETE",
    });
    if (res.ok || res.status === 204) {
      showToast("Record deleted successfully.", "success");
      if (typeof loadRecordsData === "function") loadRecordsData();
      if (typeof loadDashboardData === "function") loadDashboardData();
    } else {
      const errData = await res.json().catch(() => null);
      showToast(
        errData?.detail || "Could not delete. Check permissions.",
        "error",
      );
    }
  } catch {
    showToast("Network error.", "error");
  }
}
