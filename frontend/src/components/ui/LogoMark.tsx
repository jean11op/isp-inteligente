export default function LogoMark({ size = 24 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
      <path d="M4 12h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <circle cx="4.5" cy="12" r="2.5" fill="var(--paper)" stroke="currentColor" strokeWidth="2" />
      <circle cx="12" cy="12" r="2.5" fill="var(--paper)" stroke="currentColor" strokeWidth="2" />
      <circle cx="19.5" cy="12" r="3" fill="var(--accent)" />
    </svg>
  );
}