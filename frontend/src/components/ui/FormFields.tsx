import { useId, type ReactNode, type SelectHTMLAttributes, type TextareaHTMLAttributes } from "react";

interface BaseProps {
  label: string;
  hint?: string;
  error?: string;
}

function Wrapper({ id, label, hint, error, children }: BaseProps & { id: string; children: ReactNode }) {
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {hint && <span className="field-hint">{hint}</span>}
      {children}
      {error && (
        <span className="field-error" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}

export function TextAreaField({ label, hint, error, ...rest }: BaseProps & TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const id = useId();
  return (
    <Wrapper id={id} label={label} hint={hint} error={error}>
      <textarea id={id} rows={4} aria-invalid={error ? true : undefined} {...rest} />
    </Wrapper>
  );
}

export function SelectField({ label, hint, error, children, ...rest }: BaseProps & SelectHTMLAttributes<HTMLSelectElement>) {
  const id = useId();
  return (
    <Wrapper id={id} label={label} hint={hint} error={error}>
      <select id={id} aria-invalid={error ? true : undefined} {...rest}>
        {children}
      </select>
    </Wrapper>
  );
}
