import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listCoupons, createCoupon } from "../../api/services";

const empty = {
  code: "", discount_type: "PERCENT", discount_value: "", min_order_amount: "0",
  max_discount_amount: "", valid_from: "", valid_until: "", usage_limit: "100",
};

export default function Coupons() {
  const [coupons, setCoupons] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(empty);

  const load = () => listCoupons().then((data) => setCoupons(data.results || data));
  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    await createCoupon(form);
    setForm(empty);
    setShowForm(false);
    load();
  };

  return (
    <div className="page-wide" style={{ maxWidth: 560, paddingTop: 30 }}>
      <Link to="/admin" style={{ fontSize: 13, color: "var(--text-muted)", display: "inline-flex", alignItems: "center", gap: 6, marginBottom: 16 }}>
        <i className="ti ti-arrow-left" /> Back to dashboard
      </Link>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <h2 style={{ fontSize: 20 }}>Coupons</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}><i className="ti ti-plus" style={{ fontSize: 14 }} /> New coupon</button>
      </div>

      {showForm && (
        <form onSubmit={submit} className="card" style={{ marginBottom: 20 }}>
          <div className="field"><label>Code</label><input value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value.toUpperCase() })} required /></div>
          <div className="field">
            <label>Discount type</label>
            <select value={form.discount_type} onChange={(e) => setForm({ ...form, discount_type: e.target.value })}>
              <option value="PERCENT">Percentage</option>
              <option value="FLAT">Flat amount</option>
            </select>
          </div>
          <div className="field"><label>Discount value</label><input type="number" value={form.discount_value} onChange={(e) => setForm({ ...form, discount_value: e.target.value })} required /></div>
          <div className="field"><label>Minimum order amount</label><input type="number" value={form.min_order_amount} onChange={(e) => setForm({ ...form, min_order_amount: e.target.value })} /></div>
          <div className="field"><label>Valid from</label><input type="datetime-local" value={form.valid_from} onChange={(e) => setForm({ ...form, valid_from: e.target.value })} required /></div>
          <div className="field"><label>Valid until</label><input type="datetime-local" value={form.valid_until} onChange={(e) => setForm({ ...form, valid_until: e.target.value })} required /></div>
          <div className="field"><label>Usage limit</label><input type="number" value={form.usage_limit} onChange={(e) => setForm({ ...form, usage_limit: e.target.value })} /></div>
          <button className="btn btn-primary btn-block" type="submit">Create coupon</button>
        </form>
      )}

      {coupons.map((c) => (
        <div key={c.id} className="card" style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, fontFamily: "var(--font-mono)" }}>{c.code}</div>
            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
              {c.discount_type === "PERCENT" ? `${c.discount_value}% off` : `Rs ${c.discount_value} off`} &middot; used {c.times_used}/{c.usage_limit}
            </div>
          </div>
          <span className={`badge ${c.is_active ? "badge-success" : "badge-muted"}`}>{c.is_active ? "Active" : "Inactive"}</span>
        </div>
      ))}
    </div>
  );
}
