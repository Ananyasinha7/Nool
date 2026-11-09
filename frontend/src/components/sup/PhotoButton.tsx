import { useEffect, useRef, useState } from "react";
import { useT } from "../../i18n/provider";
import { compressImage } from "../../lib/offline/compress";

/** Opens the camera, compresses on the device, shows a 64 px thumbnail with a remove button. */
export function PhotoButton({ blob, onChange }: { blob: Blob | null; onChange: (b: Blob | null) => void }) {
  const t = useT();
  const input = useRef<HTMLInputElement>(null);
  const [url, setUrl] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  useEffect(() => { if (!blob) { setUrl(null); return; } const u = URL.createObjectURL(blob); setUrl(u); return () => URL.revokeObjectURL(u); }, [blob]);
  async function pick(f: File | undefined) {
    if (!f) return;
    setBusy(true);
    try { onChange(await compressImage(f)); } catch { onChange(null); } finally { setBusy(false); if (input.current) input.current.value = ""; }
  }
  return (
    <div className="flex items-center gap-3">
      <input ref={input} type="file" accept="image/*" capture="environment" className="hidden" onChange={(e) => void pick(e.target.files?.[0])} />
      <button type="button" aria-busy={busy} onClick={() => input.current?.click()} className="press flex min-h-[56px] min-w-[56px] flex-col items-center justify-center rounded border border-field bg-surface px-3 text-[14px]">
        <span aria-hidden="true">📷</span>{t("sup.photo")}
      </button>
      {url && (
        <span className="relative">
          <img src={url} alt={t("sup.photo")} width={64} height={64} className="h-16 w-16 rounded object-cover" />
          <button type="button" aria-label={t("sup.removePhoto")} onClick={() => onChange(null)} className="absolute -right-2 -top-2 flex h-8 w-8 items-center justify-center rounded-full bg-ink text-paper">×</button>
        </span>
      )}
    </div>
  );
}
