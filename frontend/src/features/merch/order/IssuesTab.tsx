import { api, errorKey } from "../../../api/client";
import type { EditableCategory, OrderDetail } from "../../../api/types";
import { useI18n } from "../../../i18n/provider";
import { useAsync } from "../../../lib/useAsync";
import { EmptyState, ErrorState, Skeleton, useToast } from "../../../components/ui";
import { NoteCompare } from "./NoteCompare";

export function IssuesTab({ order }: { order: OrderDetail }) {
  const { t } = useI18n();
  const toast = useToast();
  const notes = useAsync(() => api.notes(order.id), [order.id], `notes:${order.id}`);
  if (notes.loading && !notes.data) return <Skeleton className="h-40 w-full" />;
  if (notes.error) return <ErrorState message={t(errorKey(notes.error))} onRetry={notes.reload} />;
  const notesList = Array.isArray(notes.data) ? notes.data : [];
  if (!notesList.length) return <EmptyState text={t("order.noIssues")} />;
  async function set(id: string, c: EditableCategory) {
    try { await api.setNoteCategory(id, c); toast.show(t("common.saved")); notes.reload(); }
    catch (e) { toast.show(t(errorKey(e))); }
  }
  return (
    <div className="flex flex-col gap-6">
      {notesList.map((n) => (
        <div key={n.id} className="rounded-md border border-line bg-surface p-4">
          <NoteCompare note={n} value={n.category === "NEEDS_REVIEW" ? "" : (n.category as EditableCategory)} highlight={n.needsReview} onCategory={(c) => set(n.id, c)} />
        </div>
      ))}
    </div>
  );
}
