import { createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { api, Row, tokens } from "./api";

export type Role = "ADMIN" | "PLANT_MANAGER" | "ENGINEER" | "TECHNICIAN" | "SAFETY_OFFICER" | "STORE_KEEPER" | "HR" | "VIEWER";
export interface User { id: number; email: string; full_name: string; first_name: string; role: Role }

interface AuthCtx {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  can: (...roles: Role[]) => boolean;
}
const Ctx = createContext<AuthCtx>(null as unknown as AuthCtx);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(!!tokens.access);

  useEffect(() => {
    if (!tokens.access) return;
    api.get("/auth/me/").then((r) => setUser(r.data)).catch(() => tokens.clear()).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const out = () => setUser(null);
    window.addEventListener("oilops:logout", out);
    return () => window.removeEventListener("oilops:logout", out);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const r = await api.post("/auth/login/", { email, password });
    tokens.set(r.data.access, r.data.refresh);
    setUser(r.data.user as Row as User);
  }, []);

  const logout = useCallback(async () => {
    try { await api.post("/auth/logout/", { refresh: tokens.refresh }); } catch { /* token may already be invalid */ }
    tokens.clear();
    setUser(null);
  }, []);

  const can = useCallback((...roles: Role[]) => !!user && (user.role === "ADMIN" || roles.includes(user.role)), [user]);
  const value = useMemo(() => ({ user, loading, login, logout, can }), [user, loading, login, logout, can]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
