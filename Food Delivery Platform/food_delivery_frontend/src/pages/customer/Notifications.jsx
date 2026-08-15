import { useEffect, useState } from "react";
import TopBar from "../../components/TopBar";
import { useNavigate } from "react-router-dom";
import { listNotifications, markAllNotificationsRead } from "../../api/services";

const ICONS = {
  ORDER_PLACED: "ti-receipt",
  ORDER_ACCEPTED: "ti-check",
  FOOD_PREPARING: "ti-tools-kitchen-2",
  RIDER_ASSIGNED: "ti-motorbike",
  DELIVERED: "ti-circle-check",
  ORDER_CANCELLED: "ti-x",
  SYSTEM: "ti-bell",
};

export default function Notifications() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listNotifications().then((data) => {
      setItems(data.results || data);
      setLoading(false);
    });
    markAllNotificationsRead();
  }, []);

  return (
    <div className="page">
      <TopBar title="Notifications" showBack onBack={() => navigate(-1)} />

      <div style={{ padding: "0 18px" }}>
        {loading && (
          <div style={{ display: "flex", justifyContent: "center", padding: 40 }}>
            <span className="spinner" />
          </div>
        )}

        {!loading && items.length === 0 && (
          <div className="empty-state">
            <i className="ti ti-bell" />
            No notifications yet.
          </div>
        )}

        {items.map((n) => (
          <div key={n.id} className="card" style={{ display: "flex", gap: 12, marginBottom: 8 }}>
            <div style={{ width: 34, height: 34, borderRadius: "50%", background: "var(--surface-raised)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <i className={`ti ${ICONS[n.type] || "ti-bell"}`} style={{ fontSize: 16, color: "var(--gold)" }} />
            </div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 600 }}>{n.title}</div>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{n.message}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
