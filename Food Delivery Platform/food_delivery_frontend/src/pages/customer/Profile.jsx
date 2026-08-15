import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import TopBar from "../../components/TopBar";
import BottomNav from "../../components/BottomNav";
import { useAuth } from "../../context/AuthContext";
import { getProfile, updateProfile, listAddresses, deleteAddress } from "../../api/auth";
import { sendEmailVerification } from "../../api/services";

export default function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ phone_number: "" });
  const [verifySent, setVerifySent] = useState(false);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    getProfile().then((p) => { setProfile(p); setForm({ phone_number: p.phone_number || "" }); });
    listAddresses().then((data) => setAddresses(data.results || data));
  }, []);

  const resendVerification = async () => {
    setSending(true);
    try {
      await sendEmailVerification();
      setVerifySent(true);
    } finally {
      setSending(false);
    }
  };

  useEffect(() => {
    getProfile().then((p) => { setProfile(p); setForm({ phone_number: p.phone_number || "" }); });
    listAddresses().then((data) => setAddresses(data.results || data));
  }, []);

  const save = async () => {
    const updated = await updateProfile(form);
    setProfile(updated);
    setEditing(false);
  };

  const removeAddress = async (id) => {
    await deleteAddress(id);
    setAddresses(addresses.filter((a) => a.id !== id));
  };

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  if (!profile) {
    return (
      <div className="page" style={{ display: "flex", justifyContent: "center", padding: 60 }}>
        <span className="spinner" />
      </div>
    );
  }

  return (
    <div className="page">
      <TopBar title="Profile" />

      <div style={{ padding: "0 18px" }}>
        <div className="card" style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 18 }}>
          <div style={{ width: 52, height: 52, borderRadius: "50%", background: "var(--surface-raised)", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 600, color: "var(--gold)" }}>
            {user.username.slice(0, 2).toUpperCase()}
          </div>
          <div>
            <div style={{ fontSize: 15, fontWeight: 600 }}>{profile.username}</div>
            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{profile.email}</div>
          </div>
        </div>

        {!profile.is_email_verified && (
          <div className="card" style={{ marginBottom: 18, border: "1px solid var(--gold)", display: "flex", justifyContent: "space-between", alignItems: "center", gap: 10 }}>
            <div>
              <div style={{ fontSize: 13, fontWeight: 600, color: "var(--gold)" }}>
                <i className="ti ti-mail-exclamation" style={{ fontSize: 14 }} /> Email not verified
              </div>
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                {verifySent ? "Verification link sent — check your email." : "Verify your email to secure your account."}
              </div>
            </div>
            {!verifySent && (
              <button className="btn btn-secondary" style={{ padding: "8px 14px", fontSize: 12, flexShrink: 0 }} disabled={sending} onClick={resendVerification}>
                {sending ? <span className="spinner" /> : "Send link"}
              </button>
            )}
            {verifySent && (
              <Link to="/verify-email" className="btn btn-secondary" style={{ padding: "8px 14px", fontSize: 12, flexShrink: 0 }}>
                Enter code
              </Link>
            )}
          </div>
        )}

        <div className="card" style={{ marginBottom: 18 }}>
          {editing ? (
            <>
              <div className="field">
                <label htmlFor="phone">Phone number</label>
                <input id="phone" value={form.phone_number} onChange={(e) => setForm({ phone_number: e.target.value })} />
              </div>
              <button className="btn btn-primary btn-block" onClick={save}>Save</button>
            </>
          ) : (
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Phone number</div>
                <div style={{ fontSize: 13 }}>{profile.phone_number || "Not set"}</div>
              </div>
              <button className="btn btn-secondary" onClick={() => setEditing(true)}>Edit</button>
            </div>
          )}
        </div>

        <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)", marginBottom: 10 }}>SAVED ADDRESSES</div>
        {addresses.map((a) => (
          <div key={a.id} className="card" style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
            <div>
              <div style={{ fontSize: 13, fontWeight: 600 }}>{a.label || "Address"}</div>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{a.address_line}, {a.city}</div>
            </div>
            <button onClick={() => removeAddress(a.id)} aria-label="Delete address" style={{ background: "none", border: "none", color: "var(--maroon)" }}>
              <i className="ti ti-trash" style={{ fontSize: 16 }} />
            </button>
          </div>
        ))}

        <button className="btn btn-danger btn-block" style={{ marginTop: 24 }} onClick={handleLogout}>
          Log out
        </button>
      </div>

      <BottomNav />
    </div>
  );
}
