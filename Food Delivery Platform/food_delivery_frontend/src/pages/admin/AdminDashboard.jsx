import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { adminDashboard } from "../../api/services";
import SalesChart from "../../components/SalesChart";
import AnimatedCounter from "../../components/AnimatedCounter";
import AnimatedBackground from "../../components/AnimatedBackground";

export default function AdminDashboard() {
  const { logout } = useAuth();
  const [data, setData] = useState(null);

  useEffect(() => { adminDashboard().then(setData); }, []);

  if (!data) return <div className="page-wide" style={{ display: "flex", justifyContent: "center", padding: 60 }}><span className="spinner" /></div>;

  const cards = [
    ["Approved restaurants", data.totals.approved_restaurants, ""],
    ["Pending approvals", data.totals.pending_restaurants, ""],
    ["Total riders", data.totals.total_riders, ""],
    ["Total customers", data.totals.total_customers, ""],
    ["Total orders", data.totals.total_orders, ""],
    ["Total revenue", Number(data.totals.total_revenue), "Rs "],
  ];

  const commissionCards = [
    ["Platform commission earned", Number(data.totals.total_commission_earned), "ti-percentage"],
    ["Paid out to restaurants", Number(data.totals.total_restaurant_payouts), "ti-building-store"],
  ];

  const quickLinks = [
    ["/admin/approvals", "ti-user-check", "Approvals"],
    ["/admin/riders", "ti-id", "Rider CNICs"],
    ["/admin/coupons", "ti-ticket", "Coupons"],
    ["/admin/settings", "ti-settings", "Settings"],
  ];

  return (
    <div className="page-wide" style={{ paddingTop: 30, position: "relative" }}>
      <AnimatedBackground particleCount={10} />
      <div style={{ position: "relative", zIndex: 1 }}>

      <div className="fade-in-up" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h2 style={{ fontSize: 20 }}>Admin dashboard</h2>
        <button className="btn btn-secondary" onClick={logout}>Log out</button>
      </div>

      <div className="fade-in-up" style={{ display: "flex", gap: 12, marginBottom: 24, flexWrap: "wrap", animationDelay: "60ms" }}>
        {quickLinks.map(([to, icon, label]) => (
          <Link key={to} to={to} className="card hover-lift" style={{ flex: 1, minWidth: 100, textAlign: "center", padding: "16px 10px" }}>
            <i className={`ti ${icon}`} style={{ fontSize: 20, color: "var(--gold)" }} /><div style={{ fontSize: 12, marginTop: 6 }}>{label}</div>
          </Link>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12, marginBottom: 16 }}>
        {cards.map(([label, value, prefix], i) => (
          <div
            key={label}
            className="fade-in-up hover-lift"
            style={{ background: "var(--surface)", borderRadius: 10, padding: 16, animationDelay: `${100 + i * 60}ms` }}
          >
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 6 }}>{label}</div>
            <div style={{ fontSize: 20, fontWeight: 600 }}>
              <AnimatedCounter value={value} prefix={prefix} />
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12, marginBottom: 28 }}>
        {commissionCards.map(([label, value, icon], i) => (
          <div
            key={label}
            className="card hover-lift fade-in-up"
            style={{ display: "flex", alignItems: "center", gap: 14, animationDelay: `${460 + i * 60}ms` }}
          >
            <div style={{ width: 40, height: 40, borderRadius: 10, background: "var(--surface-raised)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <i className={`ti ${icon}`} style={{ fontSize: 18, color: "var(--gold)" }} />
            </div>
            <div>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{label}</div>
              <div style={{ fontSize: 17, fontWeight: 600 }}><AnimatedCounter value={value} prefix="Rs " /></div>
            </div>
          </div>
        ))}
      </div>

      <div className="card fade-in-up" style={{ marginBottom: 28, animationDelay: "600ms" }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-muted)", marginBottom: 14 }}>REVENUE — LAST 30 DAYS</div>
        <SalesChart series={data.sales.daily_series_30d} />
      </div>

      <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-muted)", marginBottom: 10 }}>POPULAR FOODS</div>
      {data.popular_foods.length === 0 && <div className="empty-state"><i className="ti ti-chart-bar" />No order data yet.</div>}
      {data.popular_foods.map((f, i) => (
        <div
          key={f.id}
          className="card hover-lift fade-in-up"
          style={{ display: "flex", justifyContent: "space-between", marginBottom: 8, animationDelay: `${680 + i * 40}ms` }}
        >
          <span style={{ fontSize: 13 }}>{f.name} <span style={{ color: "var(--text-muted)" }}>&middot; {f.restaurant__name}</span></span>
          <span style={{ fontSize: 12, color: "var(--gold)" }}>{f.total_orders} orders</span>
        </div>
      ))}

      </div>
    </div>
  );
}
