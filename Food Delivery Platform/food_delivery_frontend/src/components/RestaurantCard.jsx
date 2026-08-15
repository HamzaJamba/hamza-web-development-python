import { Link } from "react-router-dom";

export default function RestaurantCard({ restaurant }) {
  return (
    <Link to={`/restaurants/${restaurant.id}`}>
      <div className="card hover-lift" style={{ display: "flex", gap: 12, marginBottom: 12 }}>
        <div
          style={{
            width: 56,
            height: 56,
            borderRadius: 10,
            background: "var(--surface-raised)",
            flexShrink: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            overflow: "hidden",
          }}
        >
          {restaurant.logo ? (
            <img src={restaurant.logo} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          ) : (
            <i className="ti ti-tools-kitchen-2" style={{ color: "var(--gold)", fontSize: 24 }} aria-hidden="true" />
          )}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
            <span style={{ fontSize: 14, fontWeight: 600 }}>{restaurant.name}</span>
            <span style={{ fontSize: 11, color: "var(--gold)", fontWeight: 600, display: "flex", alignItems: "center", gap: 2 }}>
              <i className="ti ti-star" style={{ fontSize: 12 }} aria-hidden="true" />
              {Number(restaurant.avg_rating).toFixed(1)}
            </span>
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", margin: "3px 0 6px" }}>
            {restaurant.city} &middot; {restaurant.total_reviews} reviews
          </div>
          <span className={`badge ${restaurant.is_open ? "badge-success" : "badge-muted"}`}>
            {restaurant.is_open ? "Open now" : "Closed"}
          </span>
        </div>
      </div>
    </Link>
  );
}
