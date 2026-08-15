import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const items = [
  { to: "/", icon: "ti-home", label: "Home", end: true },
  { to: "/wishlist", icon: "ti-heart", label: "Wishlist" },
  { to: "/orders", icon: "ti-shopping-bag", label: "Orders" },
  { to: "/cart", icon: "ti-shopping-cart", label: "Cart" },
  { to: "/notifications", icon: "ti-bell", label: "Notifications" },
  { to: "/profile", icon: "ti-user", label: "Profile" },
];

export default function Sidebar() {
  const { logout } = useAuth();

  return (
    <aside className="sidebar">
      <div style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 19, color: "var(--gold)", padding: "8px 14px 24px" }}>
        bhookh<span style={{ color: "var(--text)" }}>.pk</span>
      </div>

      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          className={({ isActive }) => `sidebar-link${isActive ? " active" : ""}`}
        >
          <i className={`ti ${item.icon}`} style={{ fontSize: 18 }} aria-hidden="true" />
          {item.label}
        </NavLink>
      ))}

      <div style={{ flex: 1 }} />

      <button
        onClick={logout}
        className="sidebar-link"
        style={{ background: "none", border: "none", textAlign: "left", width: "100%" }}
      >
        <i className="ti ti-logout" style={{ fontSize: 18 }} aria-hidden="true" />
        Log out
      </button>
    </aside>
  );
}
