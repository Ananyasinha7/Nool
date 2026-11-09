import { api, errorKey } from "../../../api/client";
import { useI18n } from "../../../i18n/provider";
import { useAsync } from "../../../lib/useAsync";
import { usePageTitle } from "../../../lib/usePageTitle";
import { fmtDateTime } from "../../../lib/format";
import { EmptyState, ErrorState, SkeletonRows } from "../../../components/ui";

/** Mock outbox: nothing here ever leaves the system (Doc2 S-9, FR-28). */
export default function OutboxPage() {
  const { t, lang } = useI18n();
  usePageTitle(t("outbox.title"));
  const box = useAsync(() => api.outbox(), []);
  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-title">{t("outbox.title")}</h1>
      <p className="text-ink-2">{t("outbox.note")}</p>
      {box.loading && !box.data ? <SkeletonRows n={3} />
        : box.error ? <ErrorState message={t(errorKey(box.error))} onRetry={box.reload} />
        : !box.data?.length ? <EmptyState text={t("outbox.empty")} />
        : (
          <div className="overflow-x-auto rounded-md border border-line bg-surface">
            <table className="w-full text-left">
              <thead><tr className="border-b border-line text-label text-ink-3">
                <th className="px-3 py-2">{t("outbox.to")}</th><th className="px-3 py-2">{t("outbox.subject")}</th><th className="px-3 py-2">Message</th><th className="px-3 py-2">{t("outbox.time")}</th>
              </tr></thead>
              <tbody>
                {box.data.map((m) => (
                  <tr key={m.id} className="border-b border-line align-top last:border-b-0">
                    <td className="px-3 py-2">{m.to}</td><td className="px-3 py-2 font-medium">{m.subject}</td>
                    <td className="max-w-md px-3 py-2 text-ink-2">{m.body}</td><td className="whitespace-nowrap px-3 py-2 text-ink-2">{fmtDateTime(m.createdAt, lang)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
    </div>
  );
}
