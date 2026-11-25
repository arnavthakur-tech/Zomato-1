interface EmptyStateProps {
  message: string;
  onRelax?: () => void;
}

export function EmptyState({ message, onRelax }: EmptyStateProps) {
  return (
    <div className="space-y-6">
      <div className="relative flex flex-col items-center overflow-hidden rounded-xl bg-surface-container-lowest p-8 text-center shadow-2xl md:p-12">
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <div className="h-72 w-72 rounded-full bg-primary-container/5 blur-3xl" />
        </div>
        <div className="relative z-10 mb-6 flex h-24 w-24 items-center justify-center rounded-2xl bg-surface-container-low text-4xl text-primary shadow-inner">
          ⌀
        </div>
        <div className="relative z-10 mb-8 max-w-lg">
          <h2 className="mb-3 font-headline text-2xl font-semibold tracking-tight text-on-surface sm:text-[28px]">
            No restaurants matched
          </h2>
          <p className="text-sm leading-relaxed text-secondary">{message}</p>
          <p className="mt-3 text-sm leading-relaxed text-secondary">
            Try a broader location, a lower minimum rating, or relaxing your
            cuisine filter.
          </p>
        </div>
        {onRelax && (
          <button
            type="button"
            onClick={onRelax}
            className="relative z-10 flex h-11 items-center gap-2 rounded bg-surface-container-high px-6 text-base font-semibold text-primary shadow-md transition hover:bg-surface-bright active:scale-[0.98]"
          >
            <span aria-hidden>↺</span>
            Relax filters & re-rank
          </button>
        )}
      </div>

      <div className="flex items-start gap-3.5 rounded-lg bg-surface-container-low p-4 shadow-sm">
        <span className="mt-0.5 shrink-0 text-xl text-primary" aria-hidden>
          🛡
        </span>
        <div className="flex flex-col gap-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-headline text-base font-semibold text-on-surface">
              Only real restaurants
            </span>
          </div>
          <p className="text-[13px] leading-normal text-secondary">
            BiteRank only shows places from the Zomato dataset. If nothing
            matches your filters, try loosening location, cuisine, or rating.
          </p>
        </div>
      </div>
    </div>
  );
}
