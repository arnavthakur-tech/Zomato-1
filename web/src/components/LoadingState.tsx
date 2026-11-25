export function LoadingState() {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 font-mono text-xs text-secondary">
        <span className="h-2 w-2 animate-br-pulse rounded-full bg-primary-container" />
        Finding matches…
      </div>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="overflow-hidden rounded-xl border border-surface-variant bg-surface-container-low p-5"
        >
          <div className="mb-3 flex gap-3">
            <div className="br-skeleton h-8 w-8 rounded" />
            <div className="flex-1 space-y-2">
              <div className="br-skeleton h-5 w-2/3 rounded" />
              <div className="br-skeleton h-3 w-1/3 rounded" />
            </div>
          </div>
          <div className="br-skeleton mb-3 h-8 w-full rounded" />
          <div className="br-skeleton h-16 w-full rounded" />
        </div>
      ))}
    </div>
  );
}
