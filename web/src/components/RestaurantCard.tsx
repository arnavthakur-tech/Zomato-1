import { BUDGET_LABELS, type Budget, type Recommendation } from "../lib/types";

interface RestaurantCardProps {
  rec: Recommendation;
  budget?: Budget;
  source: string;
}

function formatCost(value: number | null): string {
  if (value == null) return "n/a";
  return `₹${Math.round(value).toLocaleString()} for two`;
}

function formatRating(value: number | null): string {
  if (value == null) return "n/a";
  return value.toFixed(1);
}

function cuisineChips(cuisine: string): string[] {
  const parts = cuisine
    .split(",")
    .map((p) => p.trim())
    .filter(Boolean);
  return parts.length ? parts.slice(0, 5) : ["Mixed cuisine"];
}

export function RestaurantCard({ rec, budget, source }: RestaurantCardProps) {
  const isTop = rec.rank === 1;
  const chips = cuisineChips(rec.cuisine);

  return (
    <article className="group relative overflow-hidden rounded-xl border border-surface-variant bg-surface-container-low p-5 shadow-sm transition-all duration-200 hover:bg-surface-container sm:p-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
        <div className="flex items-start gap-3.5">
          <span
            className={`flex h-8 w-8 shrink-0 items-center justify-center rounded font-mono text-xs font-bold ${
              isTop
                ? "bg-primary-container text-on-primary-container"
                : "border border-surface-variant bg-surface-container-highest text-on-surface"
            }`}
          >
            {String(rec.rank).padStart(2, "0")}
          </span>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="font-headline text-xl font-semibold tracking-tight text-on-surface transition-colors group-hover:text-primary">
                {rec.name}
              </h3>
              {isTop && (
                <span className="inline-flex items-center gap-1 rounded border border-primary-container/30 bg-primary-container/15 px-2 py-0.5 text-[11px] font-semibold text-primary">
                  ★ Top Match
                </span>
              )}
            </div>
            <div className="mt-1.5 flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs text-on-surface">
                {formatCost(rec.estimated_cost)}
              </span>
              {budget && (
                <span className="rounded bg-surface-container-highest px-1.5 py-0.5 text-[11px] font-semibold text-secondary">
                  {BUDGET_LABELS[budget]}
                </span>
              )}
            </div>
          </div>
        </div>

        <div
          className={`inline-flex shrink-0 items-center gap-1 rounded px-2.5 py-1 font-mono text-xs font-bold ${
            isTop
              ? "bg-primary-container text-on-primary-container"
              : "border border-surface-variant bg-surface-container-highest text-on-surface"
          }`}
        >
          {formatRating(rec.rating)} ★
        </div>
      </div>

      <div className="my-3.5 flex flex-wrap items-center gap-1.5">
        {chips.map((chip) => (
          <span
            key={chip}
            className="rounded border border-surface-variant bg-surface-container px-2.5 py-1 text-xs font-medium text-on-surface-variant"
          >
            {chip}
          </span>
        ))}
      </div>

      <div
        className={`mb-4 rounded-lg border border-surface-variant/80 border-l-2 bg-surface-container-lowest p-3.5 ${
          isTop ? "border-l-primary-container" : "border-l-surface-variant"
        }`}
      >
        <div
          className={`mb-1 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider ${
            isTop ? "text-primary" : "text-secondary"
          }`}
        >
          <span aria-hidden>◈</span>
          Why this fits
        </div>
        <p className="text-[13px] leading-relaxed text-on-surface-variant">
          {rec.explanation}
        </p>
      </div>

      <div className="flex flex-col justify-between gap-3 border-t border-surface-variant pt-3 sm:flex-row sm:items-center">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded border border-surface-variant bg-surface-container px-2 py-0.5 text-[11px] font-semibold text-secondary">
            Verified dataset row
          </span>
          <span className="rounded border border-surface-variant bg-surface-container px-2 py-0.5 text-[11px] font-semibold text-secondary">
            source: {source}
          </span>
        </div>
      </div>
    </article>
  );
}
