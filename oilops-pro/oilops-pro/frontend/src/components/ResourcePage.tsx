import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, Pencil, Plus, Search, Trash2 } from "lucide-react";
import { FormEvent, ReactNode, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api, errorMessage, fieldErrors, getList, Row } from "../lib/api";
import { toLocalInput } from "../lib/format";
import { Button, Card, Empty, ErrorNote, Field, Input, Modal, PageHeader, Select, Spinner, Textarea } from "./ui";

export interface FieldDef {
  name: string; label: string;
  type?: "text" | "email" | "number" | "date" | "datetime-local" | "time" | "textarea" | "select" | "multiselect" | "checkbox" | "password";
  options?: { value: string; label: string }[];
  optionsFrom?: { endpoint: string; label: (r: Row) => string; params?: Row };
  required?: boolean; step?: string; full?: boolean; hint?: string; createOnly?: boolean; editOnly?: boolean;
}
export interface ColumnDef { key: string; label: string; render?: (r: Row) => ReactNode; className?: string }
export interface FilterDef { name: string; label: string; options: { value: string; label: string }[] }

interface Props {
  title?: string; subtitle?: string; endpoint: string; columns: ColumnDef[]; fields?: FieldDef[]; filters?: FilterDef[];
  canWrite?: boolean; canDelete?: boolean; rowLink?: (r: Row) => string; rowActions?: (r: Row, refresh: () => void) => ReactNode;
  headerActions?: ReactNode; embedded?: boolean; defaultParams?: Row; searchable?: boolean; defaults?: Row; noun?: string; refetchMs?: number;
}

