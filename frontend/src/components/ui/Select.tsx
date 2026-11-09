import type { SelectHTMLAttributes } from "react";
import { FormField, inputCls } from "./FormField";

export interface Option { value: string; label: string }
interface Props extends Omit<SelectHTMLAttributes<HTMLSelectElement>, "onChange"> {
  label: string;
  options: Option[];
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  error?: string | null;
}

// Native <select> everywhere: best on cheap Android phones, fully accessible, zero JS cost (C-06).
export function Select({ label, options, value, onChange, placeholder, error, className = "", ...rest }: Props) {
  return (
    <FormField label={label} error={error}>
      {({ id, describedBy, invalid }) => (
        <select id={id} aria-describedby={describedBy} value={value} onChange={(e) => onChange(e.target.value)}
                className={`${inputCls(invalid)} ${className}`} {...rest}>
          {placeholder !== undefined && <option value="">{placeholder}</option>}
          {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      )}
    </FormField>
  );
}
