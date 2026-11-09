import { useEffect, useState } from "react";
import { useT } from "../../i18n/provider";
import { canRecord, useRecorder } from "../../lib/offline/audio";

/** Voice note (P2): tap to start and stop, 30 s max, level bar and timer. Hidden when not allowed or unsupported. */
export function MicButton({ blob, onChange }: { blob: Blob | null; onChange: (b: Blob | null) => void }) {
  const t = useT();
  const r = useRecorder();
  const [denied, setDenied] = useState(false);
  useEffect(() => { if (r.blob) onChange(r.blob); }, [r.blob, onChange]);
  if (!canRecord() || denied) return null;
  async function toggle() {
    if (r.recording) { r.stop(); return; }
    try { await r.start(); } catch { setDenied(true); }
  }
  return (
    <div className="flex items-center gap-3">
      <button type="button" onClick={toggle} aria-pressed={r.recording} className={`press flex min-h-[56px] min-w-[56px] flex-col items-center justify-center rounded border px-3 text-[14px] ${r.recording ? "border-red text-red" : "border-field bg-surface"}`}>
        <span aria-hidden="true">{r.recording ? "■" : "🎤"}</span>{r.recording ? t("sup.stopRecording") : t("sup.speak")}
      </button>
      {r.recording && (
        <span className="flex flex-1 items-center gap-2" role="status" aria-label={t("sup.recording")}>
          <span className="h-1 flex-1 rounded-full bg-line"><span className="block h-1 rounded-full bg-ink" style={{ width: `${Math.round(r.level * 100)}%` }} /></span>
          <span>{r.seconds}s</span>
        </span>
      )}
      {!r.recording && blob && (
        <span className="flex items-center gap-2 text-ink-2">{t("sup.voiceAttached")}
          <button type="button" aria-label={t("common.cancel")} className="min-h-[48px] min-w-[48px]" onClick={() => { onChange(null); r.clear(); }}>×</button>
        </span>
      )}
    </div>
  );
}
