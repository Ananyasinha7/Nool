import "../../i18n/app";
import { Link } from "react-router-dom";
import { useT } from "../../i18n/provider";
import { IdentityChip, LangToggle, LogoMark } from "../ui";

export function BuyerHeader({ company, crumb }: { company: string; crumb?: { to: string; label: string } }) {
  const t = useT();
  return (
    <header className="sticky top-0 z-20 border-b border-line bg-paper pt-[var(--safe-t)]">
      <div className="mx-auto flex max-w-page items-center justify-between gap-2 px-4 py-1.5 md:gap-3 md:px-6 md:py-2">
        <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
          <Link to="/b" className="flex-shrink-0 flex items-center gap-2">
            <LogoMark size={24} />
            <span className="hidden sm:inline text-[19px] font-semibold tracking-[-0.02em] text-ink">nool</span>
          </Link>
          <div className="hidden sm:block h-5 w-px bg-line flex-shrink-0" />
          {crumb ? (
            <Link to={crumb.to} className="inline-flex min-h-[44px] items-center text-ink-2 hover:text-ink text-[14px]">
              ← {crumb.label}
            </Link>
          ) : (
            <div className="hidden sm:block min-w-0">
              <p className="truncate text-[15px] font-semibold text-ink leading-tight">{company}</p>
              <p className="text-[11px] text-ink-3 leading-tight">{t("buyer.from")}</p>
            </div>
          )}
        </div>

        <div className="flex items-center gap-1.5 sm:gap-2 flex-shrink-0">
          <IdentityChip role="BUYER" companyName={company} />
          <LangToggle />
        </div>
      </div>
    </header>
  );
}
