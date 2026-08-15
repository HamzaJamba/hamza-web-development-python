import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getPlatformSettings, updatePlatformSettings } from "../../api/services";

export default function Settings() {
  const [form, setForm] = useState(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => { getPlatformSettings().then(setForm); }, []);

  const save = async (e) => {
    e.preventDefault();
    await updatePlatformSettings(form);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  if (!form) return <div className="page-wide" style={{ display: "flex", justifyContent: "center", padding: 60 }}><span className="spinner" /></div>;

  return (
    <div className="page-wide" style={{ maxWidth: 480, paddingTop: 30 }}>
      <Link to="/admin" style={{ fontSize: 13, color: "var(--text-muted)", display: "inline-flex", alignItems: "center", gap: 6, marginBottom: 16 }}>
        <i className="ti ti-arrow-left" /> Back to dashboard
      </Link>
      <h2 style={{ fontSize: 20, marginBottom: 20 }}>Platform settings</h2>

      <form onSubmit={save}>
        <div className="field"><label>Delivery charge (Rs)</label><input type="number" value={form.delivery_charge} onChange={(e) => setForm({ ...form, delivery_charge: e.target.value })} /></div>
        <div className="field"><label>Tax rate (%)</label><input type="number" value={form.tax_rate_percent} onChange={(e) => setForm({ ...form, tax_rate_percent: e.target.value })} /></div>
        <div className="field"><label>Rider delivery fee (Rs)</label><input type="number" value={form.rider_delivery_fee} onChange={(e) => setForm({ ...form, rider_delivery_fee: e.target.value })} /></div>
        <div className="field"><label>Platform commission (%)</label><input type="number" value={form.platform_commission_percent} onChange={(e) => setForm({ ...form, platform_commission_percent: e.target.value })} /></div>
        <div className="field"><label>Support email</label><input type="email" value={form.support_email} onChange={(e) => setForm({ ...form, support_email: e.target.value })} /></div>
        <div className="field"><label>Support phone</label><input value={form.support_phone} onChange={(e) => setForm({ ...form, support_phone: e.target.value })} /></div>
        <button className="btn btn-primary btn-block" type="submit">Save settings</button>
        {saved && <p style={{ fontSize: 12, color: "var(--gold)", marginTop: 10, textAlign: "center" }}>Settings saved.</p>}
      </form>
    </div>
  );
}
