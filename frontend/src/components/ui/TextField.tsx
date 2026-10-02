import type { InputHTMLAttributes, Ref } from "react";

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  ref?: Ref<HTMLInputElement>;
}

export default function TextField({ label, error, id, ref, ...rest }: TextFieldProps) {
  const inputId = id ?? rest.name;

  return (
    <div className="field">
      <label htmlFor={inputId}>{label}</label>
      <input id={inputId} ref={ref} aria-invalid={error ? true : undefined} {...rest} />
      {error && (
        <span className="field-error" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}