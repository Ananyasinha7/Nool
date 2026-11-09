import { useI18n } from "../i18n/provider";
import { QueueChip } from "../components/sup/QueueChip";

/** Served for navigations the service worker cannot satisfy; the queue chip still works (Doc2 section 12). */
export default function OfflinePage() {
  const { t } = useI18n();
  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center gap-4 px-6 text-center">
      <h1 className="text-title">{t("offline.title")}</h1>
      <p className="text-ink-2">{t("offline.body")}</p>
      <QueueChip />
    </main>
  );
}
