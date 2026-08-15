import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "../../components/TopBar";
import { getCart, updateCartItem, removeCartItem } from "../../api/services";

export default function Cart() {
  const navigate = useNavigate();
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    getCart().then((data) => {
      setCart(data);
      setLoading(false);
    });
  }, []);

  useEffect(load, [load]);

  const changeQty = async (item, delta) => {
    const next = item.quantity + delta;
    if (next < 1) {
      await removeCartItem(item.id);
    } else {
      await updateCartItem(item.id, next);
    }
    load();
  };

  if (loading) {
    return (
      <div className="page" style={{ display: "flex", justifyContent: "center", padding: 60 }}>
        <span className="spinner" />
      </div>
    );
  }

  const isEmpty = !cart?.items?.length;

  return (
    <div className="page">
      <TopBar title="Your cart" showBack onBack={() => navigate(-1)} />

      <div style={{ padding: "0 18px" }}>
        {isEmpty ? (
          <div className="empty-state">
            <i className="ti ti-shopping-bag" />
            Your cart is empty. Go find something delicious.
          </div>
        ) : (
          <>
            <div style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 12 }}>{cart.restaurant_name}</div>

            {cart.items.map((item) => (
              <div key={item.id} className="card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>{item.food_item_name}</div>
                  <div style={{ fontSize: 12, color: "var(--gold)" }}>Rs {Number(item.unit_price).toFixed(0)}</div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <button
                    onClick={() => changeQty(item, -1)}
                    aria-label="Decrease quantity"
                    style={{ background: "var(--surface-raised)", border: "none", color: "var(--text)", width: 26, height: 26, borderRadius: 6 }}
                  >
                    −
                  </button>
                  <span style={{ fontSize: 13, minWidth: 16, textAlign: "center" }}>{item.quantity}</span>
                  <button
                    onClick={() => changeQty(item, 1)}
                    aria-label="Increase quantity"
                    style={{ background: "var(--surface-raised)", border: "none", color: "var(--text)", width: 26, height: 26, borderRadius: 6 }}
                  >
                    +
                  </button>
                </div>
              </div>
            ))}

            <div className="card" style={{ marginTop: 18 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 8 }}>
                <span style={{ color: "var(--text-muted)" }}>Subtotal</span>
                <span>Rs {Number(cart.subtotal).toFixed(0)}</span>
              </div>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Delivery charges and tax are calculated at checkout.</div>
            </div>

            <button className="btn btn-primary btn-block" style={{ marginTop: 18 }} onClick={() => navigate("/checkout")}>
              Proceed to checkout
            </button>
          </>
        )}
      </div>
    </div>
  );
}
