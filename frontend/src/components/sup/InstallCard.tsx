import { useEffect, useState } from "react";
import { useT } from "../../i18n/provider";
import { useQueue } from "../../lib/offline/useQueue";
import { Button } from "../ui";

interface BIPEvent extends Event { prompt: () => Promise<void> }
const KEY = "nool.installDismissed";
let deferred: BIPEvent | null = null;
if (typeof window !== "undefined") window.addEventListener("beforeinstallprompt", (e) => { e.preventDefault(); deferred = e as BIPEvent; });

/** One-time, dismissible card after the first successful send (Doc2 section 7). */
export function InstallCard() {
  const t = useT();
  const { items } = useQueue();
  const [dismissed, setDismissed] = useState(() => { try { return localStorage.getItem(KEY) === "1"; } catch { return false; } });
  const [, force] = useState(0);
  useEffect(() => { const f = () => force((x) => x + 1); window.addEventListener("beforeinstallprompt", f); return () => window.removeEventListener("beforeinstallprompt", f); }, []);
  const standalone = window.matchMedia?.("(display-mode: standalone)").matches;
  const ios = /iphone|ipad|ipod/i.test(navigator.userAgent);
  if (dismissed || standalone || !items.some((i) => i.state === "SENT") || (!deferred && !ios)) return null;
  const dismiss = () => { try { localStorage.setItem(KEY, "1"); } catch { /* ignore */ } setDismissed(true); };
  return (
    <div className="flex flex-col gap-3 rounded-md border border-field bg-surface p-4">
      <p className="font-semibold">{t("sup.installTitle")}</p>
      {deferred ? <Button sup onClick={async () => { await deferred?.prompt(); dismiss(); }}>{t("sup.installBtn")}</Button> : <p className="text-ink-2">{t("sup.iosInstall")}</p>}
      <button className="min-h-[48px] self-start text-ink-2 underline" onClick={dismiss}>{t("sup.installLater")}</button>
    </div>
  );
}
