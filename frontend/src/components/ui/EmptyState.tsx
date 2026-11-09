import { Button } from "./Button";

export function EmptyState({ text, actionLabel, onAction }: { text: string; actionLabel?: string; onAction?: () => void }) {
  return (
    <div className="flex flex-col items-center gap-4 px-4 py-16 text-center">
      <p className="max-w-sm text-ink-2">{text}</p>
      {actionLabel && onAction && <Button variant="secondary" onClick={onAction}>{actionLabel}</Button>}
    </div>
  );
}
