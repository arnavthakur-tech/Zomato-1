export function IdleState() {
  return (
    <div className="rounded-xl border border-surface-variant bg-surface-container-low p-8 text-center">
      <p className="font-headline text-base font-semibold text-on-surface">
        Your shortlist will appear here
      </p>
      <p className="mt-2 text-sm text-secondary">
        Set preferences on the left, then click{" "}
        <em className="text-on-surface">Get recommendations</em>. Hard filters
        run first; the LLM only ranks real candidates.
      </p>
    </div>
  );
}
