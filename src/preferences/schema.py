"""User preference model and validation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

VALID_BUDGETS = frozenset({"low", "medium", "high"})
MIN_RATING_FLOOR = 0.0
MAX_RATING_CEILING = 5.0
MAX_ADDITIONAL_PREFS_CHARS = 1000


class PreferenceValidationError(ValueError):
    """Raised when user preferences fail validation."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        message = "; ".join(errors) if errors else "Invalid preferences"
        super().__init__(message)


@dataclass(frozen=True)
class UserPreferences:
    location: str
    budget: str
    cuisine: str
    min_rating: float
    additional_preferences: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _clean_text(value: object, *, field: str) -> str:
    if value is None:
        raise PreferenceValidationError([f"{field} is required"])
    text = str(value).strip()
    if not text:
        raise PreferenceValidationError([f"{field} is required"])
    return text


def parse_preferences(
    *,
    location: object,
    budget: object,
    cuisine: object,
    min_rating: object,
    additional_preferences: object = "",
) -> UserPreferences:
    """
    Validate and normalize raw preference inputs.

    Required: location, budget, min_rating.
    Optional: cuisine, additional_preferences.
    """
    errors: list[str] = []

    # Location
    location_text = ""
    try:
        location_text = _clean_text(location, field="location")
    except PreferenceValidationError as exc:
        errors.extend(exc.errors)

    # Budget
    budget_text = ""
    if budget is None or str(budget).strip() == "":
        errors.append("budget is required")
    else:
        budget_text = str(budget).strip().lower()
        if budget_text not in VALID_BUDGETS:
            errors.append("budget must be one of: low, medium, high")

    # Cuisine (optional — blank means no cuisine hard filter)
    cuisine_text = "" if cuisine is None else str(cuisine).strip()

    # Min rating
    rating_value: float | None = None
    if min_rating is None or str(min_rating).strip() == "":
        errors.append("min_rating is required")
    else:
        try:
            rating_value = float(min_rating)
        except (TypeError, ValueError):
            errors.append("min_rating must be a number")
        else:
            if not (MIN_RATING_FLOOR <= rating_value <= MAX_RATING_CEILING):
                errors.append(
                    f"min_rating must be between {MIN_RATING_FLOOR} and {MAX_RATING_CEILING}"
                )

    # Additional preferences (optional)
    extra = "" if additional_preferences is None else str(additional_preferences).strip()
    if len(extra) > MAX_ADDITIONAL_PREFS_CHARS:
        extra = extra[:MAX_ADDITIONAL_PREFS_CHARS]

    if errors:
        raise PreferenceValidationError(errors)

    assert rating_value is not None
    return UserPreferences(
        location=location_text,
        budget=budget_text,
        cuisine=cuisine_text,
        min_rating=rating_value,
        additional_preferences=extra,
    )
