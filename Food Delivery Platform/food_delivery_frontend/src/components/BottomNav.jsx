import { NavLink } from "react-router-dom";

const items = [
  { to: "/", icon: "ti-home", label: "Home", end: true },
  { to: "/wishlist", icon: "ti-heart", label: "Wishlist" },
  { to: "/orders", icon: "ti-shopping-bag", label: "Orders" },
  { to: "/profile", icon: "ti-user", label: "Profile" },
];

export default function BottomNav() {
  return (
    <nav className="bottom-nav">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          className={({ isActive }) => (isActive ? "bottom-nav-link active" : "bottom-nav-link")}
        >
          <i className={`ti ${item.icon}`} aria-hidden="true" />
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}
