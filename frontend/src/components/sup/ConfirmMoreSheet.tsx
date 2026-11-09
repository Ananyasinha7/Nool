import { useT } from "../../i18n/provider";
import { BottomSheet, Button } from "../ui";

/** BR-09: a single entry above the remaining quantity asks before sending. */
export function ConfirmMoreSheet({ open, remaining, onCancel, onConfirm }: { open: boolean; remaining: number; onCancel: () => void; onConfirm: () => void }) {
  const t = useT();
  return (
    <BottomSheet open={open} onClose={onCancel} title={t("sup.moreThanRemaining")}>
      <p className="mb-4 text-ink-2">{t("sup.needed")}: {remaining}</p>
      <div className="flex flex-col gap-3">
        <Button sup onClick={onConfirm}>{t("sup.sendAnyway")}</Button>
        <Button sup variant="secondary" onClick={onCancel}>{t("common.cancel")}</Button>
      </div>
    </BottomSheet>
  );
}
