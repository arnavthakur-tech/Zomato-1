import { BUDGET_LABELS, type RecommendResponse } from "../lib/types";

interface SummaryBannerProps {
  response: RecommendResponse;
}

export function SummaryBanner({ response }: SummaryBannerProps) {
  const result = response.result;
  if (!result) return null;

  const count = result.recommendations.length;
  const prefs = response.preferences;
  const isFallback = result.source === "fallback";
  const sourceLabel = isFallback
    ? "Sorted by rating"
    : "Personalized ranking";

  return (
    <div className="rounded-xl border border-surface-variant border-l-4 border-l-primary-container bg-surface-container-low p-5 shadow-sm">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-primary-container" aria-hidden>
            ◈
          </span>
          <h2 className="font-headline text-base font-semibold text-on-surface">
            Your shortlist ({count} matches)
          </h2>
        </div>
        <span className="rounded border border-surface-variant bg-surface-container px-2.5 py-1 font-mono text-xs text-secondary">
          {sourceLabel}
        </span>
      </div>
      <p className="text-sm leading-relaxed text-secondary">{result.summary}</p>
      <div className="mt-3.5 flex items-center gap-4 overflow-x-auto border-t border-surface-variant/60 pt-3 font-mono text-xs text-secondary">
        <span className="inline-flex items-center gap-1 text-on-surface-variant">
          <span className="h-1.5 w-1.5 rounded-full bg-primary-container" />
          Locality: {prefs?.location ?? "—"}
        </span>
        <span>•</span>
        <span>
          Budget: {prefs ? BUDGET_LABELS[prefs.budget] : "—"}
        </span>
        <span>•</span>
        <span>
          Min rating: {prefs ? `${prefs.min_rating.toFixed(1)}★` : "—"}
        </span>
        <span>•</span>
        <span>
          {response.total_matches} filter matches · cap {response.candidate_cap}
        </span>
      </div>
    </div>
  );
}
