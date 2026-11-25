export type Budget = "low" | "medium" | "high";

export interface MetaResponse {
  rows: number;
  location_options: string[];
  cuisine_options: string[];
  default_location: string;
  llm_model: string;
  llm_configured: boolean;
  any_cuisine_label: string;
}

export interface RecommendRequest {
  location: string;
  budget: Budget;
  cuisine: string;
  min_rating: number;
  additional_preferences: string;
  max_recommendations: number;
  use_llm: boolean;
}

export interface Recommendation {
  id: string;
  name: string;
  cuisine: string;
  rating: number | null;
  estimated_cost: number | null;
  rank: number;
  explanation: string;
}

export interface RecommendationResult {
  summary: string;
  recommendations: Recommendation[];
  source: "llm" | "fallback" | string;
  raw_response?: string | null;
  parse_notes?: string[];
}

export interface Preferences {
  location: string;
  budget: Budget;
  cuisine: string;
  min_rating: number;
  additional_preferences: string;
}

export interface RecommendResponse {
  status: "ok" | "no_match" | "validation_error" | "error";
  message: string;
  preferences: Preferences | null;
  total_matches: number;
  candidate_count: number;
  candidate_cap: number;
  result: RecommendationResult | null;
  validation_errors: string[];
  meta: Record<string, unknown>;
}

export const BUDGET_LABELS: Record<Budget, string> = {
  low: "Low (₹)",
  medium: "Medium (₹₹)",
  high: "High (₹₹₹)",
};

export const BUDGET_ORDER: Budget[] = ["low", "medium", "high"];
