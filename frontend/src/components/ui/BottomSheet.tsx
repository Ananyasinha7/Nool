import { useEffect, useRef, type ReactNode } from "react";

interface Props { open: boolean; onClose: () => void; title: string; children: ReactNode }

/** Mobile filter and picker surface; a centred card on wide screens. Closes on scrim tap and Escape. */
export function BottomSheet({ open, onClose, title, children }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const prev = document.activeElement as HTMLElement | null;
    ref.current?.focus();
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    return () => { document.removeEventListener("keydown", onKey); prev?.focus(); };
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-40 flex items-end justify-center md:items-center" role="presentation">
      <div className="absolute inset-0 bg-ink/30" onClick={onClose} aria-hidden="true" />
      <div ref={ref} role="dialog" aria-modal="true" aria-label={title} tabIndex={-1}
           className="sheet-in relative max-h-[85vh] w-full max-w-md md:max-w-lg overflow-y-auto rounded-t-md border border-line bg-surface p-4 pb-[calc(16px+var(--safe-b))] shadow-[0_-8px_24px_rgba(20,24,31,.08)] md:rounded-md">
        <div aria-hidden="true" className="mx-auto mb-3 h-1 w-10 rounded-full bg-line-strong md:hidden" />
        <h2 className="mb-3 text-heading">{title}</h2>
        {children}
      </div>
    </div>
  );
}
