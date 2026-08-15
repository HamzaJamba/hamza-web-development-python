import { useEffect, useState } from "react";
import TopBar from "../../components/TopBar";
import BottomNav from "../../components/BottomNav";
import RestaurantCard from "../../components/RestaurantCard";
import { listRestaurants, listCategories } from "../../api/services";
import { Link } from "react-router-dom";

export default function Home() {
  const [restaurants, setRestaurants] = useState([]);
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listCategories().then((data) => setCategories(data.results || data));
  }, []);

  useEffect(() => {
    setLoading(true);
    const timeout = setTimeout(() => {
      listRestaurants({ search })
        .then((data) => setRestaurants(data.results || data))
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timeout);
  }, [search]);

  return (
    <div className="page">
      <TopBar right={
        <Link to="/notifications" aria-label="Notifications">
          <i className="ti ti-bell" style={{ fontSize: 18, color: "var(--text)" }} />
        </Link>
      } />

      <div style={{ padding: "0 18px" }}>
        <div className="card" style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
          <i className="ti ti-search" style={{ color: "var(--text-muted)", fontSize: 16 }} />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="biryani, karahi, chai..."
            style={{ background: "none", border: "none", color: "var(--text)", fontSize: 13, flex: 1, outline: "none" }}
          />
        </div>

        {categories.length > 0 && (
          <div style={{ display: "flex", gap: 10, overflowX: "auto", marginBottom: 18, paddingBottom: 2 }}>
            {categories.map((c) => (
              <div
                key={c.id}
                className="badge badge-muted"
                style={{ flexShrink: 0, padding: "8px 14px", fontSize: 12, border: "1px solid var(--border-accent)" }}
              >
                {c.name}
              </div>
            ))}
          </div>
        )}

        <div style={{ fontSize: 11, letterSpacing: 0.6, color: "var(--text-muted)", fontWeight: 600, marginBottom: 10 }}>
          AAP KE QAREEB
        </div>

        {loading && (
          <div style={{ display: "flex", justifyContent: "center", padding: 40 }}>
            <span className="spinner" />
          </div>
        )}

        {!loading && restaurants.length === 0 && (
          <div className="empty-state">
            <i className="ti ti-tools-kitchen-2" />
            No restaurants found. Try a different search.
          </div>
        )}

        {!loading && restaurants.length > 0 && (
          <div className="card-grid fade-in-up">
            {restaurants.map((r) => <RestaurantCard key={r.id} restaurant={r} />)}
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
