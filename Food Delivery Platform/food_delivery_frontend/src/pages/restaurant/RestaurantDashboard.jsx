import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { myRestaurants, restaurantDashboard, toggleRestaurantOpen, createRestaurant } from "../../api/services";
import SalesChart from "../../components/SalesChart";

export default function RestaurantDashboard() {
  const { logout } = useAuth();
  const [restaurants, setRestaurants] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", slug: "", address_line: "", city: "", contact_number: "" });

  const loadStats = (restaurantId) => {
    restaurantDashboard(restaurantId).then(setStats).finally(() => setLoading(false));
  };

  const load = () => {
    myRestaurants().then((data) => {
      setRestaurants(data);
      if (data.length > 0) {
        const current = activeId && data.some((r) => r.id === activeId) ? activeId : data[0].id;
        setActiveId(current);
        loadStats(current);
      } else {
        setShowCreate(true);
        setLoading(false);
      }
    });
  };

  useEffect(load, []);

  const switchRestaurant = (id) => {
    setActiveId(id);
    setLoading(true);
    loadStats(id);
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    await createRestaurant({ ...form, slug: form.name.toLowerCase().replace(/\s+/g, "-") + "-" + Date.now().toString(36) });
    setShowCreate(false);
    setForm({ name: "", slug: "", address_line: "", city: "", contact_number: "" });
    load();
  };

  const toggleOpen = async (id) => {
    await toggleRestaurantOpen(id);
    load();
  };

  if (loading) {
    return <div className="page-wide" style={{ display: "flex", justifyContent: "center", padding: 60 }}><span className="spinner" /></div>;
  }

  if (showCreate) {
    return (
      <div className="page-wide" style={{ maxWidth: 480, paddingTop: 40 }}>
        {restaurants.length > 0 && (
          <button className="btn btn-secondary" style={{ marginBottom: 20 }} onClick={() => setShowCreate(false)}>
            <i className="ti ti-arrow-left" style={{ fontSize: 14 }} /> Back to dashboard
          </button>
        )}
        <h2 style={{ fontSize: 20, marginBottom: 4 }}>
          {restaurants.length > 0 ? "Add another branch" : "Register your restaurant"}
        </h2>
        <p style={{ color: "var(--text-muted)", fontSize: 13, marginBottom: 24 }}>An admin will review and approve it.</p>
        <form onSubmit={handleCreate}>
          <div className="field"><label>Name</label><input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></div>
          <div className="field"><label>Address</label><input value={form.address_line} onChange={(e) => setForm({ ...form, address_line: e.target.value })} required /></div>
          <div className="field"><label>City</label><input value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} required /></div>
          <div className="field"><label>Contact number</label><input value={form.contact_number} onChange={(e) => setForm({ ...form, contact_number: e.target.value })} required /></div>
          <button className="btn btn-primary btn-block" type="submit">Submit for approval</button>
        </form>
      </div>
    );
  }

  const restaurant = restaurants.find((r) => r.id === activeId) || restaurants[0];

  return (
    <div className="page-wide" style={{ paddingTop: 30 }}>
      {restaurants.length > 1 && (
        <div style={{ display: "flex", gap: 8, overflowX: "auto", marginBottom: 20, paddingBottom: 2 }}>
          {restaurants.map((r) => (
            <button
              key={r.id}
              onClick={() => switchRestaurant(r.id)}
              className="badge"
              style={{
                flexShrink: 0, padding: "8px 16px", fontSize: 12, cursor: "pointer", border: "none",
                background: r.id === activeId ? "var(--gold)" : "var(--surface)",
                color: r.id === activeId ? "#2B1E06" : "var(--text-muted)",
                fontWeight: r.id === activeId ? 600 : 400,
              }}
            >
              {r.name}
            </button>
          ))}
          <button
            onClick={() => setShowCreate(true)}
            className="badge badge-muted"
            style={{ flexShrink: 0, padding: "8px 12px", fontSize: 12, cursor: "pointer", border: "1px solid var(--border-accent)" }}
          >
            <i className="ti ti-plus" style={{ fontSize: 12 }} /> Add branch
          </button>
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
        <div>
          <h2 style={{ fontSize: 20, marginBottom: 2 }}>{restaurant.name}</h2>
          <span className={`badge ${restaurant.status === "APPROVED" ? "badge-success" : "badge-muted"}`}>{restaurant.status}</span>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          {restaurants.length === 1 && (
            <button className="btn btn-secondary" onClick={() => setShowCreate(true)}>
              <i className="ti ti-plus" style={{ fontSize: 14 }} /> Add branch
            </button>
          )}
          <button className="btn btn-secondary" onClick={() => toggleOpen(restaurant.id)}>
            {restaurant.is_open ? "Close shop" : "Open shop"}
          </button>
          <button className="btn btn-secondary" onClick={logout}>Log out</button>
        </div>
      </div>

      <div style={{ display: "flex", gap: 12, marginBottom: 28 }}>
        <Link to="/restaurant/menu" className="card" style={{ flex: 1, textAlign: "center", padding: "18px 10px" }}>
          <i className="ti ti-menu-2" style={{ fontSize: 20, color: "var(--gold)" }} /><div style={{ fontSize: 12, marginTop: 6 }}>Menu</div>
        </Link>
        <Link to="/restaurant/orders" className="card" style={{ flex: 1, textAlign: "center", padding: "18px 10px" }}>
          <i className="ti ti-receipt" style={{ fontSize: 20, color: "var(--gold)" }} /><div style={{ fontSize: 12, marginTop: 6 }}>Orders</div>
        </Link>
      </div>

      {stats && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12, marginBottom: 16 }}>
            {[
              ["Today's sales", `Rs ${Number(stats.sales.today_revenue).toFixed(0)}`],
              ["This week", `Rs ${Number(stats.sales.week_revenue).toFixed(0)}`],
              ["This month", `Rs ${Number(stats.sales.month_revenue).toFixed(0)}`],
              ["Total orders", stats.total_orders_all_time],
            ].map(([label, value]) => (
              <div key={label} style={{ background: "var(--surface)", borderRadius: 10, padding: 16 }}>
                <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 6 }}>{label}</div>
                <div style={{ fontSize: 20, fontWeight: 600 }}>{value}</div>
              </div>
            ))}
          </div>

          {stats.payouts && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12, marginBottom: 24 }}>
              <div className="card" style={{ display: "flex", alignItems: "center", gap: 14 }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: "var(--surface-raised)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  <i className="ti ti-wallet" style={{ fontSize: 18, color: "var(--gold)" }} />
                </div>
                <div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Your payout (all time)</div>
                  <div style={{ fontSize: 17, fontWeight: 600 }}>Rs {Number(stats.payouts.total_payout_all_time).toFixed(0)}</div>
                </div>
              </div>
              <div className="card" style={{ display: "flex", alignItems: "center", gap: 14 }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: "var(--surface-raised)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  <i className="ti ti-percentage" style={{ fontSize: 18, color: "var(--gold)" }} />
                </div>
                <div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Platform commission paid</div>
                  <div style={{ fontSize: 17, fontWeight: 600 }}>Rs {Number(stats.payouts.total_commission_paid_all_time).toFixed(0)}</div>
                </div>
              </div>
            </div>
          )}

          <div className="card" style={{ marginBottom: 28 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-muted)", marginBottom: 14 }}>REVENUE — LAST 30 DAYS</div>
            <SalesChart series={stats.sales.daily_series_30d} />
          </div>

          <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-muted)", marginBottom: 10 }}>BEST SELLING FOOD</div>
          {stats.best_selling_food.length === 0 && <div className="empty-state"><i className="ti ti-chart-bar" />No orders yet.</div>}
          {stats.best_selling_food.map((f) => (
            <div key={f.id} className="card" style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
              <span style={{ fontSize: 13 }}>{f.name}</span>
              <span style={{ fontSize: 12, color: "var(--gold)" }}>{f.total_orders} orders</span>
            </div>
          ))}
        </>
      )}
    </div>
  );
}
