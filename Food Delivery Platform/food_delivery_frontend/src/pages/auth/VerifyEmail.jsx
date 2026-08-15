import { useState } from "react";
import { Link } from "react-router-dom";
import { confirmEmailVerification } from "../../api/services";

export default function VerifyEmail() {
  const [form, setForm] = useState({ uid: "", token: "" });
  const [status, setStatus] = useState("idle"); // idle | loading | done | error
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setStatus("loading");
    setError("");
    try {
      await confirmEmailVerification(form);
      setStatus("done");
    } catch (err) {
      setError(err.response?.data?.detail || "Invalid or expired verification link.");
      setStatus("error");
    }
  };

  if (status === "done") {
    return (
      <div className="page-auth" style={{ display: "flex", flexDirection: "column", justifyContent: "center", padding: "0 24px", textAlign: "center", minHeight: "100vh" }}>
        <i className="ti ti-circle-check" style={{ fontSize: 40, color: "var(--gold)", marginBottom: 12 }} />
        <h2 style={{ fontSize: 18, marginBottom: 8 }}>Email verified</h2>
        <p style={{ color: "var(--text-muted)", fontSize: 13, marginBottom: 24 }}>Your email has been confirmed.</p>
        <Link to="/profile" className="btn btn-primary">Back to profile</Link>
      </div>
    );
  }

  return (
    <div className="page-auth" style={{ padding: "40px 24px" }}>
      <h2 style={{ fontSize: 20, marginBottom: 4 }}>Verify your email</h2>
      <p style={{ color: "var(--text-muted)", fontSize: 13, marginBottom: 24 }}>
        Paste the uid and token from your verification email.
      </p>
      <form onSubmit={submit}>
        <div className="field">
          <label htmlFor="uid">Uid</label>
          <input id="uid" value={form.uid} onChange={(e) => setForm({ ...form, uid: e.target.value })} required />
        </div>
        <div className="field">
          <label htmlFor="token">Token</label>
          <input id="token" value={form.token} onChange={(e) => setForm({ ...form, token: e.target.value })} required />
        </div>
        {error && <p className="field-error" style={{ marginBottom: 16 }}>{error}</p>}
        <button className="btn btn-primary btn-block" disabled={status === "loading"} type="submit">
          {status === "loading" ? <span className="spinner" /> : "Verify email"}
        </button>
      </form>
    </div>
  );
}
