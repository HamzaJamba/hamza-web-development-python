import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { getRiderProfile, toggleOnline, availableDeliveries, myDeliveries, acceptDelivery, updateDeliveryStatus, updateRiderProfile } from "../../api/services";

const NEXT_STATUS = { ASSIGNED: "PICKED_UP", PICKED_UP: "DELIVERED" };
const NEXT_LABEL = { ASSIGNED: "Mark picked up", PICKED_UP: "Mark delivered" };

const CNIC_BADGE = {
  NOT_SUBMITTED: { className: "badge-muted", label: "CNIC not submitted" },
  PENDING: { className: "badge-gold", label: "CNIC pending review" },
  VERIFIED: { className: "badge-success", label: "CNIC verified" },
  REJECTED: { className: "badge-danger", label: "CNIC rejected" },
};

export default function RiderDashboard() {
  const { logout } = useAuth();
  const [profile, setProfile] = useState(null);
  const [available, setAvailable] = useState([]);
  const [mine, setMine] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cnicInput, setCnicInput] = useState("");
  const [onlineError, setOnlineError] = useState("");

  const load = () => {
    getRiderProfile().then((p) => { setProfile(p); setCnicInput(p.cnic_number || ""); });
    availableDeliveries().then((data) => setAvailable(data.results || data));
    myDeliveries().then((data) => setMine((data.results || data).filter((d) => d.status !== "DELIVERED")));
    setLoading(false);
  };

  useEffect(load, []);

  const goOnline = async () => {
    setOnlineError("");
    try {
      await toggleOnline();
      load();
    } catch (err) {
      setOnlineError(err.response?.data?.detail || "Could not go online.");
    }
  };

  const submitCnic = async (e) => {
    e.preventDefault();
    await updateRiderProfile({ cnic_number: cnicInput });
    load();
  };

  const accept = async (id) => {
    await acceptDelivery(id);
    load();
  };

  const advance = async (delivery) => {
    await updateDeliveryStatus(delivery.id, NEXT_STATUS[delivery.status]);
    load();
  };

  if (loading || !profile) return <div className="page-wide" style={{ display: "flex", justifyContent: "center", padding: 60 }}><span className="spinner" /></div>;

  const cnicBadge = CNIC_BADGE[profile.cnic_status] || CNIC_BADGE.NOT_SUBMITTED;
  const isVerified = profile.cnic_status === "VERIFIED";

  return (
    <div className="page-wide" style={{ maxWidth: 560, paddingTop: 30 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <div>
          <h2 style={{ fontSize: 20, marginBottom: 4 }}>Hi, {profile.username}</h2>
          <span className={`badge ${profile.is_online ? "badge-success" : "badge-muted"}`}>{profile.is_online ? "Online" : "Offline"}</span>
        </div>
        <button className="btn btn-secondary" onClick={logout}>Log out</button>
      </div>

      <div style={{ marginBottom: 20 }}>
        <span className={`badge ${cnicBadge.className}`}>
          <i className="ti ti-id" style={{ fontSize: 12 }} /> {cnicBadge.label}
        </span>
      </div>

      {!isVerified && (
        <div className="card" style={{ marginBottom: 24 }}>
          {profile.cnic_status === "REJECTED" && profile.cnic_rejection_reason && (
            <p className="field-error" style={{ marginBottom: 12 }}>Rejected: {profile.cnic_rejection_reason}</p>
          )}
          <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 12 }}>
            Submit your CNIC number so an admin can verify you. You can't go online until it's verified.
          </p>
          <form onSubmit={submitCnic} style={{ display: "flex", gap: 8 }}>
            <input
              value={cnicInput}
              onChange={(e) => setCnicInput(e.target.value)}
              placeholder="42101-1234567-1"
              style={{ flex: 1, background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: "10px 12px", color: "var(--text)", fontSize: 13 }}
              required
            />
            <button className="btn btn-primary" type="submit">Submit</button>
          </form>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 12, marginBottom: 24 }}>
        <div style={{ background: "var(--surface)", borderRadius: 10, padding: 16 }}>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 6 }}>Total earnings</div>
          <div style={{ fontSize: 20, fontWeight: 600 }}>Rs {Number(profile.total_earnings).toFixed(0)}</div>
        </div>
        <div style={{ background: "var(--surface)", borderRadius: 10, padding: 16 }}>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 6 }}>Deliveries</div>
          <div style={{ fontSize: 20, fontWeight: 600 }}>{profile.total_deliveries}</div>
        </div>
      </div>

      <button className="btn btn-primary btn-block" style={{ marginBottom: 8 }} onClick={goOnline} disabled={!isVerified && !profile.is_online}>
        {profile.is_online ? "Go offline" : "Go online"}
      </button>
      {onlineError && <p className="field-error" style={{ marginBottom: 20 }}>{onlineError}</p>}
      {!onlineError && <div style={{ marginBottom: 20 }} />}

      {mine.length > 0 && (
        <>
          <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-muted)", marginBottom: 10 }}>ACTIVE DELIVERY</div>
          {mine.map((d) => (
            <div key={d.id} className="card" style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>{d.order_number}</div>
              <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 10 }}>{d.restaurant_name}</div>
              <button className="btn btn-primary btn-block" onClick={() => advance(d)}>{NEXT_LABEL[d.status]}</button>
            </div>
          ))}
        </>
      )}

      {profile.is_online && mine.length === 0 && (
        <>
          <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-muted)", marginBottom: 10 }}>AVAILABLE DELIVERIES</div>
          {available.length === 0 && <div className="empty-state"><i className="ti ti-motorbike" />No deliveries waiting right now.</div>}
          {available.map((d) => (
            <div key={d.id} className="card" style={{ marginBottom: 10, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600 }}>{d.order_number}</div>
                <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{d.restaurant_name}</div>
              </div>
              <button className="btn btn-primary" onClick={() => accept(d.id)}>Accept</button>
            </div>
          ))}
        </>
      )}
    </div>
  );
}
