import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import AnimatedBackground from "../../components/AnimatedBackground";

const ROLE_HOME = {
  ADMIN: "/admin",
  RESTAURANT_OWNER: "/restaurant",
  RIDER: "/rider",
  CUSTOMER: "/",
};

export default function Login() {
  const { login, loading, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ username: "", password: "" });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const user = await login(form.username, form.password);
      const from = location.state?.from;
      navigate(from || ROLE_HOME[user.role] || "/", { replace: true });
    } catch {
      // error shown via context
    }
  };

  return (
    <div className="page-auth" style={{ display: "flex", flexDirection: "column", justifyContent: "center", padding: "0 24px", minHeight: "100vh", position: "relative" }}>
      <AnimatedBackground />
      <div className="fade-in-up" style={{ position: "relative", zIndex: 1 }}>
      <div style={{ textAlign: "center", marginBottom: 36 }}>
        <div style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 28, color: "var(--gold)" }}>
          bhookh<span style={{ color: "var(--text)" }}>.pk</span>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: 13, marginTop: 6 }}>Apna khana, apne shehar se</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="username">Username</label>
          <input
            id="username"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            placeholder="your_username"
            required
          />
        </div>
        <div className="field">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            placeholder="••••••••"
            required
          />
        </div>

        {error && <p className="field-error" style={{ marginBottom: 16 }}>{error}</p>}

        <button className="btn btn-primary btn-block glow-accent" disabled={loading} type="submit">
          {loading ? <span className="spinner" /> : "Log in"}
        </button>
      </form>

      <div style={{ textAlign: "center", marginTop: 20, fontSize: 13, color: "var(--text-muted)" }}>
        <Link to="/forgot-password" style={{ color: "var(--gold)" }}>Forgot password?</Link>
      </div>
      <div style={{ textAlign: "center", marginTop: 12, fontSize: 13, color: "var(--text-muted)" }}>
        New here? <Link to="/register" style={{ color: "var(--gold)", fontWeight: 600 }}>Create account</Link>
      </div>
      </div>
    </div>
  );
}
