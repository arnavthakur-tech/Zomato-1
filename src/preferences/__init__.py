"""Preference schema and validation."""

from src.preferences.schema import (
    PreferenceValidationError,
    UserPreferences,
    VALID_BUDGETS,
    parse_preferences,
)

__all__ = [
    "PreferenceValidationError",
    "UserPreferences",
    "VALID_BUDGETS",
    "parse_preferences",
]
