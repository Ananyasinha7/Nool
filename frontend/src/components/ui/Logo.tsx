/** One continuous thread ending in a status dot (Doc2 section 3). */
export function LogoMark({ size = 32 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" role="img" aria-label="Nool">
      <rect width="64" height="64" rx="14" fill="#181E1B" />
      <path d="M18 46V18l28 28" fill="none" stroke="#F9F8F5" strokeWidth="5.5" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="46" cy="18" r="5" fill="#26694A" />
    </svg>
  );
}
export function Wordmark({ tamil = false }: { tamil?: boolean }) {
  return (
    <span className="inline-flex items-center gap-2.5">
      <LogoMark size={28} />
      <span className="text-[20px] font-semibold tracking-[-0.02em] text-ink">nool</span>
      {tamil && <span lang="ta" className="text-[17px] text-ink-2 font-medium">நூல்</span>}
    </span>
  );
}
