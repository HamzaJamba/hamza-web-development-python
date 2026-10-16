import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowDownUp } from "lucide-react";
import { FormEvent, useState } from "react";

import ResourcePage from "../components/ResourcePage";
import { Badge, Button, ErrorNote, Field, Input, Modal, Select, Tabs, PageHeader } from "../components/ui";
import { api, errorMessage, Row } from "../lib/api";
import { useAuth } from "../lib/auth";
import { dateTime, money, num } from "../lib/format";
import { ITEM_CATEGORIES, opts, plantOption } from "../lib/options";

export default function Inventory() {
  const { can } = useAuth();
  const qc = useQueryClient();
  const [tab, setTab] = useState<"items" | "low" | "movements">("items");
  const [adj, setAdj] = useState<Row | null>(null);
  const [f, setF] = useState<Row>({ movement_type: "IN", quantity: "" });
  const [err, setErr] = useState<string | null>(null);
  const write = can("STORE_KEEPER", "PLANT_MANAGER");
  const m = useMutation({ mutationFn: () => api.post(`/inventory/${adj!.id}/adjust/`, f), onSuccess: () => { setAdj(null); qc.invalidateQueries({ queryKey: ["res"] }); }, onError: (e) => setErr(errorMessage(e)) });
  const submit = (e: FormEvent) => { e.preventDefault(); setErr(null); m.mutate(); };

  const columns = [
    { key: "sku", label: "SKU" }, { key: "name", label: "Item" }, { key: "category_display", label: "Category" },
    { key: "quantity", label: "In stock", render: (r: Row) => <span className={r.is_low ? "font-semibold text-crit" : ""}>{num(r.quantity, 2)} {r.unit}</span> },
    { key: "reorder_level", label: "Reorder at", render: (r: Row) => num(r.reorder_level, 2) },
    { key: "is_low", label: "Stock", render: (r: Row) => <Badge value={r.is_low ? "WARNING" : "OK"} tone={r.is_low ? "crit" : "ok"} label={r.is_low ? "Low" : "OK"} /> },
    { key: "stock_value", label: "Value", render: (r: Row) => money(r.stock_value) }, { key: "location", label: "Location" }];

  return (
    <div>
      <PageHeader title="Inventory" subtitle="Spare parts, chemicals, lubricants and safety equipment. Stock changes only through recorded movements." />
      <Tabs value={tab} onChange={setTab} tabs={[{ id: "items", label: "All items" }, { id: "low", label: "Low stock" }, { id: "movements", label: "Movement history" }]} />
      {tab !== "movements" ? (
        <ResourcePage key={tab} embedded noun="item" endpoint={tab === "low" ? "/inventory/low-stock/" : "/inventory/"} canWrite={write && tab === "items"} canDelete={write && tab === "items"} searchable={tab === "items"}
          filters={[{ name: "category", label: "Category", options: opts(ITEM_CATEGORIES) }]} columns={columns}
          rowActions={(r) => (can("STORE_KEEPER", "PLANT_MANAGER", "ENGINEER") && (tab === "items" || r.is_low)) ? <Button variant="ghost" onClick={() => { setAdj(r); setErr(null); setF({ movement_type: "IN", quantity: "" }); }}><ArrowDownUp className="h-4 w-4" />Adjust</Button> : null}
          fields={[{ name: "sku", label: "SKU", required: true }, { name: "name", label: "Name", required: true }, { name: "category", label: "Category", type: "select", options: opts(ITEM_CATEGORIES), required: true },
            { name: "unit", label: "Unit", required: true }, { name: "quantity", label: "Opening quantity", type: "number", step: "0.01", createOnly: true, hint: "After creation, use Adjust to change stock." },
            { name: "reorder_level", label: "Reorder level", type: "number", step: "0.01" }, { name: "unit_cost", label: "Unit cost", type: "number", step: "0.01" },
            { name: "plant", label: "Plant", type: "select", optionsFrom: plantOption }, { name: "location", label: "Bin / location" }, { name: "supplier", label: "Supplier" },
            { name: "is_active", label: "Active", type: "checkbox" }]}
          defaults={{ unit: "pcs", category: "SPARE_PART", quantity: 0, reorder_level: 0, unit_cost: 0, is_active: true }} />
      ) : (
        <ResourcePage embedded noun="movement" endpoint="/inventory/movements/" filters={[{ name: "movement_type", label: "Type", options: opts(["IN", "OUT", "ADJUST"]) }]}
          columns={[{ key: "created_at", label: "When", render: (r) => dateTime(r.created_at) }, { key: "item_sku", label: "SKU" }, { key: "item_name", label: "Item" },
            { key: "movement_type", label: "Type", render: (r) => <Badge value={r.movement_type} tone={r.movement_type === "OUT" ? "warn" : r.movement_type === "IN" ? "ok" : "info"} /> },
            { key: "quantity", label: "Qty" }, { key: "balance_after", label: "Balance" }, { key: "reference", label: "Reference" }, { key: "user_name", label: "By" }]} />
      )}
      {adj && (
        <Modal title={`Adjust stock: ${adj.name}`} onClose={() => setAdj(null)}>
          <form onSubmit={submit} className="space-y-4">
            <p className="text-sm text-slate-600">Currently {num(adj.quantity, 2)} {adj.unit}.</p>
            <Field label="Movement"><Select value={f.movement_type} onChange={(e) => setF({ ...f, movement_type: e.target.value })}><option value="IN">Stock in (receive)</option><option value="OUT">Stock out (issue)</option><option value="ADJUST">Set level (cycle count)</option></Select></Field>
            <Field label={f.movement_type === "ADJUST" ? "New quantity *" : "Quantity *"}><Input type="number" step="0.01" min="0" required value={f.quantity} onChange={(e) => setF({ ...f, quantity: e.target.value })} /></Field>
            <Field label="Reference"><Input value={f.reference ?? ""} onChange={(e) => setF({ ...f, reference: e.target.value })} placeholder="PO number, work order, count sheet…" /></Field>
            <ErrorNote message={err} /><div className="flex justify-end gap-2"><Button type="button" onClick={() => setAdj(null)}>Cancel</Button><Button type="submit" variant="primary" loading={m.isPending}>Record movement</Button></div>
          </form>
        </Modal>
      )}
    </div>
  );
}
