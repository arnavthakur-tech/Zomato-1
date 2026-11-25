"use client";

import { useCallback, useEffect, useState } from "react";
import { fetchMeta, postRecommend } from "../lib/api";
import type { MetaResponse, RecommendResponse } from "../lib/types";
import { EmptyState } from "./EmptyState";
import { ErrorBanner } from "./ErrorBanner";
import { FallbackChip } from "./FallbackChip";
import { HeroBanner } from "./HeroBanner";
import { IdleState } from "./IdleState";
import { LoadingState } from "./LoadingState";
import {
  PreferenceForm,
  toRecommendRequest,
  type PreferenceFormValues,
} from "./PreferenceForm";
import { RestaurantCard } from "./RestaurantCard";
import { SummaryBanner } from "./SummaryBanner";

function defaultValues(meta: MetaResponse): PreferenceFormValues {
  return {
    location: meta.default_location,
    budget: "medium",
    cuisine: meta.any_cuisine_label,
    min_rating: 4.0,
    additional_preferences: "family-friendly, not too crowded",
    max_recommendations: 5,
  };
}

export function RecommendClient() {
  const [meta, setMeta] = useState<MetaResponse | null>(null);
  const [metaError, setMetaError] = useState<string | null>(null);
  const [values, setValues] = useState<PreferenceFormValues | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<RecommendResponse | null>(null);
  const [requestError, setRequestError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchMeta()
      .then((data) => {
        if (cancelled) return;
        setMeta(data);
        setValues(defaultValues(data));
      })
      .catch((err: Error) => {
        if (cancelled) return;
        setMetaError(err.message || "Failed to load dataset meta");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const handleClear = useCallback(() => {
    if (!meta) return;
    setValues(defaultValues(meta));
    setResponse(null);
    setRequestError(null);
    setSubmitted(false);
  }, [meta]);

  const handleSubmit = useCallback(async () => {
    if (!meta || !values) return;
    setLoading(true);
    setRequestError(null);
    setSubmitted(true);
    try {
      const body = toRecommendRequest(values, meta.any_cuisine_label);
      const result = await postRecommend(body);
      setResponse(result);
    } catch (err) {
      setResponse(null);
      setRequestError(
        err instanceof Error ? err.message : "Recommendation request failed",
      );
    } finally {
      setLoading(false);
    }
  }, [meta, values]);

  if (metaError) {
    return (
      <ErrorBanner
        title="API unavailable"
        message={metaError}
        errors={[
          "Start the FastAPI backend: uvicorn src.api.main:app --reload --port 8000",
        ]}
      />
    );
  }

  if (!meta || !values) {
    return (
      <div className="space-y-4">
        <div className="br-skeleton h-40 w-full rounded-xl" />
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
          <div className="br-skeleton h-96 rounded-xl lg:col-span-4" />
          <div className="br-skeleton h-96 rounded-xl lg:col-span-8" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex w-full flex-col">
      <HeroBanner rowCount={meta.rows} />

      <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-12">
        <PreferenceForm
          values={values}
          locationOptions={meta.location_options}
          cuisineOptions={meta.cuisine_options}
          loading={loading}
          onChange={setValues}
          onSubmit={handleSubmit}
          onClear={handleClear}
        />

        <section className="space-y-4 lg:col-span-7 xl:col-span-8">
          {loading && <LoadingState />}

          {!loading && requestError && (
            <ErrorBanner title="Request failed" message={requestError} />
          )}

          {!loading && !requestError && !submitted && <IdleState />}

          {!loading &&
            !requestError &&
            response?.status === "validation_error" && (
              <ErrorBanner
                title="Validation error"
                message={response.message}
                errors={response.validation_errors}
              />
            )}

          {!loading && !requestError && response?.status === "no_match" && (
            <EmptyState message={response.message} onRelax={handleClear} />
          )}

          {!loading && !requestError && response?.status === "error" && (
            <ErrorBanner title="Pipeline error" message={response.message} />
          )}

          {!loading &&
            !requestError &&
            response?.status === "ok" &&
            response.result && (
              <>
                {response.result.source === "fallback" && <FallbackChip />}
                <SummaryBanner response={response} />
                <div className="space-y-4">
                  {response.result.recommendations.map((rec) => (
                    <RestaurantCard
                      key={rec.id}
                      rec={rec}
                      budget={response.preferences?.budget}
                      source={response.result!.source}
                    />
                  ))}
                </div>
              </>
            )}
        </section>
      </div>

      <p className="mt-6 font-mono text-xs text-secondary">
        {meta.rows.toLocaleString()} restaurants ·{" "}
        {meta.location_options.length.toLocaleString()} locations ·{" "}
        {Math.max(meta.cuisine_options.length - 1, 0).toLocaleString()} cuisines
      </p>
    </div>
  );
}
