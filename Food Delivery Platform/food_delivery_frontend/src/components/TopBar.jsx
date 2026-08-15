import { Link } from "react-router-dom";

export default function TopBar({ title, showBack, onBack, right }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "18px 18px 14px",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        {showBack && (
          <button
            onClick={onBack}
            style={{ background: "none", border: "none", color: "var(--text)", padding: 0 }}
            aria-label="Go back"
          >
            <i className="ti ti-arrow-left" style={{ fontSize: 20 }} />
          </button>
        )}
        {title ? (
          <span style={{ fontSize: 16, fontWeight: 600 }}>{title}</span>
        ) : (
          <Link to="/" style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 19, color: "var(--gold)" }}>
            bhookh<span style={{ color: "var(--text)" }}>.pk</span>
          </Link>
        )}
      </div>
      {right}
    </div>
  );
}
