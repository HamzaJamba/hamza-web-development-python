import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { myRestaurants, listFoodItems, createFoodItem, updateFoodItem, deleteFoodItem, listCategories, bulkImportFoodItems } from "../../api/services";

export default function MenuManager() {
  const [restaurant, setRestaurant] = useState(null);
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", price: "", category: "", description: "" });
  const [showImport, setShowImport] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importResult, setImportResult] = useState(null);
  const [importing, setImporting] = useState(false);

  const load = async () => {
    const restaurants = await myRestaurants();
    if (!restaurants.length) return;
    setRestaurant(restaurants[0]);
    const foods = await listFoodItems({ restaurant: restaurants[0].id });
    setItems(foods.results || foods);
  };

  useEffect(() => {
    load();
    listCategories().then((data) => setCategories(data.results || data));
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    await createFoodItem({ ...form, restaurant: restaurant.id });
    setForm({ name: "", price: "", category: "", description: "" });
    setShowForm(false);
    load();
  };

  const toggleAvailable = async (item) => {
    await updateFoodItem(item.id, { is_available: !item.is_available });
    load();
  };

  const remove = async (id) => {
    await deleteFoodItem(id);
    load();
  };

  const runImport = async () => {
    if (!importFile) return;
    setImporting(true);
    setImportResult(null);
    try {
      const result = await bulkImportFoodItems(restaurant.id, importFile);
      setImportResult(result);
      load();
    } catch (err) {
      setImportResult({ error: err.response?.data?.detail || "Import failed." });
    } finally {
      setImporting(false);
    }
  };

  if (!restaurant) return null;

  return (
    <div className="page-wide" style={{ maxWidth: 640, paddingTop: 30 }}>
      <Link to="/restaurant" style={{ fontSize: 13, color: "var(--text-muted)", display: "inline-flex", alignItems: "center", gap: 6, marginBottom: 16 }}>
        <i className="ti ti-arrow-left" /> Back to dashboard
      </Link>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20, flexWrap: "wrap", gap: 10 }}>
        <h2 style={{ fontSize: 20 }}>Menu</h2>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-secondary" onClick={() => { setShowImport(!showImport); setShowForm(false); }}>
            <i className="ti ti-file-spreadsheet" style={{ fontSize: 14 }} /> Bulk import CSV
          </button>
          <button className="btn btn-primary" onClick={() => { setShowForm(!showForm); setShowImport(false); }}>
            <i className="ti ti-plus" style={{ fontSize: 14 }} /> Add food item
          </button>
        </div>
      </div>

      {showImport && (
        <div className="card" style={{ marginBottom: 20 }}>
          <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 12 }}>
            CSV columns: <code style={{ color: "var(--gold)" }}>name, price, category, description, discount_price</code>.
            Category names are matched or created automatically. Only <code>name</code> and <code>price</code> are required.
          </p>
          <div className="field">
            <label>CSV file</label>
            <input type="file" accept=".csv" onChange={(e) => setImportFile(e.target.files[0])} />
          </div>
          <button className="btn btn-primary btn-block" disabled={!importFile || importing} onClick={runImport}>
            {importing ? <span className="spinner" /> : "Import"}
          </button>

          {importResult && !importResult.error && (
            <p style={{ fontSize: 12, color: "var(--gold)", marginTop: 12 }}>
              {importResult.created_count} item(s) imported{importResult.error_count > 0 ? `, ${importResult.error_count} row(s) skipped` : ""}.
            </p>
          )}
          {importResult?.error && <p className="field-error" style={{ marginTop: 12 }}>{importResult.error}</p>}
        </div>
      )}

      {showForm && (
        <form onSubmit={submit} className="card" style={{ marginBottom: 20 }}>
          <div className="field"><label>Name</label><input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></div>
          <div className="field"><label>Price (Rs)</label><input type="number" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} required /></div>
          <div className="field">
            <label>Category</label>
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} required>
              <option value="">Select category</option>
              {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="field"><label>Description</label><textarea rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
          <button className="btn btn-primary btn-block" type="submit">Save</button>
        </form>
      )}

      {items.map((item) => (
        <div key={item.id} className="card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600 }}>{item.name}</div>
            <div style={{ fontSize: 12, color: "var(--gold)" }}>Rs {Number(item.price).toFixed(0)}</div>
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <button className={`btn ${item.is_available ? "btn-secondary" : "btn-primary"}`} style={{ padding: "6px 12px", fontSize: 11 }} onClick={() => toggleAvailable(item)}>
              {item.is_available ? "Available" : "Unavailable"}
            </button>
            <button onClick={() => remove(item.id)} aria-label="Delete item" style={{ background: "none", border: "none", color: "var(--maroon)" }}>
              <i className="ti ti-trash" style={{ fontSize: 16 }} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
