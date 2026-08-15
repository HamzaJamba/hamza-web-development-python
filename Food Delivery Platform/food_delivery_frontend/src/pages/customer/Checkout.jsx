import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "../../components/TopBar";
import { listAddresses, createAddress } from "../../api/auth";
import { getCart, checkout } from "../../api/services";

const PAYMENT_METHODS = [
  { value: "COD", label: "Cash on delivery", icon: "ti-cash" },
  { value: "STRIPE", label: "Card (Stripe)", icon: "ti-credit-card" },
  { value: "PAYPAL", label: "PayPal", icon: "ti-brand-paypal" },
];

export default function Checkout() {
  const navigate = useNavigate();
  const [cart, setCart] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [addressId, setAddressId] = useState("");
  const [showNewAddress, setShowNewAddress] = useState(false);
  const [newAddress, setNewAddress] = useState({ label: "Home", address_line: "", city: "" });
  const [method, setMethod] = useState("COD");
  const [couponCode, setCouponCode] = useState("");
  const [error, setError] = useState("");
  const [placing, setPlacing] = useState(false);

  useEffect(() => {
    getCart().then(setCart);
    listAddresses().then((data) => {
      const list = data.results || data;
      setAddresses(list);
      const def = list.find((a) => a.is_default) || list[0];
      if (def) setAddressId(def.id);
      else setShowNewAddress(true);
    });
  }, []);

  const saveAddress = async () => {
    const created = await createAddress(newAddress);
    setAddresses([...addresses, created]);
    setAddressId(created.id);
    setShowNewAddress(false);
  };

  const placeOrder = async () => {
    setError("");
    if (!addressId) {
      setError("Please select or add a delivery address.");
      return;
    }
    setPlacing(true);
    try {
      const order = await checkout({
        delivery_address_id: addressId,
        payment_method: method,
        coupon_code: couponCode || undefined,
      });
      navigate(`/orders/${order.id}`, { replace: true });
    } catch (e) {
      const data = e.response?.data;
      setError(data?.detail || (data ? Object.values(data).flat().join(" ") : "Could not place order."));
    } finally {
      setPlacing(false);
    }
  };

  if (!cart) {
    return (
      <div className="page" style={{ display: "flex", justifyContent: "center", padding: 60 }}>
        <span className="spinner" />
      </div>
    );
  }

  return (
    <div className="page">
      <TopBar title="Checkout" showBack onBack={() => navigate(-1)} />

      <div style={{ padding: "0 18px" }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)", marginBottom: 10 }}>DELIVERY ADDRESS</div>
        {addresses.map((a) => (
          <label key={a.id} className="card" style={{ display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 8, border: addressId === a.id ? "1px solid var(--gold)" : "1px solid transparent" }}>
            <input type="radio" name="address" checked={addressId === a.id} onChange={() => setAddressId(a.id)} style={{ marginTop: 3 }} />
            <div>
              <div style={{ fontSize: 13, fontWeight: 600 }}>{a.label || "Address"}</div>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{a.address_line}, {a.city}</div>
            </div>
          </label>
        ))}

        {!showNewAddress && (
          <button className="btn btn-secondary btn-block" style={{ marginBottom: 20 }} onClick={() => setShowNewAddress(true)}>
            <i className="ti ti-plus" style={{ fontSize: 14 }} /> Add new address
          </button>
        )}

        {showNewAddress && (
          <div className="card" style={{ marginBottom: 20 }}>
            <div className="field">
              <label htmlFor="label">Label</label>
              <input id="label" value={newAddress.label} onChange={(e) => setNewAddress({ ...newAddress, label: e.target.value })} />
            </div>
            <div className="field">
              <label htmlFor="line">Address</label>
              <input id="line" value={newAddress.address_line} onChange={(e) => setNewAddress({ ...newAddress, address_line: e.target.value })} />
            </div>
            <div className="field">
              <label htmlFor="city">City</label>
              <input id="city" value={newAddress.city} onChange={(e) => setNewAddress({ ...newAddress, city: e.target.value })} />
            </div>
            <button className="btn btn-primary btn-block" onClick={saveAddress}>Save address</button>
          </div>
        )}

        <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)", marginBottom: 10 }}>PAYMENT METHOD</div>
        <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
          {PAYMENT_METHODS.map((m) => (
            <button
              key={m.value}
              className="card"
              onClick={() => setMethod(m.value)}
              style={{ flex: 1, textAlign: "center", padding: "12px 4px", border: method === m.value ? "1px solid var(--gold)" : "1px solid transparent" }}
            >
              <i className={`ti ${m.icon}`} style={{ fontSize: 18, color: method === m.value ? "var(--gold)" : "var(--text-muted)" }} />
              <div style={{ fontSize: 10, marginTop: 6 }}>{m.label}</div>
            </button>
          ))}
        </div>

        <div className="field">
          <label htmlFor="coupon">Coupon code (optional)</label>
          <input id="coupon" value={couponCode} onChange={(e) => setCouponCode(e.target.value.toUpperCase())} placeholder="WELCOME50" />
        </div>

        <div className="card" style={{ marginBottom: 20 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 6 }}>
            <span style={{ color: "var(--text-muted)" }}>Subtotal</span>
            <span>Rs {Number(cart.subtotal).toFixed(0)}</span>
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Delivery charges, tax, and any discount are applied when you place the order.</div>
        </div>

        {error && <p className="field-error" style={{ marginBottom: 16 }}>{error}</p>}

        <button className="btn btn-primary btn-block" disabled={placing} onClick={placeOrder}>
          {placing ? <span className="spinner" /> : "Place order"}
        </button>
      </div>
    </div>
  );
}
