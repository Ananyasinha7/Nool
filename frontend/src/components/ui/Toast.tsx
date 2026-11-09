import { createContext, useCallback, useContext, useMemo, useRef, useState, type ReactNode } from "react";

interface ToastItem { id: number; message: string; action?: { label: string; onClick: () => void } }
interface Ctx { show: (message: string, action?: ToastItem["action"]) => void }
const ToastCtx = createContext<Ctx | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const next = useRef(1);
  const show = useCallback((message: string, action?: ToastItem["action"]) => {
    const id = next.current++;
    setItems((x) => [...x, { id, message, action }]);
    setTimeout(() => setItems((x) => x.filter((i) => i.id !== id)), 3000); // 3 s, never blocks (C-13)
  }, []);
  const value = useMemo(() => ({ show }), [show]);
  return (
    <ToastCtx.Provider value={value}>
      {children}
      <div aria-live="polite" className="pointer-events-none fixed inset-x-0 bottom-0 z-50 flex flex-col items-center gap-2 px-4 pb-[calc(16px+var(--safe-b))]">
        {items.map((i) => (
          <div key={i.id} className="toast-in pointer-events-auto flex items-center gap-4 rounded bg-ink px-4 py-3 text-paper">
            <span>{i.message}</span>
            {i.action && <button className="font-semibold underline" onClick={i.action.onClick}>{i.action.label}</button>}
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}

export function useToast(): Ctx {
  const c = useContext(ToastCtx);
  if (!c) throw new Error("ToastProvider missing");
  return c;
}