function SelectField({ f, value, onChange }: { f: FieldDef; value: unknown; onChange: (v: unknown) => void }) {
  const q = useQuery({ queryKey: ["options", f.optionsFrom?.endpoint, f.optionsFrom?.params], enabled: !!f.optionsFrom,
    queryFn: () => getList(f.optionsFrom!.endpoint, f.optionsFrom!.params), staleTime: 60_000 });
  const opts = f.options ?? (q.data ?? []).map((r) => ({ value: String(r.id), label: f.optionsFrom!.label(r) }));
  if (f.type === "multiselect") {
    const sel = (value as (string | number)[] | undefined)?.map(String) ?? [];
    return (
      <select multiple value={sel} className="h-28 w-full rounded-md border border-line bg-white px-2 py-1 text-sm"
        onChange={(e) => onChange(Array.from(e.target.selectedOptions).map((o) => Number(o.value)))}>
        {opts.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    );
  }
  return (
    <Select value={value === null || value === undefined ? "" : String(value)} onChange={(e) => onChange(e.target.value === "" ? null : e.target.value)} required={f.required}>
      <option value="">{f.required ? "Select…" : "— none —"}</option>
      {opts.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
    </Select>
  );
}

function FormModal({ title, fields, initial, onClose, onSubmit, saving, error, errs }:
  { title: string; fields: FieldDef[]; initial: Row; onClose: () => void; onSubmit: (v: Row) => void; saving: boolean; error: string | null; errs: Record<string, string> }) {
  const [v, setV] = useState<Row>(initial);
  const set = (k: string, val: unknown) => setV((p) => ({ ...p, [k]: val }));
  const submit = (e: FormEvent) => { e.preventDefault(); onSubmit(v); };
  return (
    <Modal title={title} onClose={onClose} wide>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          {fields.map((f) => (
            <Field key={f.name} label={f.label + (f.required ? " *" : "")} error={errs[f.name]} hint={f.hint} full={f.full || f.type === "textarea"}>
              {f.type === "textarea" ? <Textarea value={v[f.name] ?? ""} onChange={(e) => set(f.name, e.target.value)} required={f.required} />
                : f.type === "select" || f.type === "multiselect" ? <SelectField f={f} value={v[f.name]} onChange={(x) => set(f.name, x)} />
                : f.type === "checkbox" ? <input type="checkbox" className="h-5 w-5" checked={!!v[f.name]} onChange={(e) => set(f.name, e.target.checked)} />
                : <Input type={f.type ?? "text"} step={f.step} value={v[f.name] ?? ""} required={f.required} onChange={(e) => set(f.name, e.target.value)} autoComplete="off" />}
            </Field>
          ))}
        </div>
        <ErrorNote message={error} />
        <div className="flex justify-end gap-2">
          <Button type="button" onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="primary" loading={saving}>Save</Button>
        </div>
      </form>
    </Modal>
  );
}

export default function ResourcePage(p: Props) {
  const qc = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [q, setQ] = useState("");
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [editing, setEditing] = useState<Row | "new" | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [errs, setErrs] = useState<Record<string, string>>({});
  const key = ["res", p.endpoint, page, q, filters, p.defaultParams];

  useEffect(() => { const t = setTimeout(() => { setQ(search); setPage(1); }, 300); return () => clearTimeout(t); }, [search]);

  const list = useQuery({ queryKey: key, refetchInterval: p.refetchMs, placeholderData: (prev) => prev, queryFn: async () => {
    const params: Row = { page, ...p.defaultParams };
    if (q) params.search = q;
    Object.entries(filters).forEach(([k, val]) => val && (params[k] = val));
    return (await api.get(p.endpoint, { params })).data as { count: number; results: Row[] } | Row[];
  } });
  const rows: Row[] = Array.isArray(list.data) ? list.data : list.data?.results ?? [];
  const count = Array.isArray(list.data) ? rows.length : list.data?.count ?? 0;
  const pages = Math.max(1, Math.ceil(count / 20));
  const refresh = () => qc.invalidateQueries({ queryKey: ["res", p.endpoint] });

  const save = useMutation({
    mutationFn: async (v: Row) => {
      const body: Row = {};
      for (const f of p.fields ?? []) {
        if ((editing === "new" && f.editOnly) || (editing !== "new" && f.createOnly)) continue;
        let val = v[f.name];
        if (f.type === "datetime-local" && val) val = new Date(val).toISOString();
        if (val === "" && f.type !== "text" && f.type !== "textarea" && f.type !== "email") val = null;
        if (f.type === "password" && !val) continue;
        body[f.name] = val;
      }
      return editing === "new" ? api.post(p.endpoint, body) : api.patch(`${p.endpoint}${(editing as Row).id}/`, body);
    },
    onSuccess: () => { setEditing(null); refresh(); },
    onError: (e) => { setErr(errorMessage(e)); setErrs(fieldErrors(e)); },
  });
  const del = useMutation({ mutationFn: (id: number) => api.delete(`${p.endpoint}${id}/`), onSuccess: refresh, onError: (e) => alert(errorMessage(e)) });

  const initial = (): Row => {
    if (editing === "new") return { ...p.defaults };
    const r: Row = { ...(editing as Row) };
    for (const f of p.fields ?? []) if (f.type === "datetime-local") r[f.name] = toLocalInput(r[f.name]);
    return r;
  };
  const showActions = p.canWrite || p.canDelete || p.rowActions;
  const body = (
    <>
      <div className="mb-3 flex flex-wrap items-end gap-3">
        {p.searchable !== false && (
          <div className="relative min-w-52 flex-1 sm:max-w-xs">
            <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <Input aria-label="Search" placeholder="Search…" value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" />
          </div>
        )}
        {p.filters?.map((f) => (
          <Select key={f.name} aria-label={f.label} className="w-auto" value={filters[f.name] ?? ""} onChange={(e) => { setFilters((s) => ({ ...s, [f.name]: e.target.value })); setPage(1); }}>
            <option value="">{f.label}: all</option>
            {f.options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
          </Select>
        ))}
      </div>
      <div className="overflow-x-auto rounded-lg border border-line bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-line bg-paper text-slate-600">
            <tr>{p.columns.map((c) => <th key={c.key} className="whitespace-nowrap px-4 py-2.5 font-medium">{c.label}</th>)}{showActions && <th className="px-4 py-2.5" />}</tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-b border-line last:border-0 hover:bg-paper/60">
                {p.columns.map((c, i) => {
                  const content = c.render ? c.render(r) : r[c.key] ?? "—";
                  return <td key={c.key} className={`px-4 py-2.5 ${c.className ?? ""}`}>{i === 0 && p.rowLink ? <Link className="font-medium text-gauge hover:underline" to={p.rowLink(r)}>{content}</Link> : content}</td>;
                })}
                {showActions && (
                  <td className="whitespace-nowrap px-4 py-2 text-right">
                    <div className="flex items-center justify-end gap-1">
                      {p.rowActions?.(r, refresh)}
                      {p.canWrite && p.fields && <button aria-label="Edit" onClick={() => { setErr(null); setErrs({}); setEditing(r); }} className="rounded p-1.5 text-slate-500 hover:bg-ink-900/5"><Pencil className="h-4 w-4" /></button>}
                      {p.canDelete && <button aria-label="Delete" onClick={() => confirm("Delete this record? This cannot be undone.") && del.mutate(r.id)} className="rounded p-1.5 text-crit hover:bg-red-50"><Trash2 className="h-4 w-4" /></button>}
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
        {list.isLoading && <Spinner />}
        {list.isError && <div className="p-4"><ErrorNote message={errorMessage(list.error)} /></div>}
        {!list.isLoading && !list.isError && rows.length === 0 && <Empty title={`No ${p.noun ?? "records"} found`} hint={p.canWrite ? "Use the button above to add the first one." : "Try different filters."} />}
      </div>
      <div className="mt-3 flex items-center justify-between text-sm text-slate-600">
        <span>{count} {count === 1 ? "record" : "records"}</span>
        <div className="flex items-center gap-1">
          <Button variant="ghost" disabled={page <= 1} onClick={() => setPage((x) => x - 1)} aria-label="Previous page"><ChevronLeft className="h-4 w-4" /></Button>
          <span>Page {page} of {pages}</span>
          <Button variant="ghost" disabled={page >= pages} onClick={() => setPage((x) => x + 1)} aria-label="Next page"><ChevronRight className="h-4 w-4" /></Button>
        </div>
      </div>
      {editing && p.fields && (
        <FormModal title={editing === "new" ? `New ${p.noun ?? "record"}` : `Edit ${p.noun ?? "record"}`}
          fields={p.fields.filter((f) => (editing === "new" ? !f.editOnly : !f.createOnly))} initial={initial()}
          onClose={() => setEditing(null)} onSubmit={(v) => { setErr(null); setErrs({}); save.mutate(v); }} saving={save.isPending} error={err} errs={errs} />
      )}
    </>
  );
  const add = p.canWrite && p.fields ? <Button variant="primary" onClick={() => { setErr(null); setErrs({}); setEditing("new"); }}><Plus className="h-4 w-4" />Add {p.noun ?? "record"}</Button> : null;
  if (p.embedded) return <div><div className="mb-3 flex justify-end gap-2">{p.headerActions}{add}</div>{body}</div>;
  return <div><PageHeader title={p.title ?? ""} subtitle={p.subtitle} actions={<>{p.headerActions}{add}</>} />{body}</div>;
}

export { Card };
