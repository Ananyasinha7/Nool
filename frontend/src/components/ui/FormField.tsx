import { useId, type InputHTMLAttributes, type ReactNode } from "react";

interface FieldProps {
  label: string;
  helper?: string;
  error?: string | null;
  children: (a: { id: string; describedBy: string | undefined; invalid: boolean }) => ReactNode;
}

/** Label above, helper below, error below with an icon: never a placeholder-only label (Doc2 C-05). */
export function FormField({ label, helper, error, children }: FieldProps) {
  const id = useId();
  const msgId = `${id}-msg`;
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-label text-ink-2">{label}</label>
      {children({ id, describedBy: error || helper ? msgId : undefined, invalid: !!error })}
      {error ? (
        <p id={msgId} aria-live="polite" className="flex items-start gap-1 text-[13px] text-red"><span aria-hidden="true">⚠</span>{error}</p>
      ) : helper ? (
        <p id={msgId} className="text-[13px] text-ink-3">{helper}</p>
      ) : null}
    </div>
  );
}

export const inputCls = (invalid: boolean) =>
  `min-h-[44px] w-full rounded-md border bg-surface px-3 py-2 text-ink shadow-xs transition-colors duration-150 placeholder:text-ink-3 hover:border-ink/30 ${invalid ? "border-red" : "border-line-strong"}`;

interface TextProps extends InputHTMLAttributes<HTMLInputElement> { label: string; helper?: string; error?: string | null }
export function TextInput({ label, helper, error, className = "", ...rest }: TextProps) {
  return (
    <FormField label={label} helper={helper} error={error}>
      {({ id, describedBy, invalid }) => (
        <input id={id} aria-describedby={describedBy} aria-invalid={invalid || undefined} className={`${inputCls(invalid)} ${className}`} {...rest} />
      )}
    </FormField>
  );
}
