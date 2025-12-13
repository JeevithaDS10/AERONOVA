// src/services/api.js
const API_BASE_URL = "http://127.0.0.1:9000";

function getAuthHeaders() {
  const token = localStorage.getItem("airnova_token");
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

// frontend/src/services/api.js
export async function registerUser(body) {
  const res = await fetch("http://127.0.0.1:9000/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.message || data?.error || JSON.stringify(data) || "Registration failed");
  }
  return data;
}


export async function loginUser(data) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  let body = {};
  try { body = await response.json(); } catch { body = {}; }

  if (!response.ok) {
    const msg = body.detail || "Login request failed";
    throw new Error(msg);
  }

  // normalize common shapes
  const token = body.access_token || body.token || body.data?.token || null;
  const user = body.user || body.data?.user || null;

  return { access_token: token, user: user ?? body, raw: body };
}

/* add other API functions (searchFlights, etc.) below, keep file JS only */