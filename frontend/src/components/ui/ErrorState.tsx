import { useState } from "react";
import { useT } from "../../i18n/provider";
import { Button } from "./Button";

export function ErrorState({ message, detail, onRetry }: { message?: string; detail?: string; onRetry?: () => void }) {
  const t = useT();
  const [open, setOpen] = useState(false);
  return (
    <div role="alert" className="flex flex-col items-center gap-3 px-4 py-16 text-center">
      <p className="max-w-sm text-ink">{message ?? t("err.loadFailed")}</p>
      {onRetry && <Button variant="secondary" onClick={onRetry}>{t("common.retry")}</Button>}
      {detail && (
        <>
          <button className="text-[13px] text-ink-3 underline" onClick={() => setOpen(!open)}>{t("common.details")}</button>
          {open && <p className="max-w-sm break-words text-[13px] text-ink-3">{detail}</p>}
        </>
      )}
    </div>
  );
}
