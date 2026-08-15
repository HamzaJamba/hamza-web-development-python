import { useEffect, useState } from "react";
import TopBar from "../../components/TopBar";
import BottomNav from "../../components/BottomNav";
import { listWishlist, removeWishlist, addCartItem } from "../../api/services";

export default function Wishlist() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState("");

  const load = () => listWishlist().then((data) => { setItems(data.results || data); setLoading(false); });
  useEffect(() => { load(); }, []);

  const remove = async (id) => {
    await removeWishlist(id);
    setItems(items.filter((i) => i.id !== id));
  };

  const addToCart = async (foodItemId, name) => {
    try {
      await addCartItem({ food_item_id: foodItemId, quantity: 1 });
      setToast(`${name} added to cart`);
      setTimeout(() => setToast(""), 2000);
    } catch {
      setToast("Could not add — check restaurant match");
      setTimeout(() => setToast(""), 2000);
    }
  };

  return (
    <div className="page">
      <TopBar title="Wishlist" />

      <div style={{ padding: "0 18px" }}>
        {loading && (
          <div style={{ display: "flex", justifyContent: "center", padding: 40 }}>
            <span className="spinner" />
          </div>
        )}

        {!loading && items.length === 0 && (
          <div className="empty-state">
            <i className="ti ti-heart" />
            No favourites saved yet.
          </div>
        )}

        <div className="card-grid">
          {items.map((w) => (
            <div key={w.id} className="card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600 }}>{w.food_item_detail.name}</div>
                <div style={{ fontSize: 12, color: "var(--gold)", marginTop: 2 }}>Rs {Number(w.food_item_detail.price).toFixed(0)}</div>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <button className="btn btn-primary" style={{ padding: "6px 12px", fontSize: 12 }} onClick={() => addToCart(w.food_item, w.food_item_detail.name)}>
                  Add
                </button>
                <button
                  onClick={() => remove(w.id)}
                  aria-label="Remove from wishlist"
                  style={{ background: "none", border: "none", color: "var(--maroon)" }}
                >
                  <i className="ti ti-trash" style={{ fontSize: 16 }} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {toast && <div className="toast">{toast}</div>}
      <BottomNav />
    </div>
  );
}
