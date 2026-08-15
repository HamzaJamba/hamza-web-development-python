import { useState } from "react";
import { Link } from "react-router-dom";
import { requestPasswordReset, confirmPasswordReset } from "../../api/auth";

export default function ForgotPassword() {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState("");
  const [form, setForm] = useState({ uid: "", token: "", new_password: "" });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const requestReset = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await requestPasswordReset(email);
      setMessage(data.detail);
      setStep(2);
    } catch {
      setError("Something went wrong. Try again.");
    } finally {
      setLoading(false);
    }
  };

  const confirmReset = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await confirmPasswordReset(form);
      setStep(3);
    } catch (err) {
      setError(err.response?.data?.detail || "Reset link is invalid or expired.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-auth" style={{ padding: "40px 24px" }}>
      <h2 style={{ fontSize: 20, marginBottom: 4 }}>Reset password</h2>
      <p style={{ color: "var(--text-muted)", fontSize: 13, marginBottom: 24 }}>
        {step === 1 && "Enter your email and we'll send you a reset code."}
        {step === 2 && "Check your email for the uid and token, then enter them below."}
        {step === 3 && "Your password has been reset."}
      </p>

      {step === 1 && (
        <form onSubmit={requestReset}>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          {error && <p className="field-error" style={{ marginBottom: 16 }}>{error}</p>}
          <button className="btn btn-primary btn-block" disabled={loading} type="submit">
            {loading ? <span className="spinner" /> : "Send reset code"}
          </button>
        </form>
      )}

      {step === 2 && (
        <form onSubmit={confirmReset}>
          {message && <p style={{ fontSize: 12, color: "var(--gold)", marginBottom: 16 }}>{message}</p>}
          <div className="field">
            <label htmlFor="uid">Uid</label>
            <input id="uid" value={form.uid} onChange={(e) => setForm({ ...form, uid: e.target.value })} required />
          </div>
          <div className="field">
            <label htmlFor="token">Token</label>
            <input id="token" value={form.token} onChange={(e) => setForm({ ...form, token: e.target.value })} required />
          </div>
          <div className="field">
            <label htmlFor="new_password">New password</label>
            <input
              id="new_password"
              type="password"
              value={form.new_password}
              onChange={(e) => setForm({ ...form, new_password: e.target.value })}
              required
            />
          </div>
          {error && <p className="field-error" style={{ marginBottom: 16 }}>{error}</p>}
          <button className="btn btn-primary btn-block" disabled={loading} type="submit">
            {loading ? <span className="spinner" /> : "Reset password"}
          </button>
        </form>
      )}

      {step === 3 && (
        <Link to="/login" className="btn btn-primary btn-block" style={{ textAlign: "center" }}>
          Go to login
        </Link>
      )}
    </div>
  );
}
