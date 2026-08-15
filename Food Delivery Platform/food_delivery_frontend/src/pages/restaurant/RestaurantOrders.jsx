import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import StatusBadge from "../../components/StatusBadge";
import { listOrders, updateOrderStatus } from "../../api/services";

const NEXT_STATUS = {
  PENDING: "ACCEPTED",
  ACCEPTED: "PREPARING",
  PREPARING: "READY_FOR_PICKUP",
};
const NEXT_LABEL = {
  PENDING: "Accept order",
  ACCEPTED: "Start preparing",
  PREPARING: "Mark ready for pickup",
};

export default function RestaurantOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => listOrders().then((data) => { setOrders(data.results || data); setLoading(false); });
  useEffect(() => { load(); }, []);

  const advance = async (order) => {
    await updateOrderStatus(order.id, NEXT_STATUS[order.status]);
    load();
  };

  if (loading) return <div className="page-wide" style={{ display: "flex", justifyContent: "center", padding: 60 }}><span className="spinner" /></div>;

  return (
    <div className="page-wide" style={{ maxWidth: 640, paddingTop: 30 }}>
      <Link to="/restaurant" style={{ fontSize: 13, color: "var(--text-muted)", display: "inline-flex", alignItems: "center", gap: 6, marginBottom: 16 }}>
        <i className="ti ti-arrow-left" /> Back to dashboard
      </Link>
      <h2 style={{ fontSize: 20, marginBottom: 20 }}>Order queue</h2>

      {orders.length === 0 && <div className="empty-state"><i className="ti ti-receipt" />No orders yet.</div>}

      {orders.map((o) => (
        <div key={o.id} className="card" style={{ marginBottom: 12 }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
            <span style={{ fontSize: 13, fontWeight: 600 }}>{o.order_number}</span>
            <StatusBadge status={o.status} />
          </div>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 10 }}>Rs {Number(o.grand_total).toFixed(0)}</div>
          {NEXT_STATUS[o.status] && (
            <button className="btn btn-primary btn-block" onClick={() => advance(o)}>
              {NEXT_LABEL[o.status]}
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
