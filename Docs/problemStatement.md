# Problem Statement — Zomato Restaurant Recommendation System

## Overview

Build an intelligent restaurant recommendation system that uses the Zomato dataset and a Large Language Model (LLM) to deliver personalized, human-like restaurant suggestions based on user preferences.

The system should not only filter restaurants by hard constraints (location, budget, cuisine, rating) but also reason about softer preferences and explain *why* each recommendation fits the user.

## Goals

- Load and preprocess restaurant data from the Zomato dataset hosted on Hugging Face.
- Collect structured user preferences (location, budget, cuisine, rating, and free-form needs).
- Filter candidate restaurants, then use an LLM to rank and explain recommendations.
- Present clear, useful results that feel personalized rather than purely rule-based.

## Core Features

1. **LLM-powered recommendations** — Generate personalized, human-like restaurant suggestions with reasoning.
2. **Preference-aware filtering** — Narrow the dataset using location, budget, cuisine, and minimum rating before LLM ranking.
3. **Explainable output** — Show why each recommended restaurant matches the user’s needs.
4. **Clear result display** — Present recommendations in a readable, user-friendly format.

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face.
- Extract relevant fields such as:
  - Restaurant name
  - Location
  - Cuisine
  - Cost
  - Rating

### 2. User Input

Collect user preferences:

| Preference | Examples |
|---|---|
| Location | Bangalore |
| Budget | low, medium, high |
| Cuisine | Italian, Chinese |
| Minimum rating | e.g. 4.0+ |
| Additional preferences | family-friendly, quick service |

### 3. Integration Layer

- Filter and prepare relevant restaurant data based on user input.
- Pass structured results into an LLM prompt.
- Design a prompt that helps the LLM reason about fit and rank options.

### 4. Recommendation Engine

Use the LLM to:

- Rank restaurants according to user preferences
- Provide explanations for why each recommendation fits
- Optionally summarize the overall set of choices

### 5. Output Display

Present top recommendations in a user-friendly format including:

- Restaurant name
- Cuisine
- Rating
- Estimated cost
- AI-generated explanation

## Expected Outcome

A working end-to-end recommendation pipeline where:

1. Raw Zomato data is cleaned and structured.
2. User preferences constrain the candidate set.
3. An LLM ranks and explains the best matches.
4. The user receives actionable, personalized restaurant suggestions.

## Project Scope Notes

- This project focuses on **recommendation quality and explanation**, not on building a full food-delivery marketplace.
- The Hugging Face Zomato dataset is the primary data source.
- The LLM is used for ranking, reasoning, and natural-language explanations after deterministic filtering.
