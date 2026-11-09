import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api } from "../api/client";
import { getCachedMe, getStoredLang, setStoredLang } from "../lib/session";
import { translate, type Lang } from "./t";

interface Ctx { lang: Lang; setLang: (l: Lang, persist?: boolean) => void; t: (key: string, params?: Record<string, string | number>) => string }
const I18nContext = createContext<Ctx | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => getStoredLang() ?? getCachedMe()?.lang ?? "en");
  useEffect(() => { document.documentElement.lang = lang; }, [lang]);
  const setLang = useCallback((l: Lang, persist = true) => {
    setLangState(l);
    setStoredLang(l);
    // The toggle persists per user (Doc2 section 8); a failure (offline, buyer) is harmless.
    if (persist && getCachedMe()?.role && getCachedMe()?.role !== "BUYER") void api.setLang(l).catch(() => undefined);
  }, []);
  const t = useCallback((key: string, params?: Record<string, string | number>) => translate(lang, key, params), [lang]);
  const value = useMemo(() => ({ lang, setLang, t }), [lang, setLang, t]);
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): Ctx {
  const c = useContext(I18nContext);
  if (!c) throw new Error("I18nProvider missing");
  return c;
}
export const useT = () => useI18n().t;
