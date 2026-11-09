import { useRegisterSW } from "virtual:pwa-register/react";
import { useLocation } from "react-router-dom";
import { useT } from "../../i18n/provider";

/** "New version ready. Reload": never reloads by itself, and stays hidden while an entry is being typed. */
export function UpdateToast() {
  const t = useT();
  const loc = useLocation();
  const { needRefresh: [need], updateServiceWorker } = useRegisterSW();
  if (!need || loc.pathname.startsWith("/s/update")) return null;
  return (
    <div role="status" className="toast-in fixed inset-x-0 bottom-0 z-50 mx-auto flex max-w-md md:max-w-xl items-center justify-between gap-4 bg-ink px-4 py-3 pb-[calc(12px+var(--safe-b))] text-paper md:rounded-t-md">
      <span>{t("sup.updateReady")}</span>
      <button className="min-h-[48px] font-semibold underline" onClick={() => void updateServiceWorker(true)}>{t("sup.reload")}</button>
    </div>
  );
}
