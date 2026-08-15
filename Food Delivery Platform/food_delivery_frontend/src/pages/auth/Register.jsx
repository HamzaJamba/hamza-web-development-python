import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import AnimatedBackground from "../../components/AnimatedBackground";

const ROLES = [
  { value: "CUSTOMER", label: "Customer", icon: "ti-user" },
  { value: "RESTAURANT_OWNER", label: "Restaurant", icon: "ti-tools-kitchen-2" },
  { value: "RIDER", label: "Rider", icon: "ti-motorbike" },
];

export default function Register() {
  const { register, loading, error } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "", email: "", password: "", password2: "", role: "CUSTOMER", phone_number: "",
  });
  const [done, setDone] = useState(false);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await register(form);
      setDone(true);
    } catch {
      // error shown via context
    }
  };

  if (done) {
    const needsApproval = form.role !== "CUSTOMER";
    return (
      <div className="page-auth" style={{ display: "flex", flexDirection: "column", justifyContent: "center", padding: "0 24px", textAlign: "center", minHeight: "100vh" }}>
        <i className="ti ti-circle-check" style={{ fontSize: 40, color: "var(--gold)", marginBottom: 12 }} />
        <h2 style={{ fontSize: 18, marginBottom: 8 }}>Account created</h2>
        <p style={{ color: "var(--text-muted)", fontSize: 13, marginBottom: 24 }}>
          {needsApproval
            ? "An admin needs to approve your account before you can log in. We'll be quick."
            : "You're all set. Log in to start ordering."}
        </p>
        <Link to="/login" className="btn btn-primary">Go to login</Link>
      </div>
    );
  }

  return (
    <div className="page-auth" style={{ padding: "40px 24px", position: "relative", minHeight: "100vh" }}>
      <AnimatedBackground particleCount={12} />
      <div className="fade-in-up" style={{ position: "relative", zIndex: 1 }}>
      <h2 style={{ fontSize: 20, marginBottom: 4 }}>Create account</h2>
      <p style={{ color: "var(--text-muted)", fontSize: 13, marginBottom: 24 }}>Join bhookh.pk in a few seconds</p>

      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        {ROLES.map((r) => (
          <button
            key={r.value}
            type="button"
            onClick={() => setForm({ ...form, role: r.value })}
            className="card"
            style={{
              flex: 1,
              textAlign: "center",
              padding: "12px 6px",
              border: form.role === r.value ? "1px solid var(--gold)" : "1px solid transparent",
              background: form.role === r.value ? "var(--surface-raised)" : "var(--surface)",
            }}
          >
            <i className={`ti ${r.icon}`} style={{ fontSize: 20, color: form.role === r.value ? "var(--gold)" : "var(--text-muted)" }} />
            <div style={{ fontSize: 11, marginTop: 6, color: form.role === r.value ? "var(--text)" : "var(--text-muted)" }}>{r.label}</div>
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="username">Username</label>
          <input id="username" value={form.username} onChange={set("username")} required />
        </div>
        <div className="field">
          <label htmlFor="email">Email</label>
          <input id="email" type="email" value={form.email} onChange={set("email")} required />
        </div>
        <div className="field">
          <label htmlFor="phone">Phone number</label>
          <input id="phone" value={form.phone_number} onChange={set("phone_number")} placeholder="03xxxxxxxxx" />
        </div>
        <div className="field">
          <label htmlFor="password">Password</label>
          <input id="password" type="password" value={form.password} onChange={set("password")} required />
        </div>
        <div className="field">
          <label htmlFor="password2">Confirm password</label>
          <input id="password2" type="password" value={form.password2} onChange={set("password2")} required />
        </div>

        {error && <p className="field-error" style={{ marginBottom: 16 }}>{error}</p>}

        <button className="btn btn-primary btn-block" disabled={loading} type="submit">
          {loading ? <span className="spinner" /> : "Create account"}
        </button>
      </form>

      <div style={{ textAlign: "center", marginTop: 16, fontSize: 13, color: "var(--text-muted)" }}>
        Already have an account? <Link to="/login" style={{ color: "var(--gold)", fontWeight: 600 }}>Log in</Link>
      </div>
      </div>
    </div>
  );
}
