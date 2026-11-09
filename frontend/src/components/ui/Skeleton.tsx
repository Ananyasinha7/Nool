/** Static grey blocks that fade 0.6-1.0 over 1.2 s: no shimmer sweeps (Doc2 C-14). */
export function Skeleton({ className = "" }: { className?: string }) {
  return <div aria-hidden="true" className={`skeleton ${className}`} />;
}
export function SkeletonRows({ n = 6 }: { n?: number }) {
  return (
    <div role="status" aria-busy="true" className="flex flex-col gap-3">
      {Array.from({ length: n }, (_, i) => <Skeleton key={i} className="h-[72px] w-full" />)}
    </div>
  );
}
