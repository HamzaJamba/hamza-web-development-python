import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

export type Row = Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
export interface Page<T = Row> { count: number; next: string | null; previous: string | null; results: T[] }

const BASE = (import.meta.env.VITE_API_URL as string | undefined) || "/api/v1";
const ACCESS = "oilops.access";
const REFRESH = "oilops.refresh";

export const tokens = {
  get access() { return localStorage.getItem(ACCESS); },
  get refresh() { return localStorage.getItem(REFRESH); },
  set(access: string, refresh?: string) {
    localStorage.setItem(ACCESS, access);
    if (refresh) localStorage.setItem(REFRESH, refresh);
  },
  clear() { localStorage.removeItem(ACCESS); localStorage.removeItem(REFRESH); },
};

export const api = axios.create({ baseURL: BASE });

api.interceptors.request.use((cfg: InternalAxiosRequestConfig) => {
  if (tokens.access) cfg.headers.Authorization = `Bearer ${tokens.access}`;
  return cfg;
});

let refreshing: Promise<string> | null = null;
async function refreshAccess(): Promise<string> {
  if (!tokens.refresh) throw new Error("no refresh token");
  const r = await axios.post(`${BASE}/auth/refresh/`, { refresh: tokens.refresh });
  tokens.set(r.data.access, r.data.refresh);
  return r.data.access as string;
}

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    const isAuthCall = original?.url?.includes("/auth/login") || original?.url?.includes("/auth/refresh");
    if (error.response?.status === 401 && original && !original._retry && !isAuthCall && tokens.refresh) {
      original._retry = true;
      try {
        refreshing = refreshing ?? refreshAccess().finally(() => { refreshing = null; });
        const access = await refreshing;
        original.headers.Authorization = `Bearer ${access}`;
        return api(original);
      } catch {
        tokens.clear();
        window.dispatchEvent(new Event("oilops:logout"));
      }
    }
    return Promise.reject(error);
  },
);

/** Pull a readable message out of the API's {detail, errors} payload. */
export function errorMessage(e: unknown): string {
  const err = e as AxiosError<Row>;
  const d = err.response?.data;
  if (!d) return err.message || "Something went wrong.";
  if (d.errors && typeof d.errors === "object") {
    return Object.entries(d.errors).map(([k, v]) => `${k === "non_field_errors" ? "" : k + ": "}${Array.isArray(v) ? v.join(" ") : JSON.stringify(v)}`).join(" · ");
  }
  return (d.detail as string) || "Request failed.";
}

export function fieldErrors(e: unknown): Record<string, string> {
  const d = (e as AxiosError<Row>).response?.data?.errors;
  if (!d || typeof d !== "object") return {};
  return Object.fromEntries(Object.entries(d).map(([k, v]) => [k, Array.isArray(v) ? v.join(" ") : String(v)]));
}

export async function getList(endpoint: string, params: Row = {}): Promise<Row[]> {
  const r = await api.get(endpoint, { params: { page_size: 200, ...params } });
  return Array.isArray(r.data) ? r.data : r.data.results;
}

export async function download(url: string, params: Row, filename: string) {
  const r = await api.get(url, { params, responseType: "blob" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(r.data);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}
