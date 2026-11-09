import { useState, useRef, useEffect, lazy, Suspense } from "react";
import { createPortal } from "react-dom";
import { useT } from "../../i18n/provider";
import { useAuth } from "../../lib/auth";

const SHOW_DEMO = import.meta.env.DEV || import.meta.env.VITE_DEMO_LOGINS === "true";
const RoleSwitcher = lazy(() => import("./RoleSwitcherDropdown"));

interface Props {
  role?: "SUPERVISOR" | "MERCHANDISER" | "BUYER";
  unitName?: string;
  companyName?: string;
  className?: string;
}

export function IdentityChip({ role, unitName, companyName, className = "" }: Props) {
  const t = useT();
  const { me } = useAuth();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const [dropPos, setDropPos] = useState<{ top: number; left: number; maxHeight: number } | null>(null);

  // Compute dropdown position: left-align when chip is in left half, right-align when in right half
  useEffect(() => {
    if (open && ref.current) {
      const rect = ref.current.getBoundingClientRect();
      const W = window.innerWidth;
      const dropW = 224; // w-56 = 14rem = 224px
      const top = rect.bottom + 4;
      const maxHeight = window.innerHeight - top - 8;
      // Left-align to button's left edge, then clamp so it never overflows either side
      const left = Math.min(Math.max(rect.left, 8), W - dropW - 8);
      setDropPos({ top, left, maxHeight });
    }
  }, [open]);

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) document.addEventListener("click", onDocClick);
    return () => document.removeEventListener("click", onDocClick);
  }, [open]);

  const currentRole = role ?? me?.role;
  const roleLabel =
    currentRole === "SUPERVISOR"
      ? t("common.roleSupervisor")
      : currentRole === "BUYER"
      ? t("common.roleBuyer")
      : t("common.roleMerchandiser");

  const displayName = me?.displayName || (currentRole === "BUYER" ? "Hannah" : "");
  const subtitle =
    currentRole === "SUPERVISOR"
      ? unitName || "Unit 1"
      : currentRole === "BUYER"
      ? companyName || me?.buyerName || "Company B"
      : null;

  const showSubtitle = subtitle && subtitle !== displayName;

  return (
    <div className={`relative inline-flex items-center ${className}`} ref={ref}>
      <button
        type="button"
        onClick={() => SHOW_DEMO && setOpen((x) => !x)}
        className={`inline-flex min-h-[44px] items-center gap-1.5 rounded border border-line bg-surface px-2.5 py-1 text-left text-[13px] text-ink transition-colors hover:bg-paper ${
          SHOW_DEMO ? "cursor-pointer" : "cursor-default"
        }`}
        aria-expanded={open}
        aria-haspopup={SHOW_DEMO ? "menu" : undefined}
        title={SHOW_DEMO ? t("common.switchRole") : undefined}
      >
        <span className="flex flex-col leading-tight">
          <span className="font-medium text-ink">
            {displayName || roleLabel}
            {showSubtitle && <span className="text-ink-3 font-normal"> · {subtitle}</span>}
          </span>
          <span className="text-[11px] text-ink-3">
            {roleLabel}
            {SHOW_DEMO && " ▾"}
          </span>
        </span>
      </button>

      {open && SHOW_DEMO && dropPos &&
        createPortal(
          <Suspense fallback={null}>
            <RoleSwitcher
              onClose={() => setOpen(false)}
              style={{ position: "fixed", top: dropPos.top, left: dropPos.left, zIndex: 9999, maxHeight: dropPos.maxHeight, overflowY: "auto" }}
            />
          </Suspense>,
          document.body
        )
      }
    </div>
  );
}
