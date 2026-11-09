import { useState } from "react";
import { api, errorKey } from "../../../api/client";
import { useI18n } from "../../../i18n/provider";
import { useAsync } from "../../../lib/useAsync";
import { usePageTitle } from "../../../lib/usePageTitle";
import { EmptyState, ErrorState, SkeletonRows } from "../../../components/ui";
import { WarningDetail } from "./WarningDetail";
import { WarningList } from "./WarningList";

export default function WarningsPage() {
  const { t } = useI18n();
  usePageTitle(t("merch.warnings"));
  const list = useAsync(() => api.warnings(), [], "merch.warnings");
  const [sel, setSel] = useState<string | null>(null);

  if (list.loading && !list.data) return <SkeletonRows n={4} />;
  if (list.error) return <ErrorState message={t(errorKey(list.error))} onRetry={list.reload} />;
  const items = list.data ?? [];
  if (items.length === 0) return <EmptyState text={t("warn.empty")} />;
  const current = items.find((w) => w.id === sel) ?? null;
  const detail = current ?? (window.matchMedia?.("(min-width:1024px)").matches ? items[0] : null);

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-title">{t("warn.inbox")}</h1>
      <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <div className={detail && current ? "hidden lg:block" : ""}>
          <WarningList items={items} selected={detail?.id ?? null} onSelect={setSel} />
        </div>
        {detail && (
          <div className={current ? "" : "hidden lg:block"}>
            <WarningDetail key={detail.id} w={detail} onBack={() => setSel(null)} onDone={() => { setSel(null); list.reload(); }} />
          </div>
        )}
      </div>
    </div>
  );
}
