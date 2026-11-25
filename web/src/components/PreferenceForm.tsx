"use client";

import {
  BUDGET_LABELS,
  BUDGET_ORDER,
  type Budget,
  type RecommendRequest,
} from "../lib/types";

export interface PreferenceFormValues {
  location: string;
  budget: Budget;
  cuisine: string;
  min_rating: number;
  additional_preferences: string;
  max_recommendations: number;
}

interface PreferenceFormProps {
  values: PreferenceFormValues;
  locationOptions: string[];
  cuisineOptions: string[];
  loading: boolean;
  onChange: (next: PreferenceFormValues) => void;
  onSubmit: () => void;
  onClear: () => void;
}

export function PreferenceForm({
  values,
  locationOptions,
  cuisineOptions,
  loading,
  onChange,
  onSubmit,
  onClear,
}: PreferenceFormProps) {
  const set = <K extends keyof PreferenceFormValues>(
    key: K,
    value: PreferenceFormValues[K],
  ) => onChange({ ...values, [key]: value });

  return (
    <aside className="space-y-4 lg:sticky lg:top-20 lg:col-span-5 xl:col-span-4">
      <section className="relative overflow-hidden rounded-xl border border-surface-variant bg-surface-container-low p-6 shadow-md">
        <div className="absolute left-0 right-0 top-0 h-0.5 bg-gradient-to-r from-primary-container via-primary-container/40 to-transparent" />

        <div className="mb-5 flex items-center justify-between border-b border-surface-variant pb-4">
          <div className="flex items-center gap-2">
            <span className="text-primary" aria-hidden>
              ◎
            </span>
            <h2 className="font-headline text-base font-semibold text-on-surface">
              Your Preferences
            </h2>
          </div>
          <span className="rounded border border-surface-variant bg-surface-container px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wider text-secondary">
            Filters
          </span>
        </div>

        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
          }}
        >
          <div>
            <label className="mb-1.5 flex items-center justify-between text-xs font-medium text-on-surface-variant">
              <span>Location</span>
              <span className="font-mono text-secondary">Locality / City</span>
            </label>
            <select
              className="h-10 w-full rounded border border-surface-variant bg-surface-container px-3 text-sm text-on-surface outline-none transition focus:border-primary-container focus:ring-1 focus:ring-primary-container"
              value={values.location}
              onChange={(e) => set("location", e.target.value)}
            >
              {locationOptions.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-medium text-on-surface-variant">
              Budget Level
            </label>
            <div className="grid grid-cols-3 gap-2" role="radiogroup">
              {BUDGET_ORDER.map((b) => {
                const selected = values.budget === b;
                return (
                  <button
                    key={b}
                    type="button"
                    onClick={() => set("budget", b)}
                    className={`flex h-9 items-center justify-center rounded text-xs font-medium transition-colors ${
                      selected
                        ? "border border-primary-container bg-primary-container/15 font-semibold text-on-surface"
                        : "border border-surface-variant bg-surface-container text-secondary hover:bg-surface-container-high hover:text-on-surface"
                    }`}
                  >
                    {BUDGET_LABELS[b]}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-medium text-on-surface-variant">
              Cuisine & Dish types
            </label>
            <select
              className="h-10 w-full rounded border border-surface-variant bg-surface-container px-3 text-sm text-on-surface outline-none transition focus:border-primary-container focus:ring-1 focus:ring-primary-container"
              value={values.cuisine}
              onChange={(e) => set("cuisine", e.target.value)}
            >
              {cuisineOptions.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          <div className="pt-1">
            <div className="mb-2 flex items-center justify-between">
              <label className="text-xs font-medium text-on-surface-variant">
                Minimum Rating
              </label>
              <span className="inline-flex items-center gap-1 rounded border border-surface-variant bg-surface-container-highest px-2 py-0.5 font-mono text-xs font-semibold text-primary-container">
                {values.min_rating.toFixed(1)} ★
              </span>
            </div>
            <input
              className="br-slider accent-primary-container"
              type="range"
              min={0}
              max={5}
              step={0.1}
              value={values.min_rating}
              onChange={(e) => set("min_rating", Number(e.target.value))}
            />
            <div className="mt-1.5 flex justify-between font-mono text-xs text-secondary">
              <span>0.0</span>
              <span className="text-on-surface-variant">4.0 ★ threshold</span>
              <span>5.0</span>
            </div>
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-medium text-on-surface-variant">
              Additional Preferences & Vibe
            </label>
            <textarea
              className="w-full resize-none rounded border border-surface-variant bg-surface-container p-3 text-sm text-on-surface outline-none transition placeholder:text-secondary/60 focus:border-primary-container focus:ring-1 focus:ring-primary-container"
              rows={3}
              placeholder="e.g. family-friendly, quiet, date night"
              value={values.additional_preferences}
              onChange={(e) => set("additional_preferences", e.target.value)}
            />
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-medium text-on-surface-variant">
              Max recommendations
            </label>
            <input
              type="number"
              min={1}
              max={10}
              className="h-10 w-full rounded border border-surface-variant bg-surface-container px-3 text-sm text-on-surface outline-none focus:border-primary-container"
              value={values.max_recommendations}
              onChange={(e) =>
                set(
                  "max_recommendations",
                  Math.min(10, Math.max(1, Number(e.target.value) || 1)),
                )
              }
            />
          </div>

          <div className="flex flex-col gap-2.5 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="flex h-11 w-full items-center justify-center gap-2 rounded border-t border-primary-fixed/20 bg-primary-container text-xs font-semibold text-white shadow-lg shadow-primary-container/20 transition active:scale-[0.99] hover:bg-primary-container/90 disabled:opacity-60"
            >
              <span aria-hidden>✦</span>
              {loading ? "Finding matches…" : "Get recommendations"}
            </button>
            <button
              type="button"
              onClick={onClear}
              disabled={loading}
              className="flex h-9 w-full items-center justify-center gap-1.5 rounded border border-surface-variant bg-transparent text-xs font-medium text-secondary transition hover:bg-surface-container hover:text-on-surface disabled:opacity-60"
            >
              <span aria-hidden>↺</span>
              Clear filters
            </button>
          </div>
        </form>
      </section>
    </aside>
  );
}

export function toRecommendRequest(
  values: PreferenceFormValues,
  anyCuisineLabel: string,
): RecommendRequest {
  return {
    location: values.location,
    budget: values.budget,
    cuisine: values.cuisine === anyCuisineLabel ? "" : values.cuisine,
    min_rating: values.min_rating,
    additional_preferences: values.additional_preferences,
    max_recommendations: values.max_recommendations,
    use_llm: true,
  };
}
