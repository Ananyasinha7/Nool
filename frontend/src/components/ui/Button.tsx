import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";
interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  /** 56 px tall on supervisor screens (Doc2 C-01) */
  sup?: boolean;
  loading?: boolean;
}

const styles: Record<Variant, string> = {
  primary: "bg-ink text-paper border border-ink shadow-xs hover:bg-[#252E29] disabled:bg-line-strong disabled:border-field disabled:text-ink-2",
  secondary: "bg-surface text-ink border border-line-strong shadow-xs hover:bg-paper hover:border-ink/30 disabled:text-ink-3",
  ghost: "bg-transparent text-ink border border-transparent hover:bg-line/40 disabled:text-ink-3",
  danger: "bg-surface text-red border border-[#F3D7CF] hover:bg-red-bg disabled:opacity-50",
};

export function Button({ variant = "primary", sup, loading, className = "", children, disabled, type = "button", ...rest }: Props) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      className={`press inline-flex items-center justify-center gap-2 rounded-md px-4 font-medium tracking-tight disabled:cursor-not-allowed ${
        sup ? "min-h-[56px] text-[18px] font-semibold" : "min-h-[44px]"
      } ${styles[variant]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}
