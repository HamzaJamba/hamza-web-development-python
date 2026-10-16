import { Loader2, X } from "lucide-react";
import { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes, useEffect } from "react";

import { pretty } from "../lib/format";

export const cx = (...a: (string | false | null | undefined)[]) => a.filter(Boolean).join(" ");

type Variant = "primary" | "secondary" | "ghost" | "danger";
const variants: Record<Variant, string> = {
  primary: "bg-signal text-white hover:bg-signal-dark",
  secondary: "bg-white text-ink-900 border border-line hover:bg-paper",
  ghost: "text-ink-700 hover:bg-ink-900/5",
  danger: "bg-crit text-white hover:bg-red-800",
};
export function Button({ variant = "secondary", loading, className, children, disabled, ...p }:
  ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; loading?: boolean }) {
  return (
    <button {...p} disabled={disabled || loading}
      className={cx("inline-flex items-center justify-center gap-2 rounded-md px-3.5 py-2 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed", variants[variant], className)}>
      {loading && <Loader2 className="h-4 w-4 animate-spin" />}
      {children}
    </button>
  );
}

const TONES: Record<string, string> = {
  crit: "bg-red-100 text-red-800 ring-red-200", warn: "bg-amber-100 text-amber-800 ring-amber-200",
  ok: "bg-emerald-100 text-emerald-800 ring-emerald-200", info: "bg-sky-100 text-sky-800 ring-sky-200",
  neutral: "bg-slate-100 text-slate-700 ring-slate-200",
};
export function toneOf(v: string): string {
  if (["CRITICAL", "FAULTY", "CATASTROPHIC", "SHUTDOWN", "OUT_OF_SERVICE", "OPEN", "REPORTED", "LOGIN_FAILED"].includes(v)) return "crit";
  if (["HIGH", "MAJOR", "WARNING", "MAINTENANCE", "ON_HOLD", "OFFLINE", "INSPECTION", "MODERATE", "ON_LEAVE", "IDLE"].includes(v)) return "warn";
  if (["OPERATIONAL", "COMPLETED", "RESOLVED", "CLOSED", "NORMAL", "ACTIVE", "IN_SERVICE", "LOW", "MINOR", "SENT"].includes(v)) return "ok";
  if (["IN_PROGRESS", "ASSIGNED", "INVESTIGATING", "ACKNOWLEDGED", "MEDIUM", "PREVENTIVE"].includes(v)) return "info";
  return "neutral";
}
export function Badge({ value, tone, label }: { value: string; tone?: string; label?: string }) {
  return <span className={cx("inline-flex items-center whitespace-nowrap rounded px-2 py-0.5 text-xs font-medium ring-1 ring-inset", TONES[tone ?? toneOf(value)])}>{label ?? pretty(value)}</span>;
}

export function Card({ title, action, children, className, pad = true }:
  { title?: ReactNode; action?: ReactNode; children: ReactNode; className?: string; pad?: boolean }) {
  return (
    <section className={cx("rounded-lg border border-line bg-white", className)}>
      {(title || action) && (
        <header className="flex items-center justify-between gap-3 border-b border-line px-4 py-3">
          <h2 className="text-lg font-semibold text-ink-900">{title}</h2>{action}
        </header>
      )}
      <div className={pad ? "p-4" : ""}>{children}</div>
    </section>
  );
}

export function PageHeader({ title, subtitle, actions }: { title: string; subtitle?: string; actions?: ReactNode }) {
  return (
    <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-3xl font-semibold text-ink-900">{title}</h1>
        {subtitle && <p className="mt-0.5 max-w-2xl text-sm text-slate-600">{subtitle}</p>}
      </div>
      <div className="flex flex-wrap gap-2">{actions}</div>
    </div>
  );
}

export function Spinner({ label = "Loading" }: { label?: string }) {
  return <div role="status" className="flex items-center justify-center gap-2 py-10 text-sm text-slate-500"><Loader2 className="h-4 w-4 animate-spin" />{label}…</div>;
}

export function Empty({ title, hint }: { title: string; hint?: string }) {
  return <div className="py-10 text-center"><p className="font-medium text-ink-800">{title}</p>{hint && <p className="mt-1 text-sm text-slate-500">{hint}</p>}</div>;
}

