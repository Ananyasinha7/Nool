import { Link, useNavigate } from "react-router-dom";
import { useT } from "../../i18n/provider";
import { IdentityChip, LangToggle, LogoMark } from "../ui";
import { QueueChip } from "./QueueChip";

export function SupHeader({ title, back }: { title?: string; back?: string }) {
  const nav = useNavigate();
  const t = useT();

  return (
    <header className="sticky top-0 z-20 border-b border-line bg-paper pt-[var(--safe-t)]">
      <div className="mx-auto flex max-w-page items-center justify-between gap-2 px-4 py-1.5 md:gap-3 md:px-6 md:py-2">
        <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
          <Link to="/s" className="flex-shrink-0 flex items-center gap-2">
            <LogoMark size={24} />
            <span className="hidden sm:inline text-[19px] font-semibold tracking-[-0.02em] text-ink">nool</span>
          </Link>
          <div className="h-5 w-px bg-line flex-shrink-0" />
          {back && (
            <button
              type="button"
              aria-label={t("common.back")}
              className="-ml-2 flex min-h-[44px] min-w-[44px] items-center justify-center text-[22px] text-ink hover:text-ink-2"
              onClick={() => nav(back)}
            >
              ←
            </button>
          )}
          <h1 className="min-w-0 truncate text-heading text-[16px] sm:text-heading">{title}</h1>
        </div>

        <div className="flex items-center gap-1.5 sm:gap-2 flex-shrink-0">
          {!back && <IdentityChip role="SUPERVISOR" unitName="Unit 1" />}
          {!back && <LangToggle />}
          <QueueChip />
        </div>
      </div>
    </header>
  );
}
