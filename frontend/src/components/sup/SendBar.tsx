import { useT } from "../../i18n/provider";
import { Button } from "../ui";

/** Pinned, full width, 56 px, a single short word. Turns into a check for 400 ms once saved locally. */
export function SendBar({ onSend, disabled, done }: { onSend: () => void; disabled: boolean; done: boolean }) {
  const t = useT();
  return (
    <div className="sticky bottom-0 border-t border-line bg-paper px-4 pb-[calc(12px+var(--safe-b))] pt-3 md:px-6">
      <div className="mx-auto w-full max-w-2xl">
        <Button sup className="w-full" disabled={disabled || done} onClick={onSend}>{done ? `✓ ${t("sup.entryLogged")}` : t("sup.send")}</Button>
      </div>
    </div>
  );
}
