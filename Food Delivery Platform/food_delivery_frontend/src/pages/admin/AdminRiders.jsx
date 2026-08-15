import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { adminListRiders, adminReviewCnic } from "../../api/services";

const STATUS_BADGE = {
  NOT_SUBMITTED: "badge-muted",
  PENDING: "badge-gold",
  VERIFIED: "badge-success",
  REJECTED: "badge-danger",
};

export default function AdminRiders() {
  const [riders, setRiders] = useState([]);
  const [filter, setFilter] = useState("PENDING");
  const [rejectingId, setRejectingId] = useState(null);
  const [reason, setReason] = useState("");

  const load = () => {
    const params = filter ? { cnic_status: filter } : {};
    adminListRiders(params).then((data) => setRiders(data.results || data));
  };
  useEffect(load, [filter]);

  const verify = async (riderId) => {
    await adminReviewCnic(riderId, { action: "verify" });
    load();
  };

  const reject = async (riderId) => {
    await adminReviewCnic(riderId, { action: "reject", reason });
    setRejectingId(null);
    setReason("");
    load();
  };

  return (
    <div className="page-wide" style={{ maxWidth: 640, paddingTop: 30 }}>
      <Link to="/admin" style={{ fontSize: 13, color: "var(--text-muted)", display: "inline-flex", alignItems: "center", gap: 6, marginBottom: 16 }}>
        <i className="ti ti-arrow-left" /> Back to dashboard
      </Link>
      <h2 style={{ fontSize: 20, marginBottom: 16 }}>Rider CNIC verification</h2>

      <div style={{ display: "flex", gap: 8, marginBottom: 20, overflowX: "auto" }}>
        {["PENDING", "VERIFIED", "REJECTED", "NOT_SUBMITTED", ""].map((s) => (
          <button
            key={s || "all"}
            onClick={() => setFilter(s)}
            className="badge"
            style={{
              flexShrink: 0, padding: "8px 14px", fontSize: 12, cursor: "pointer", border: "none",
              background: filter === s ? "var(--gold)" : "var(--surface)",
              color: filter === s ? "#2B1E06" : "var(--text-muted)",
            }}
          >
            {s || "All"}
          </button>
        ))}
      </div>

      {riders.length === 0 && <div className="empty-state"><i className="ti ti-id" />No riders in this category.</div>}

      {riders.map((r) => (
        <div key={r.id} className="card" style={{ marginBottom: 10 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
            <div>
              <div style={{ fontSize: 13, fontWeight: 600 }}>{r.username}</div>
              <div style={{ fontSize: 12, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>{r.cnic_number || "No CNIC submitted"}</div>
            </div>
            <span className={`badge ${STATUS_BADGE[r.cnic_status]}`}>{r.cnic_status.replace("_", " ")}</span>
          </div>

          {r.cnic_status === "PENDING" && (
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn btn-primary" style={{ flex: 1, padding: "8px", fontSize: 12 }} onClick={() => verify(r.id)}>
                Verify
              </button>
              <button className="btn btn-danger" style={{ flex: 1, padding: "8px", fontSize: 12 }} onClick={() => setRejectingId(r.id)}>
                Reject
              </button>
            </div>
          )}

          {rejectingId === r.id && (
            <div style={{ marginTop: 10, display: "flex", gap: 8 }}>
              <input
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Reason for rejection"
                style={{ flex: 1, background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: "8px 10px", color: "var(--text)", fontSize: 12 }}
              />
              <button className="btn btn-danger" style={{ padding: "8px 14px", fontSize: 12 }} onClick={() => reject(r.id)}>Confirm</button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
