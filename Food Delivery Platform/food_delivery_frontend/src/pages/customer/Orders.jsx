import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import TopBar from "../../components/TopBar";
import BottomNav from "../../components/BottomNav";
import StatusBadge from "../../components/StatusBadge";
import { listOrders } from "../../api/services";

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listOrders().then((data) => {
      setOrders(data.results || data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="page">
      <TopBar title="Your orders" />

      <div style={{ padding: "0 18px" }}>
        {loading && (
          <div style={{ display: "flex", justifyContent: "center", padding: 40 }}>
            <span className="spinner" />
          </div>
        )}

        {!loading && orders.length === 0 && (
          <div className="empty-state">
            <i className="ti ti-receipt" />
            No orders yet. Time to order something good.
          </div>
        )}

        <div className="card-grid">
          {orders.map((o) => (
            <Link key={o.id} to={`/orders/${o.id}`}>
              <div className="card">
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                  <span style={{ fontSize: 13, fontWeight: 600 }}>{o.restaurant_name}</span>
                  <StatusBadge status={o.status} />
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "var(--text-muted)" }}>
                  <span>{o.order_number}</span>
                  <span>Rs {Number(o.grand_total).toFixed(0)}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
