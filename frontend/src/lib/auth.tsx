import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api, ApiException } from "../api/client";
import type { MeOut } from "../api/types";
import { useI18n } from "../i18n/provider";
import { getCachedMe, setCachedMe } from "./session";

interface AuthCtx {
  me: MeOut | null;
  loading: boolean;
  signIn: (u: string, p: string) => Promise<MeOut>;
  signOut: () => Promise<void>;
  refresh: () => Promise<void>;
}
const Ctx = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { setLang } = useI18n();
  const [me, setMe] = useState<MeOut | null>(() => getCachedMe());
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const fresh = await api.me();
      setMe(fresh); setCachedMe(fresh);
    } catch (e) {
      // Offline: trust the cached user so supervisors can still open the app (the queue keeps working).
      if (e instanceof ApiException && e.code === "NETWORK") return;
      setMe(null); setCachedMe(null);
    } finally { setLoading(false); }
  }, []);
  useEffect(() => { void refresh(); }, [refresh]);

  const signIn = useCallback(async (u: string, p: string) => {
    const m = await api.login(u, p);
    setMe(m); setCachedMe(m);
    setLang(m.lang, false); // role default (Tamil for supervisors, English for merchandisers), no write-back
    return m;
  }, [setLang]);

  const signOut = useCallback(async () => {
    try { await api.logout(); } catch { /* offline: still clear the local copy */ }
    setMe(null); setCachedMe(null);
  }, []);

  const value = useMemo(() => ({ me, loading, signIn, signOut, refresh }), [me, loading, signIn, signOut, refresh]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAuth(): AuthCtx {
  const c = useContext(Ctx);
  if (!c) throw new Error("AuthProvider missing");
  return c;
}
