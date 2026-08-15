import { createContext, useContext, useState, useCallback } from "react";
import { decodeJwt } from "../api/jwt";
import * as authApi from "../api/auth";

const AuthContext = createContext(null);

function userFromToken(token) {
  if (!token) return null;
  const payload = decodeJwt(token);
  if (!payload) return null;
  return {
    id: payload.user_id,
    username: payload.username,
    role: payload.role,
    isApproved: payload.is_approved,
  };
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => userFromToken(localStorage.getItem("access_token")));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const login = useCallback(async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      const data = await authApi.login(username, password);
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      const nextUser = userFromToken(data.access);
      setUser(nextUser);
      return nextUser;
    } catch (e) {
      const msg = e.response?.data?.detail || "Login failed. Check your username and password.";
      setError(msg);
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    try {
      return await authApi.register(payload);
    } catch (e) {
      const msg = e.response?.data ? Object.values(e.response.data).flat().join(" ") : "Registration failed.";
      setError(msg);
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    const refresh = localStorage.getItem("refresh_token");
    try {
      if (refresh) await authApi.logout(refresh);
    } catch {
      // ignore — clearing local tokens still logs the user out client-side
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
