import { useRef, type KeyboardEvent, type ReactNode } from "react";

export interface TabDef { id: string; label: string }
interface Props { tabs: TabDef[]; active: string; onChange: (id: string) => void; children: ReactNode }

/** Accessible tablist: arrow keys move between tabs (WAI-ARIA tabs pattern). */
export function Tabs({ tabs, active, onChange, children }: Props) {
  const refs = useRef<Record<string, HTMLButtonElement | null>>({});
  const onKey = (e: KeyboardEvent, i: number) => {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    const n = tabs[(i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length].id;
    onChange(n);
    refs.current[n]?.focus();
  };
  return (
    <div>
      <div role="tablist" className="flex gap-5 overflow-x-auto border-b border-line">
        {tabs.map((tab, i) => (
          <button key={tab.id} ref={(el) => { refs.current[tab.id] = el; }} role="tab" id={`tab-${tab.id}`}
                  aria-selected={active === tab.id} aria-controls={`panel-${tab.id}`} tabIndex={active === tab.id ? 0 : -1}
                  onClick={() => onChange(tab.id)} onKeyDown={(e) => onKey(e, i)}
                  className={`min-h-[44px] whitespace-nowrap border-b-2 text-[14px] transition-colors duration-150 ${active === tab.id ? "border-green font-semibold text-ink" : "border-transparent text-ink-2 hover:border-line-strong hover:text-ink"}`}>
            {tab.label}
          </button>
        ))}
      </div>
      <div role="tabpanel" id={`panel-${active}`} aria-labelledby={`tab-${active}`} className="pt-4">{children}</div>
    </div>
  );
}
