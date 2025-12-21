// src/pages/Register.jsx
import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import { registerUser } from "../services/api"; // ✅ ADD THIS
import "./auth-page.css";

export default function Register() {
  const navigate = useNavigate();
  const location = useLocation();

  const role = location.state?.role || "USER"; // CUSTOMER → USER

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    crewRole: "",
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleRegister = async () => {
    try {
      const payload = {
        name: form.name,
        email: form.email,
        password: form.password,
        role: role,
      };

      // optional: crew role logic (future use)
      if (role === "CREW" && form.crewRole) {
        payload.role = form.crewRole;
      }

      await registerUser(payload);

      alert("Registration successful! Please login.");
      navigate("/login");

    } catch (err) {
      console.error("Registration error:", err);
      alert(
        err.message ||
        "Registration failed. Please try again."
      );
    }
  };

  return (
    <div className="register-page">
      <div className="register-card">

        <h2 className="register-title">Create your account</h2>
        <p className="register-subtitle">
          Join AeroNova to book flights seamlessly
        </p>

        <div className="register-form">
          <label>
            Full Name
            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Your name"
            />
          </label>

          <label>
            Email
            <input
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              placeholder="you@example.com"
            />
          </label>

          <label>
            Password
            <input
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Create a password"
            />
          </label>

          {role === "CREW" && (
            <label>
              Crew Role
              <select
                name="crewRole"
                value={form.crewRole}
                onChange={handleChange}
              >
                <option value="">Select role</option>
                <option value="PILOT">Pilot</option>
                <option value="CABIN_CREW">Cabin Crew</option>
                <option value="GROUND_STAFF">Ground Staff</option>
                <option value="ADMIN">Admin</option>
              </select>
            </label>
          )}

          <button className="register-btn" onClick={handleRegister}>
            Register
          </button>
        </div>

        <div className="register-footer">
          Already have an account?{" "}
          <span onClick={() => navigate("/login")}>
            Login
          </span>
        </div>

      </div>
    </div>
  );
}
