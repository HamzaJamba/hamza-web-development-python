import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listRestaurants, approveRestaurant, listUsers, approveUser, suspendUser } from "../../api/services";

export default function Approvals() {
  const [pendingRestaurants, setPendingRestaurants] = useState([]);
  const [pendingUsers, setPendingUsers] = useState([]);

  const load = () => {
    listRestaurants({ status: "PENDING" }).then((data) => setPendingRestaurants(data.results || data));
    listUsers({ is_approved: false }).then((data) => setPendingUsers((data.results || data).filter((u) => u.role !== "CUSTOMER")));
  };
  useEffect(load, []);

  const approveRest = async (id) => { await approveRestaurant(id, "APPROVED"); load(); };
  const rejectRest = async (id) => { await approveRestaurant(id, "REJECTED"); load(); };
  const approveU = async (id) => { await approveUser(id); load(); };
  const suspendU = async (id) => { await suspendUser(id); load(); };

  return (
    <div className="page-wide" style={{ maxWidth: 640, paddingTop: 30 }}>
      <Link to="/admin" style={{ fontSize: 13, color: "var(--text-muted)", display: "inline-flex", alignItems: "center", gap: 6, marginBottom: 16 }}>
        <i className="ti ti-arrow-left" /> Back to dashboard
      </Link>
      <h2 style={{ fontSize: 20, marginBottom: 20 }}>Approvals</h2>

      <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-muted)", marginBottom: 10 }}>PENDING RESTAURANTS</div>
      {pendingRestaurants.length === 0 && <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 20 }}>Nothing pending.</p>}
      {pendingRestaurants.map((r) => (
        <div key={r.id} className="card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600 }}>{r.name}</div>
            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{r.city}</div>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button className="btn btn-primary" style={{ padding: "6px 14px", fontSize: 12 }} onClick={() => approveRest(r.id)}>Approve</button>
            <button className="btn btn-danger" style={{ padding: "6px 14px", fontSize: 12 }} onClick={() => rejectRest(r.id)}>Reject</button>
          </div>
        </div>
      ))}

      <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-muted)", margin: "24px 0 10px" }}>PENDING RIDERS / OWNERS</div>
      {pendingUsers.length === 0 && <p style={{ fontSize: 12, color: "var(--text-muted)" }}>Nothing pending.</p>}
      {pendingUsers.map((u) => (
        <div key={u.id} className="card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600 }}>{u.username}</div>
            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{u.role} &middot; {u.email}</div>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button className="btn btn-primary" style={{ padding: "6px 14px", fontSize: 12 }} onClick={() => approveU(u.id)}>Approve</button>
            <button className="btn btn-danger" style={{ padding: "6px 14px", fontSize: 12 }} onClick={() => suspendU(u.id)}>Suspend</button>
          </div>
        </div>
      ))}
    </div>
  );
}
