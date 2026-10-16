import { Flame } from "lucide-react";
import { FormEvent, useState } from "react";

import { Button, ErrorNote, Field, Input } from "../components/ui";
import { errorMessage } from "../lib/api";
import { useAuth } from "../lib/auth";

export default function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true); setError(null);
    try { await login(email, password); } catch (err) { setError(errorMessage(err)); } finally { setBusy(false); }
  };

  return (
    <div className="grid min-h-full lg:grid-cols-[1.1fr_1fr]">
      <div className="relative hidden flex-col justify-between bg-ink-900 p-12 text-white lg:flex">
        <div className="flex items-center gap-3"><Flame className="h-8 w-8 text-signal" /><span className="font-display text-3xl font-semibold">OilOps Pro</span></div>
        <div>
          <h1 className="max-w-md text-5xl font-semibold leading-[1.05]">Every pump, valve and tank, accounted for.</h1>
          <p className="mt-5 max-w-md text-lg" style={{ color: "#b9cdd0" }}>Maintenance, incidents, stock and live sensor alerts for refineries, gas plants and fuel stations in one control room.</p>
        </div>
        <div>
          <div className="hazard mb-4 h-3 w-48 rounded-sm" />
          <p className="text-sm" style={{ color: "#8fb0b5" }}>Demo accounts use the password OilOps@2026! — admin@oilops.com, manager@oilops.com, engineer@oilops.com, tech1@oilops.com</p>
        </div>
      </div>
      <div className="flex items-center justify-center p-6">
        <form onSubmit={submit} className="w-full max-w-sm space-y-4">
          <div>
            <h2 className="text-3xl font-semibold text-ink-900">Sign in</h2>
            <p className="mt-1 text-sm text-slate-600">Use your company email address.</p>
          </div>
          <Field label="Email"><Input type="email" required autoFocus autoComplete="username" value={email} onChange={(e) => setEmail(e.target.value)} /></Field>
          <Field label="Password"><Input type="password" required autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} /></Field>
          <ErrorNote message={error} />
          <Button type="submit" variant="primary" loading={busy} className="w-full py-2.5">Sign in</Button>
        </form>
      </div>
    </div>
  );
}
