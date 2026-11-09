import { useState, type FormEvent } from "react";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { api, ApiException } from "../../api/client";
import { useT } from "../../i18n/provider";
import { useAuth } from "../../lib/auth";
import { homeFor } from "../../components/shell/RequireRole";
import { Button, LangToggle, TextInput, Wordmark } from "../../components/ui";

const SHOW_DEMO = import.meta.env.DEV || import.meta.env.VITE_DEMO_LOGINS === "true";
const DEMO = [
  { u: "priya.merch", p: "Nool@Demo2026", label: "Priya (merchandiser)" },
  { u: "murugan.u1", p: "246810", label: "Murugan (Unit 1 supervisor)" },
  { u: "selvi.u2", p: "246810", label: "Selvi (Unit 2 supervisor)" },
];

export default function LoginPage() {
  const t = useT();
  const nav = useNavigate();
  const { me, signIn, refresh } = useAuth();
  const [params] = useSearchParams();
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (me) {
    const back = params.get("returnTo");
    return <Navigate to={back && back.startsWith("/") && !back.startsWith("//") ? back : homeFor(me.role)} replace />;
  }

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true); setErr(null);
    try { await signIn(u.trim(), p); }
    catch (x) {
      if (x instanceof ApiException && x.code === "RATE_LIMITED") setErr(x.message); // carries the minutes remaining
      else if (x instanceof ApiException && x.code === "NETWORK") setErr(t("err.network"));
      else setErr(t("err.badLogin"));
    } finally { setBusy(false); }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 py-10">
      <div className="absolute right-4 top-4 pt-[var(--safe-t)]"><LangToggle /></div>
      <div className="w-full max-w-sm rounded-xl border border-line bg-surface p-7 shadow-sm">
        <div className="mb-2"><Wordmark tamil /></div>
        <p className="mb-6 text-ink-2">{t("auth.tagline")}</p>
        <form onSubmit={submit} className="flex flex-col gap-4" noValidate>
          <TextInput label={t("auth.username")} value={u} onChange={(e) => setU(e.target.value)} autoComplete="username" autoCapitalize="none" required />
          <TextInput label={t("auth.pin")} type="password" value={p} onChange={(e) => setP(e.target.value)} autoComplete="current-password" required error={err} />
          <Button type="submit" loading={busy} disabled={!u || !p}>{busy ? t("auth.signingIn") : t("auth.signIn")}</Button>
        </form>
        {SHOW_DEMO && (
          <details className="mt-6 text-[13px] text-ink-2">
            <summary className="cursor-pointer">{t("auth.demoLogins")}</summary>
            <ul className="mt-2 flex flex-col gap-1">
              {DEMO.map((d) => (
                <li key={d.u} className="flex items-center justify-between gap-2">
                  <span>{d.label}</span>
                  <button className="underline" onClick={() => { setU(d.u); setP(d.p); }}>{t("auth.useThis")}</button>
                </li>
              ))}
              <li key="buyer" className="flex items-center justify-between gap-2 border-t border-line pt-2 mt-1">
                <span>Hannah (Company B buyer)</span>
                <button
                  type="button"
                  className="underline hover:text-ink cursor-pointer"
                  onClick={async () => {
                    setBusy(true);
                    try {
                      await api.buyerSession("demo-b-0001");
                      await refresh();
                      nav("/b", { replace: true });
                    } catch {
                      window.location.assign("/b/demo-b-0001");
                    } finally {
                      setBusy(false);
                    }
                  }}
                >
                  {t("auth.useThis")}
                </button>
              </li>
            </ul>
          </details>
        )}
      </div>
    </div>
  );
}