export function ErrorNote({ message }: { message?: string | null }) {
  if (!message) return null;
  return <div role="alert" className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{message}</div>;
}

export function Stat({ label, value, hint, tone }: { label: string; value: ReactNode; hint?: string; tone?: "crit" | "warn" | "ok" }) {
  const bar = tone === "crit" ? "bg-crit" : tone === "warn" ? "bg-warn" : tone === "ok" ? "bg-ok" : "bg-gauge";
  return (
    <div className="relative overflow-hidden rounded-lg border border-line bg-white p-4 pl-5">
      <span className={cx("absolute inset-y-0 left-0 w-1.5", bar)} />
      <p className="text-sm text-slate-600">{label}</p>
      <p className="mt-1 font-display text-3xl font-semibold text-ink-900">{value}</p>
      {hint && <p className="mt-0.5 text-xs text-slate-500">{hint}</p>}
    </div>
  );
}

export function Gauge({ value, size = 96, label }: { value: number; size?: number; label?: string }) {
  const r = size / 2 - 8, c = 2 * Math.PI * r;
  const color = value >= 80 ? "var(--color-ok)" : value >= 50 ? "var(--color-warn)" : "var(--color-crit)";
  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }} role="img" aria-label={`${label ?? "Value"} ${value}%`}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#e3e8e9" strokeWidth="8" />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth="8" strokeLinecap="round"
          strokeDasharray={c} strokeDashoffset={c * (1 - Math.min(100, Math.max(0, value)) / 100)} />
      </svg>
      <span className="absolute font-display text-xl font-semibold text-ink-900">{Math.round(value)}</span>
    </div>
  );
}

export function Modal({ title, onClose, children, wide }: { title: string; onClose: () => void; children: ReactNode; wide?: boolean }) {
  useEffect(() => {
    const h = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [onClose]);
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-ink-950/60 p-4 sm:p-8" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div role="dialog" aria-modal="true" aria-label={title} className={cx("w-full rounded-lg bg-white shadow-xl", wide ? "max-w-3xl" : "max-w-lg")}>
        <header className="flex items-center justify-between border-b border-line px-5 py-3">
          <h2 className="text-xl font-semibold text-ink-900">{title}</h2>
          <button onClick={onClose} aria-label="Close" className="rounded p-1 text-slate-500 hover:bg-paper"><X className="h-5 w-5" /></button>
        </header>
        <div className="p-5">{children}</div>
      </div>
    </div>
  );
}

const input = "w-full rounded-md border border-line bg-white px-3 py-2 text-sm text-ink-900 placeholder:text-slate-400 focus:border-gauge focus:outline-none";
export function Field({ label, error, hint, children, full }: { label: string; error?: string; hint?: string; children: ReactNode; full?: boolean }) {
  return (
    <label className={cx("block", full && "sm:col-span-2")}>
      <span className="mb-1 block text-sm font-medium text-ink-800">{label}</span>
      {children}
      {hint && !error && <span className="mt-1 block text-xs text-slate-500">{hint}</span>}
      {error && <span className="mt-1 block text-xs text-crit">{error}</span>}
    </label>
  );
}
export const Input = (p: InputHTMLAttributes<HTMLInputElement>) => <input {...p} className={cx(input, p.className)} />;
export const Textarea = (p: TextareaHTMLAttributes<HTMLTextAreaElement>) => <textarea rows={3} {...p} className={cx(input, p.className)} />;
export const Select = ({ children, ...p }: SelectHTMLAttributes<HTMLSelectElement>) => <select {...p} className={cx(input, p.className)}>{children}</select>;

export function Tabs<T extends string>({ tabs, value, onChange }: { tabs: { id: T; label: string }[]; value: T; onChange: (t: T) => void }) {
  return (
    <div role="tablist" className="mb-4 flex flex-wrap gap-1 border-b border-line">
      {tabs.map((t) => (
        <button key={t.id} role="tab" aria-selected={value === t.id} onClick={() => onChange(t.id)}
          className={cx("-mb-px border-b-2 px-3.5 py-2 text-sm font-medium", value === t.id ? "border-signal text-ink-900" : "border-transparent text-slate-500 hover:text-ink-800")}>
          {t.label}
        </button>
      ))}
    </div>
  );
}
