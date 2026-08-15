export default function FoodItemCard({ item, onAdd, onWishlist, isWishlisted }) {
  const price = item.discount_price || item.price;
  return (
    <div className="card hover-lift" style={{ display: "flex", gap: 12, marginBottom: 10 }}>
      <div
        style={{
          width: 64,
          height: 64,
          borderRadius: 10,
          background: "var(--surface-raised)",
          flexShrink: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          overflow: "hidden",
        }}
      >
        {item.primary_image ? (
          <img src={item.primary_image} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : (
          <i className="ti ti-toppings" style={{ color: "var(--gold)", fontSize: 22 }} aria-hidden="true" />
        )}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
          <span style={{ fontSize: 14, fontWeight: 600 }}>{item.name}</span>
          {onWishlist && (
            <button
              onClick={() => onWishlist(item)}
              aria-label={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
              style={{ background: "none", border: "none", padding: 0, color: isWishlisted ? "var(--maroon)" : "var(--text-muted)" }}
            >
              <i className={`ti ${isWishlisted ? "ti-heart-filled" : "ti-heart"}`} style={{ fontSize: 18 }} />
            </button>
          )}
        </div>
        <div style={{ fontSize: 11, color: "var(--text-muted)", margin: "3px 0 8px" }}>
          {item.description ? item.description.slice(0, 50) : "\u00A0"}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: "var(--gold)" }}>Rs {Number(price).toFixed(0)}</span>
          {onAdd && (
            <button className="btn btn-primary" style={{ padding: "6px 14px", fontSize: 12 }} onClick={() => onAdd(item)}>
              Add
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
