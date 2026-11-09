import "../../i18n/app";
import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { api } from "../../api/client";
import { useT } from "../../i18n/provider";
import { IdentityChip, LangToggle, LogoMark } from "../ui";

export function MerchShell() {
  const t = useT();
  const [count, setCount] = useState<number | null>(null);
  useEffect(() => { api.warnings().then((w) => setCount(w.length)).catch(() => undefined); }, []);

  const link = ({ isActive }: { isActive: boolean }) =>
    `inline-flex min-h-[44px] items-center border-b-2 px-1 text-[14px] transition-colors duration-150 ${
      isActive
        ? "border-green font-semibold text-ink"
        : "border-transparent text-ink-2 hover:border-line-strong hover:text-ink"
    }`;
  const tab = ({ isActive }: { isActive: boolean }) =>
    `flex min-h-[56px] flex-1 flex-col items-center justify-center text-[12px] transition-colors duration-150 ${
      isActive ? "font-semibold text-green-text" : "text-ink-2"
    }`;
  const warnCount = count ? (
    <span className="ml-1.5 inline-flex items-center rounded-full bg-amber-bg px-1.5 py-0.2 text-[11px] font-semibold text-amber-text border border-[#F5E4C2]">
      {count}
    </span>
  ) : null;

  return (
    <div className="min-h-screen bg-paper pb-[calc(56px+var(--safe-b))] md:pb-0">
      <header className="sticky top-0 z-30 border-b border-line bg-paper/95 backdrop-blur-sm pt-[var(--safe-t)]">
        <div className="mx-auto flex max-w-page items-center gap-6 px-4 md:px-6">
          <NavLink to="/board" className="py-2.5 flex items-center gap-2">
            <LogoMark size={24} />
            <span className="hidden sm:inline text-[20px] font-semibold tracking-[-0.02em] text-ink">nool</span>
          </NavLink>
          <nav className="hidden gap-6 md:flex" aria-label="Main">
            <NavLink to="/board" className={link}>{t("merch.board")}</NavLink>
            <NavLink to="/warnings" className={link}>
              <span>{t("merch.warnings")}</span>
              {warnCount}
            </NavLink>
            <NavLink to="/orders/new" className={link}>{t("merch.newOrder")}</NavLink>
            <NavLink to="/outbox" className={link}>{t("merch.outbox")}</NavLink>
          </nav>
          <div className="ml-auto flex items-center gap-1.5 sm:gap-3 py-2">
            <IdentityChip role="MERCHANDISER" />
            <LangToggle />
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-page px-4 py-6 md:px-6"><Outlet /></main>
      <nav aria-label="Main navigation" className="fixed inset-x-0 bottom-0 z-30 flex border-t border-line bg-paper/95 backdrop-blur-sm pb-[var(--safe-b)] shadow-lg md:hidden">
        <NavLink to="/board" className={tab}>{t("merch.board")}</NavLink>
        <NavLink to="/warnings" className={tab}>
          <span>{t("merch.warnings")}</span>
          {count ? <span className="text-[10px] text-amber-text font-bold">({count})</span> : null}
        </NavLink>
        <NavLink to="/orders/new" className={tab}>{t("merch.newOrder")}</NavLink>
        <NavLink to="/outbox" className={tab}>{t("merch.outbox")}</NavLink>
      </nav>
    </div>
  );
}
