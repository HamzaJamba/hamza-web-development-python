import { useQuery } from "@tanstack/react-query";
import {
  Activity, Bell, Boxes, ClipboardList, Factory, FileBarChart, Flame, Gauge as GaugeIcon, History, LayoutDashboard,
  LogOut, Menu, Settings2, ShieldAlert, Users, Wrench, X,
} from "lucide-react";
import { ReactNode, useEffect, useState } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";

import { api, Row } from "../lib/api";
import { Role, useAuth } from "../lib/auth";
import { ago, pretty } from "../lib/format";
import { cx } from "./ui";

const NAV: { to: string; label: string; icon: ReactNode; roles?: Role[] }[] = [
  { to: "/", label: "Dashboard", icon: <LayoutDashboard className="h-4 w-4" /> },
  { to: "/monitoring", label: "Live monitoring", icon: <Activity className="h-4 w-4" /> },
  { to: "/plants", label: "Plants & assets", icon: <Factory className="h-4 w-4" /> },
  { to: "/equipment", label: "Equipment", icon: <GaugeIcon className="h-4 w-4" /> },
  { to: "/work-orders", label: "Work orders", icon: <ClipboardList className="h-4 w-4" /> },
  { to: "/maintenance", label: "Maintenance plans", icon: <Wrench className="h-4 w-4" /> },
  { to: "/incidents", label: "Incidents", icon: <ShieldAlert className="h-4 w-4" /> },
  { to: "/inventory", label: "Inventory", icon: <Boxes className="h-4 w-4" /> },
  { to: "/employees", label: "People", icon: <Users className="h-4 w-4" />, roles: ["PLANT_MANAGER", "HR", "SAFETY_OFFICER", "ENGINEER"] },
  { to: "/reports", label: "Reports", icon: <FileBarChart className="h-4 w-4" />, roles: ["PLANT_MANAGER", "ENGINEER", "SAFETY_OFFICER", "HR"] },
  { to: "/users", label: "User accounts", icon: <Settings2 className="h-4 w-4" />, roles: ["ADMIN"] },
  { to: "/audit", label: "Audit log", icon: <History className="h-4 w-4" />, roles: ["ADMIN"] },
];

function Brand() {
  return (
    <div>
      <div className="hazard h-1.5" />
      <div className="flex items-center gap-2.5 px-5 py-4">
        <Flame className="h-6 w-6 text-signal" />
        <div>
          <p className="font-display text-xl font-semibold leading-none text-white">OilOps Pro</p>
          <p className="mt-1 text-xs text-ink-600" style={{ color: "#8fb0b5" }}>Operations control</p>
        </div>
      </div>
    </div>
  );
}

function NotificationBell() {
  const [open, setOpen] = useState(false);
  const count = useQuery({ queryKey: ["unread"], queryFn: async () => (await api.get("/notifications/unread-count/")).data.count as number, refetchInterval: 30_000 });
  const recent = useQuery({ queryKey: ["notif-recent"], enabled: open, queryFn: async () => (await api.get("/notifications/", { params: { page_size: 6 } })).data.results as Row[] });
  const loc = useLocation();
  useEffect(() => setOpen(false), [loc.pathname]);
  return (
    <div className="relative">
      <button onClick={() => setOpen((o) => !o)} aria-label={`Notifications, ${count.data ?? 0} unread`} className="relative rounded-md p-2 text-ink-800 hover:bg-ink-900/5">
        <Bell className="h-5 w-5" />
        {!!count.data && <span className="absolute -right-0.5 -top-0.5 min-w-4 rounded-full bg-signal px-1 text-center text-[10px] font-semibold leading-4 text-white">{count.data > 99 ? "99+" : count.data}</span>}
      </button>
      {open && (
        <div className="absolute right-0 z-40 mt-2 w-80 rounded-lg border border-line bg-white shadow-lg">
          <div className="max-h-96 overflow-y-auto">
            {recent.data?.length === 0 && <p className="p-4 text-sm text-slate-500">You're all caught up.</p>}
            {recent.data?.map((n) => (
              <Link key={n.id} to={n.link || "/notifications"} className="block border-b border-line px-4 py-3 last:border-0 hover:bg-paper">
                <p className={cx("text-sm", !n.is_read && "font-semibold")}>{n.title}</p>
                <p className="mt-0.5 text-xs text-slate-500">{pretty(n.kind)} · {ago(n.created_at)}</p>
              </Link>
            ))}
          </div>
          <Link to="/notifications" className="block border-t border-line px-4 py-2.5 text-center text-sm font-medium text-gauge hover:bg-paper">View all notifications</Link>
        </div>
      )}
    </div>
  );
}

export default function Layout() {
  const { user, logout, can } = useAuth();
  const [menu, setMenu] = useState(false);
  const loc = useLocation();
  useEffect(() => setMenu(false), [loc.pathname]);
  const items = NAV.filter((n) => !n.roles || can(...n.roles));

  const sidebar = (
    <div className="flex h-full flex-col bg-ink-900 text-white">
      <Brand />
      <nav className="flex-1 space-y-0.5 overflow-y-auto px-3 py-2" aria-label="Main">
        {items.map((n) => (
          <NavLink key={n.to} to={n.to} end={n.to === "/"}
            className={({ isActive }) => cx("flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors", isActive ? "bg-ink-700 text-white" : "text-[#b9cdd0] hover:bg-ink-800 hover:text-white")}>
            {n.icon}{n.label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-ink-700 p-4">
        <p className="truncate text-sm font-medium">{user?.full_name}</p>
        <p className="mb-3 text-xs" style={{ color: "#8fb0b5" }}>{pretty(user?.role)}</p>
        <button onClick={logout} className="flex items-center gap-2 text-sm text-[#b9cdd0] hover:text-white"><LogOut className="h-4 w-4" />Sign out</button>
      </div>
    </div>
  );

  return (
    <div className="flex h-full">
      <aside className="hidden w-64 shrink-0 lg:block">{sidebar}</aside>
      {menu && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-ink-950/60" onClick={() => setMenu(false)} />
          <div className="absolute inset-y-0 left-0 w-64">{sidebar}</div>
        </div>
      )}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-line bg-white px-4 py-2 lg:justify-end">
          <button className="rounded-md p-2 lg:hidden" onClick={() => setMenu((m) => !m)} aria-label="Toggle menu">{menu ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}</button>
          <NotificationBell />
        </header>
        <main className="flex-1 overflow-y-auto p-4 sm:p-6"><div className="mx-auto max-w-7xl"><Outlet /></div></main>
      </div>
    </div>
  );
}
