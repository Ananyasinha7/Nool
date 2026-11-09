import { CSSProperties } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../api/client";
import { useT } from "../../i18n/provider";
import { useAuth } from "../../lib/auth";

interface Props {
  onClose: () => void;
  style?: CSSProperties;
}

export default function RoleSwitcherDropdown({ onClose, style }: Props) {
  const t = useT();
  const nav = useNavigate();
  const { signIn, signOut, refresh } = useAuth();

  async function switchTo(u: string, p: string, targetPath: string) {
    onClose();
    try {
      await signOut();
      await signIn(u, p);
      nav(targetPath, { replace: true });
    } catch {
      nav("/login");
    }
  }

  async function switchToBuyer() {
    onClose();
    try {
      await signOut();
      await api.buyerSession("demo-b-0001");
      await refresh();
      nav("/b", { replace: true });
    } catch {
      window.location.assign("/b/demo-b-0001");
    }
  }

  return (
    <div
      role="menu"
      aria-label={t("common.switchRole")}
      className="sheet-in w-56 max-w-[calc(100vw-1rem)] rounded border border-line bg-surface p-1 shadow-md"
      style={style}
    >
      <div className="border-b border-line px-3 py-1.5 text-[11px] font-semibold text-ink-3">
        {t("common.switchRole")}
      </div>
      <button
        type="button"
        role="menuitem"
        className="flex w-full items-center justify-between rounded px-3 py-2 text-left text-[13px] hover:bg-paper"
        onClick={() => switchTo("priya.merch", "Nool@Demo2026", "/board")}
      >
        <span>Priya</span>
        <span className="text-[11px] text-ink-3">{t("common.roleMerchandiser")}</span>
      </button>
      <button
        type="button"
        role="menuitem"
        className="flex w-full items-center justify-between rounded px-3 py-2 text-left text-[13px] hover:bg-paper"
        onClick={() => switchTo("murugan.u1", "246810", "/s")}
      >
        <span>Murugan</span>
        <span className="text-[11px] text-ink-3">{t("common.roleSupervisor")} (U1)</span>
      </button>
      <button
        type="button"
        role="menuitem"
        className="flex w-full items-center justify-between rounded px-3 py-2 text-left text-[13px] hover:bg-paper"
        onClick={switchToBuyer}
      >
        <span>Hannah</span>
        <span className="text-[11px] text-ink-3">{t("common.roleBuyer")}</span>
      </button>
      <div className="my-1 border-t border-line" />
      <button
        type="button"
        role="menuitem"
        className="flex w-full items-center px-3 py-2 text-left text-[13px] text-red hover:bg-red-bg"
        onClick={async () => {
          onClose();
          await signOut();
          nav("/login");
        }}
      >
        {t("common.signOut")}
      </button>
    </div>
  );
}
