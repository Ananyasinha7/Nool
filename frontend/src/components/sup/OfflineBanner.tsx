import { useT } from "../../i18n/provider";
import { useOnline } from "../../lib/offline/useQueue";

/** A one-line strip, never a blocking modal (Doc2 S-7). */
export function OfflineBanner() {
  const t = useT();
  if (useOnline()) return null;
  return (
    <div className="bg-amber-bg px-4 py-2 text-[14px] text-amber-text md:px-6">
      <div className="mx-auto max-w-page">
        <p role="status">{t("net.offline")}</p>
      </div>
    </div>
  );
}
