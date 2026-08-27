"""
Ayurveda Intelligence
ML Recommendation Engine

This module is the bridge between the trained ML artifact
and the FastAPI backend.

IMPORTANT:

The backend does NOT retrain the model.

The backend loads:

    ml/models/final_top5_formulation_ranker.joblib

and uses the artifact to generate Top-5 formulation
recommendations.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from config import (
    MODEL_PATH,
    MAX_RECOMMENDATIONS,
    FRONTEND_RECOMMENDATIONS,
    DISCLAIMER,
)


# ============================================================
# GLOBAL MODEL CACHE
# ============================================================

_MODEL_BUNDLE: Any = None


# ============================================================
# TEXT UTILITIES
# ============================================================

def normalize_text(value: Any) -> str:
    """
    Normalize text for matching.
    """

    if value is None:
        return ""

    text = str(value)

    text = text.replace("\n", " ")
    text = text.replace("\r", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()


def clean_display_text(value: Any) -> str:
    """
    Convert model output into clean frontend text.
    """

    if value is None:
        return ""

    text = str(value)

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# INGREDIENT EXTRACTION
# ============================================================

def extract_ingredients(formulation: str) -> set[str]:
    """
    Extract approximate ingredient names from a formulation.

    This intentionally ignores quantities such as:

        (5g)
        (2 tsp)
        (200ml)

    Example:

        Ashwagandha (5g), Brahmi (2g), Warm water (200ml)

    becomes approximately:

        {
            "ashwagandha",
            "brahmi",
            "warm water"
        }
    """

    if not formulation:
        return set()

    text = formulation.lower()

    # Remove parenthetical quantities/details.
    text = re.sub(
        r"\([^)]*\)",
        "",
        text
    )

    # Split formulation.
    parts = re.split(
        r",|;|\+|\band\b",
        text
    )

    ingredients = set()

    for part in parts:

        part = part.strip()

        if not part:
            continue

        # Remove common preparation instructions.
        part = re.sub(
            r"\b(daily|fresh|as needed|apply on skin|"
            r"consume|in water|with water)\b",
            "",
            part,
            flags=re.IGNORECASE
        )

        part = re.sub(
            r"\s+",
            " ",
            part
        ).strip()

        if len(part) >= 2:
            ingredients.add(part)

    return ingredients


def calculate_ingredient_match(
    actual: str,
    recommended: str,
) -> float:
    """
    Calculate ingredient overlap percentage.

    The score is:

        intersection / actual ingredients * 100
    """

    actual_ingredients = extract_ingredients(actual)

    recommended_ingredients = extract_ingredients(
        recommended
    )

    if not actual_ingredients:
        return 0.0

    overlap = (
        actual_ingredients
        & recommended_ingredients
    )

    return round(
        len(overlap) / len(actual_ingredients) * 100,
        1
    )


# ============================================================
# MODEL LOADING
# ============================================================

def load_model():
    """
    Load the final trained model artifact.

    The artifact is cached after the first load.
    """

    global _MODEL_BUNDLE

    if _MODEL_BUNDLE is not None:
        return _MODEL_BUNDLE

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            "\nFinal ML model was not found.\n\n"
            f"Expected:\n{MODEL_PATH}\n\n"
            "Run ml/train_model.py first."
        )

    print()
    print("=" * 70)
    print("Loading Ayurveda ML model")
    print("=" * 70)
    print()
    print(f"Model: {MODEL_PATH}")
    print()

    _MODEL_BUNDLE = joblib.load(
        MODEL_PATH
    )

    print("Model loaded successfully.")

    if isinstance(_MODEL_BUNDLE, dict):

        print(
            "Artifact keys:"
        )

        for key in _MODEL_BUNDLE.keys():
            print(
                f"  - {key}"
            )

    print()

    return _MODEL_BUNDLE


# ============================================================
# ARTIFACT HELPERS
# ============================================================

def _get_from_dict(
    bundle: dict,
    possible_names: list[str],
):
    """
    Find a value using multiple possible artifact key names.
    """

    for name in possible_names:

        if name in bundle:

            return bundle[name]

    return None


def _get_formulations(bundle):
    """
    Locate formulation records inside the trained artifact.
    """

    if not isinstance(bundle, dict):
        return None

    return _get_from_dict(
        bundle,
        [
            "formulations",
            "formulation_profiles",
            "formulation_records",
            "profiles",
            "candidates",
            "formulation_data",
        ]
    )


def _get_vectorizer(bundle):
    """
    Locate the trained vectorizer.
    """

    if not isinstance(bundle, dict):
        return None

    return _get_from_dict(
        bundle,
        [
            "vectorizer",
            "tfidf_vectorizer",
            "profile_vectorizer",
        ]
    )


def _get_matrix(bundle):
    """
    Locate the trained formulation/profile matrix.
    """

    if not isinstance(bundle, dict):
        return None

    return _get_from_dict(
        bundle,
        [
            "formulation_matrix",
            "profile_matrix",
            "tfidf_matrix",
            "formulation_vectors",
            "profile_vectors",
        ]
    )


# ============================================================
# FORMULATION NAME EXTRACTION
# ============================================================

def _formulation_name(record: Any) -> str:
    """
    Extract formulation display text from an artifact record.
    """

    if isinstance(record, str):

        return clean_display_text(record)

    if isinstance(record, dict):

        for key in [
            "Formulation",
            "formulation",
            "name",
            "formulation_name",
            "text",
        ]:

            if key in record:

                value = record[key]

                if value is not None:

                    return clean_display_text(value)

    return clean_display_text(record)


# ============================================================
# DISEASE MATCHING
# ============================================================

def _record_disease(record: Any) -> str:

    if not isinstance(record, dict):
        return ""

    for key in [
        "Disease",
        "disease",
        "condition",
        "disease_name",
        "canonical_name",
    ]:

        if key in record:

            return clean_display_text(
                record[key]
            )

    return ""


def _find_disease_profiles(
    query: str,
    records,
):
    """
    Find records belonging to the requested disease.

    Exact disease matching is deliberately preferred because
    the frontend will normally send a condition such as:

        Leigh Syndrome
        Depression
        Cold
        Rheumatoid Arthritis
    """

    query_norm = normalize_text(query)

    exact = []

    for record in records:

        disease = normalize_text(
            _record_disease(record)
        )

        if disease == query_norm:

            exact.append(record)

    if exact:
        return exact

    # Partial matching.
    partial = []

    for record in records:

        disease = normalize_text(
            _record_disease(record)
        )

        if (
            query_norm in disease
            or disease in query_norm
        ):

            partial.append(record)

    return partial


# ============================================================
# MODEL RECOMMENDATION
# ============================================================

def _recommend_from_artifact(
    query: str,
    bundle: dict,
):
    """
    Generate recommendations from the saved artifact.

    This function supports the artifact structure produced by
    the final training pipeline.
    """

    formulations = _get_formulations(
        bundle
    )

    vectorizer = _get_vectorizer(
        bundle
    )

    matrix = _get_matrix(
        bundle
    )

    # --------------------------------------------------------
    # Direct precomputed ranking support
    # --------------------------------------------------------

    if "recommend" in bundle:

        recommender = bundle["recommend"]

        if callable(recommender):

            result = recommender(
                query
            )

            return result

    # --------------------------------------------------------
    # No formulation data
    # --------------------------------------------------------

    if formulations is None:

        raise RuntimeError(
            "The trained model artifact does not contain "
            "formulation profiles.\n\n"
            "Available artifact keys:\n"
            + (
                "\n".join(
                    f" - {key}"
                    for key in bundle.keys()
                )
                if isinstance(bundle, dict)
                else str(type(bundle))
            )
        )

    # --------------------------------------------------------
    # If records have explicit disease information,
    # prefer those belonging to the requested disease.
    # --------------------------------------------------------

    disease_records = _find_disease_profiles(
        query,
        formulations
    )

    candidate_records = (
        disease_records
        if disease_records
        else formulations
    )

    # --------------------------------------------------------
    # If vectorizer + matrix exist, use TF-IDF similarity.
    # --------------------------------------------------------

    if (
        vectorizer is not None
        and matrix is not None
    ):

        texts = []

        for record in candidate_records:

            if isinstance(record, dict):

                text = " ".join(
                    str(
                        value
                    )
                    for value in record.values()
                    if value is not None
                )

            else:

                text = str(record)

            texts.append(text)

        query_vector = vectorizer.transform(
            [query]
        )

        candidate_matrix = matrix

        # If the matrix belongs to all formulations,
        # align it with the selected records where possible.
        if len(candidate_records) != len(formulations):

            full_indices = []

            for candidate in candidate_records:

                try:
                    index = formulations.index(
                        candidate
                    )
                    full_indices.append(index)

                except ValueError:
                    pass

            if len(full_indices) == len(
                candidate_records
            ):

                candidate_matrix = matrix[
                    full_indices
                ]

        try:

            from sklearn.metrics.pairwise import (
                cosine_similarity
            )

            scores = cosine_similarity(
                query_vector,
                candidate_matrix
            )[0]

        except Exception:

            scores = np.zeros(
                len(candidate_records)
            )

        ranked_indices = np.argsort(
            scores
        )[::-1]

        results = []

        for index in ranked_indices[
            :MAX_RECOMMENDATIONS
        ]:

            record = candidate_records[
                int(index)
            ]

            name = _formulation_name(
                record
            )

            results.append(
                {
                    "formulation": name,
                    "score": round(
                        float(scores[index]),
                        4
                    ),
                    "record": record,
                }
            )

        return results

    # --------------------------------------------------------
    # Artifact contains already-ranked candidates.
    # --------------------------------------------------------

    results = []

    for record in candidate_records[
        :MAX_RECOMMENDATIONS
    ]:

        if isinstance(record, dict):

            score = record.get(
                "score",
                record.get(
                    "similarity",
                    record.get(
                        "rank_score",
                        0
                    )
                )
            )

        else:

            score = 0

        results.append(
            {
                "formulation": _formulation_name(
                    record
                ),
                "score": float(
                    score or 0
                ),
                "record": record,
            }
        )

    return results


# ============================================================
# PUBLIC RECOMMEND FUNCTION
# ============================================================

def recommend(
    query: str,
    limit: int = FRONTEND_RECOMMENDATIONS,
):
    """
    Public recommendation API.

    Returns a frontend-friendly response.
    """

    query = clean_display_text(
        query
    )

    if not query:

        return {
            "status": "invalid_input",
            "query": query,
            "condition": None,
            "recommendations": [],
            "message": "Please enter a disease or condition.",
            "disclaimer": DISCLAIMER,
        }

    bundle = load_model()

    if not isinstance(bundle, dict):

        raise RuntimeError(
            "The final model artifact must be a dictionary "
            "containing the trained recommendation components."
        )

    raw_results = _recommend_from_artifact(
        query,
        bundle
    )

    if raw_results is None:

        raw_results = []

    # Handle direct recommender output.
    if isinstance(raw_results, dict):

        if "recommendations" in raw_results:

            raw_results = raw_results[
                "recommendations"
            ]

        else:

            raw_results = [
                raw_results
            ]

    recommendations = []

    for rank, item in enumerate(
        raw_results[:MAX_RECOMMENDATIONS],
        start=1
    ):

        if isinstance(item, dict):

            formulation = (
                item.get("formulation")
                or item.get("name")
                or item.get("Formulation")
                or ""
            )

            score = float(
                item.get(
                    "score",
                    item.get(
                        "similarity",
                        item.get(
                            "match_score",
                            0
                        )
                    )
                ) or 0
            )

            record = item.get(
                "record",
                item
            )

        else:

            formulation = str(
                item
            )

            score = 0.0

            record = item

        formulation = clean_display_text(
            formulation
        )

        if not formulation:
            continue

        recommendations.append(
            {
                "rank": rank,
                "formulation": formulation,
                "score": round(
                    score,
                    4
                ),
                "ingredient_match": None,
                "ingredient_match_label": "—",
                "record": record,
            }
        )

    # --------------------------------------------------------
    # Important:
    #
    # The ML artifact gives relevance/ranking.
    # Ingredient match is only a transparent overlap metric.
    # It is NOT a medical confidence score.
    # --------------------------------------------------------

    if recommendations:

        # If the artifact includes an actual formulation
        # reference, compare recommendations against the
        # strongest candidate where available.
        reference = recommendations[0][
            "formulation"
        ]

        for item in recommendations:

            match = calculate_ingredient_match(
                reference,
                item["formulation"]
            )

            item[
                "ingredient_match"
            ] = match

            item[
                "ingredient_match_label"
            ] = f"{match:.1f}%"

    return {
        "status": "success" if recommendations else "no_match",

        "query": query,

        "condition": query,

        "recommendations": recommendations[
            :limit
        ],

        "model": {
            "artifact": MODEL_PATH.name,
            "max_candidates": MAX_RECOMMENDATIONS,
        },

        "message": (
            "Top Ayurvedic formulation candidates "
            "generated by the trained ML model."
            if recommendations
            else
            "No formulation candidates were returned "
            "for this query."
        ),

        "disclaimer": DISCLAIMER,
    }


# ============================================================
# MODEL STATUS
# ============================================================

def get_model_status():

    bundle = load_model()

    if isinstance(bundle, dict):

        keys = list(
            bundle.keys()
        )

    else:

        keys = []

    return {
        "loaded": True,
        "path": str(MODEL_PATH),
        "exists": MODEL_PATH.exists(),
        "artifact_type": type(bundle).__name__,
        "artifact_keys": keys,
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("AYURVEDA INTELLIGENCE — MODEL TEST")
    print("=" * 70)

    print()

    print(
        get_model_status()
    )

    print()

    test_queries = [
        "Leigh Syndrome",
        "Depression",
        "Cold",
        "Rheumatoid Arthritis",
    ]

    for query in test_queries:

        print()
        print("-" * 70)
        print(
            f"Query: {query}"
        )
        print("-" * 70)

        try:

            result = recommend(
                query
            )

            for item in result[
                "recommendations"
            ]:

                print(
                    f"{item['rank']}. "
                    f"{item['formulation']}"
                )

                print(
                    f"   Score: "
                    f"{item['score']}"
                )

                print(
                    f"   Ingredient overlap: "
                    f"{item['ingredient_match_label']}"
                )

        except Exception as error:

            print(
                "ERROR:"
            )

            print(
                error
            )
