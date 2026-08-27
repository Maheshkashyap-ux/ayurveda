"""
Ayurveda Intelligence
ML Recommendation Service

Uses the existing trained artifact:

ml/models/final_top5_formulation_ranker.joblib

IMPORTANT:
- Do NOT retrain the model.
- Do NOT use diseases.csv / formulations.csv.
- The trained artifact is the only source for formulation profiles,
  TF-IDF matrices, disease evidence, priors, and model configuration.
- The artifact stores disease evidence inside each profile's
  `diseases` dictionary.
- The artifact stores disease/formulation prior counts using the
  normalized formulation `key`, not the human-readable `formulation`.

This service provides:
- model loading and validation
- model health information
- disease matching
- disease TF-IDF similarity
- patient-context TF-IDF similarity
- formulation/profile similarity
- ingredient similarity
- disease/formulation prior scoring
- hybrid ranking
- API-ready Top-K recommendations
- frontend compatibility through recommend_for_frontend()
"""

from __future__ import annotations

import re
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PATHS
# ============================================================

# This file is:
#
# PROJECT_ROOT/backend/services/ml_recommender.py
#
# Therefore:
#   parents[0] = services
#   parents[1] = backend
#   parents[2] = PROJECT_ROOT

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "final_top5_formulation_ranker.joblib"
)


# ============================================================
# MODEL LOADING
# ============================================================

_model: Optional[Dict[str, Any]] = None
_model_lock = threading.Lock()


def load_model() -> Dict[str, Any]:
    """
    Load the trained Ayurvedic Top-5 ranker.

    The model is loaded once and cached in memory.

    No retraining occurs here.
    No CSV files are loaded here.
    """

    global _model

    if _model is not None:
        return _model

    with _model_lock:
        if _model is not None:
            return _model

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Ayurvedic model artifact was not found:\n"
                f"{MODEL_PATH}"
            )

        loaded_model = joblib.load(MODEL_PATH)

        if not isinstance(loaded_model, dict):
            raise ValueError(
                "Invalid Ayurvedic model artifact. "
                "Expected a dictionary."
            )

        required_keys = [
            "model_version",
            "config",
            "columns",
            "profiles",
            "profile_vectorizer",
            "profile_matrix",
            "disease_vectorizer",
            "disease_matrix",
            "context_vectorizer",
            "context_matrix",
            "ingredient_vectorizer",
            "ingredient_matrix",
            "disease_formulation_counts",
            "disease_total_counts",
            "metrics",
        ]

        missing = [
            key
            for key in required_keys
            if key not in loaded_model
        ]

        if missing:
            raise ValueError(
                "The trained Ayurvedic artifact is missing "
                f"required components: {missing}"
            )

        profiles = loaded_model.get("profiles", [])

        if not isinstance(profiles, list):
            raise ValueError(
                "Invalid Ayurvedic model artifact. "
                "Expected `profiles` to be a list."
            )

        _model = loaded_model

    return _model


# ============================================================
# MODEL INFORMATION
# ============================================================

def get_model_info() -> Dict[str, Any]:
    """
    Return safe model information for the API/frontend.
    """

    model = load_model()

    metrics = model.get("metrics", {})

    return {
        "version": model.get("model_version"),
        "artifact": str(MODEL_PATH),
        "exists": MODEL_PATH.exists(),
        "profiles": len(model.get("profiles", [])),
        "metrics": metrics,
        "config": model.get("config", {}),
        "columns": model.get("columns", {}),
    }

def model_health() -> Dict[str, Any]:
    """
    Backward-compatible health check for ayurveda_api.py.

    Existing API code expects model_health(), while the
    recommender internally exposes get_model_info().
    """
    try:
        info = get_model_info()

        return {
            "status": "ready",
            "artifact": info["artifact"],
            "exists": info["exists"],
            "model_version": info["version"],
            "profiles": info["profiles"],
            "metrics": info["metrics"],
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": "ML recommendation service could not be loaded.",
            "error": str(exc),
        }


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value: Any) -> str:
    """
    Convert arbitrary input into normalized text.
    """

    if value is None:
        return ""

    return str(value).strip().lower()


def clean_text(value: Any) -> str:
    """
    Normalize whitespace while preserving meaningful text.
    """

    text = normalize_text(value)

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# DISEASE MATCHING
# ============================================================

def _profile_diseases(
    profile: Dict[str, Any],
) -> Dict[str, int]:
    """
    Return the disease-count dictionary stored inside a profile.
    """

    diseases = profile.get("diseases", {})

    if hasattr(diseases, "items"):
        result: Dict[str, int] = {}

        for key, value in diseases.items():
            try:
                result[normalize_text(key)] = int(value)
            except (TypeError, ValueError):
                continue

        return result

    return {}


def calculate_exact_disease_scores(
    disease: str,
    profiles: List[Dict[str, Any]],
) -> np.ndarray:
    """
    Calculate the exact-disease signal.

    A formulation receives a positive score when the disease
    exists in the disease Counter stored in its profile.
    """

    query = normalize_text(disease)

    scores = np.zeros(
        len(profiles),
        dtype=float,
    )

    if not query:
        return scores

    for index, profile in enumerate(profiles):
        disease_counts = _profile_diseases(profile)

        if query in disease_counts:
            scores[index] = 1.0

    return scores


# ============================================================
# DISEASE TF-IDF
# ============================================================

def calculate_disease_tfidf_scores(
    disease: str,
    model: Dict[str, Any],
) -> np.ndarray:
    """
    Calculate disease TF-IDF similarity against the
    formulation profiles stored in the trained artifact.
    """

    vectorizer = model["disease_vectorizer"]
    matrix = model["disease_matrix"]

    query = clean_text(disease)

    if not query:
        return np.zeros(
            matrix.shape[0],
            dtype=float,
        )

    query_vector = vectorizer.transform([query])

    return cosine_similarity(
        query_vector,
        matrix,
    )[0]


# ============================================================
# CONTEXT TEXT
# ============================================================

def build_context_text(
    patient: Dict[str, Any],
    columns: Dict[str, Any],
) -> str:
    """
    Build patient-context text for the trained context TF-IDF model.

    The trained artifact uses dataset-style context column names,
    while the frontend/API normally sends snake_case field names.

    This function intentionally supports BOTH formats.

    Examples:

        frontend:
            symptoms
            symptom_severity
            age_group
            gender
            doshas
            constitution

        trained artifact:
            Symptoms
            Symptom Severity
            Age Group
            Gender
            Doshas
            Constitution/Prakriti

    IMPORTANT:
    The artifact remains the only source for the trained model,
    vectorizer and matrix. This function only converts incoming
    patient fields into the text expected by that trained model.
    """

    if not isinstance(patient, dict):
        return ""

    context_columns = columns.get("context", [])

    if not isinstance(context_columns, list):
        context_columns = []

    # ========================================================
    # FRONTEND → TRAINED DATASET COLUMN ALIASES
    # ========================================================

    aliases = {
        "symptoms": "Symptoms",
        "chief_complaint": "Symptoms",

        "diagnosis_tests": "Diagnosis & Tests",

        "symptom_severity": "Symptom Severity",
        "severity": "Symptom Severity",

        "duration": "Duration of Treatment",
        "duration_of_treatment": "Duration of Treatment",

        "medical_history": "Medical History",

        "current_medications": "Current Medications",

        "risk_factors": "Risk Factors",

        "environmental_factors": "Environmental Factors",

        "sleep": "Sleep Patterns",
        "sleep_patterns": "Sleep Patterns",

        "stress_level": "Stress Levels",
        "stress_levels": "Stress Levels",

        "physical_activity": "Physical Activity Levels",
        "physical_activity_levels": "Physical Activity Levels",

        "family_history": "Family History",

        "diet": "Dietary Habits",
        "dietary_habits": "Dietary Habits",

        "allergies": "Allergies (Food/Env)",

        "seasonal_variation": "Seasonal Variation",

        "age_group": "Age Group",

        "gender": "Gender",

        "occupation": "Occupation and Lifestyle",
        "occupation_lifestyle": "Occupation and Lifestyle",

        "cultural_preferences": "Cultural Preferences",

        "herbal_remedies": "Herbal/Alternative Remedies",

        "ayurvedic_herbs": "Ayurvedic Herbs",

        "doshas": "Doshas",

        "constitution": "Constitution/Prakriti",
        "prakriti": "Constitution/Prakriti",

        "diet_lifestyle_recommendations":
            "Diet and Lifestyle Recommendations",

        "yoga_physical_therapy":
            "Yoga & Physical Therapy",

        "medical_intervention":
            "Medical Intervention",

        "patient_recommendations":
            "Patient Recommendations",
    }

    parts: List[str] = []

    # ========================================================
    # 1. FIRST: READ DATASET-STYLE KEYS DIRECTLY
    # ========================================================

    for column in context_columns:

        value = patient.get(column)

        if value is None:
            continue

        # Support lists from API/frontend.
        if isinstance(value, (list, tuple, set)):
            value = " ".join(
                str(item)
                for item in value
                if item is not None
            )

        value = clean_text(value)

        if value:
            parts.append(value)

    # ========================================================
    # 2. SECOND: READ FRONTEND SNAKE_CASE ALIASES
    # ========================================================

    for input_key, dataset_column in aliases.items():

        # If the dataset-style field was already supplied,
        # don't duplicate it through the alias.
        if dataset_column in context_columns:
            direct_value = patient.get(dataset_column)

            if direct_value is not None:
                continue

        value = patient.get(input_key)

        if value is None:
            continue

        # Support arrays such as:
        #
        # symptoms: ["headache", "dizziness"]
        #
        # allergies: ["nuts", "milk"]
        #
        # family_history: ["hypertension"]
        if isinstance(value, (list, tuple, set)):
            value = " ".join(
                str(item)
                for item in value
                if item is not None
            )

        value = clean_text(value)

        if value:
            parts.append(value)

    # ========================================================
    # 3. FALLBACK: ACCEPT COMMON CASE VARIATIONS
    # ========================================================

    # This makes the API tolerant if a frontend sends:
    #
    # Symptoms
    # symptoms
    # SYMPTOMS
    #
    # without changing the trained artifact.

    normalized_patient_keys = {
        normalize_text(key): key
        for key in patient.keys()
    }

    for dataset_column in context_columns:

        normalized_column = normalize_text(
            dataset_column
        )

        actual_key = normalized_patient_keys.get(
            normalized_column
        )

        if actual_key is None:
            continue

        value = patient.get(actual_key)

        if isinstance(value, (list, tuple, set)):
            value = " ".join(
                str(item)
                for item in value
                if item is not None
            )

        value = clean_text(value)

        if value:
            parts.append(value)

    # ========================================================
    # 4. REMOVE DUPLICATES WHILE PRESERVING ORDER
    # ========================================================

    unique_parts: List[str] = []
    seen: Set[str] = set()

    for part in parts:

        normalized_part = clean_text(part)

        if not normalized_part:
            continue

        if normalized_part in seen:
            continue

        seen.add(normalized_part)
        unique_parts.append(normalized_part)

    return " ".join(unique_parts)


# ============================================================
# CONTEXT TF-IDF
# ============================================================

def calculate_context_scores(
    context_text: str,
    model: Dict[str, Any],
) -> np.ndarray:
    """
    Calculate patient-context similarity.
    """

    matrix = model.get("context_matrix")
    vectorizer = model.get("context_vectorizer")

    if matrix is None or vectorizer is None:
        return np.zeros(
            len(model["profiles"]),
            dtype=float,
        )

    if not context_text.strip():
        return np.zeros(
            matrix.shape[0],
            dtype=float,
        )

    query_vector = vectorizer.transform(
        [context_text]
    )

    return cosine_similarity(
        query_vector,
        matrix,
    )[0]


# ============================================================
# INGREDIENT EXTRACTION
# ============================================================

def extract_ingredients(
    formulation: str,
) -> Set[str]:
    """
    Extract approximate ingredient tokens from a formulation.

    This is retained for compatibility and optional
    ingredient/context matching.
    """

    if not formulation:
        return set()

    text = normalize_text(formulation)

    # Remove parenthetical quantities/details.
    text = re.sub(
        r"\([^)]*\)",
        " ",
        text,
    )

    # Split formulation components.
    pieces = re.split(
        r",|;|\+",
        text,
    )

    ingredients: Set[str] = set()

    for piece in pieces:
        piece = piece.strip()

        if not piece:
            continue

        # Remove numeric quantities.
        piece = re.sub(
            r"\b\d+(?:[./]\d+)?\b",
            " ",
            piece,
        )

        # Remove common preparation/measurement words.
        piece = re.sub(
            r"\b("
            r"ml|mg|g|kg|tsp|tbsp|"
            r"cloves?|daily|fresh"
            r")\b",
            " ",
            piece,
        )

        piece = re.sub(
            r"\s+",
            " ",
            piece,
        ).strip()

        if piece:
            ingredients.add(piece)

    return ingredients


# ============================================================
# INGREDIENT TF-IDF
# ============================================================

def calculate_ingredient_scores(
    formulation_query: str,
    model: Dict[str, Any],
) -> np.ndarray:
    """
    Calculate ingredient TF-IDF similarity.

    If the frontend does not provide a formulation query,
    this signal remains zero.
    """

    matrix = model.get("ingredient_matrix")
    vectorizer = model.get("ingredient_vectorizer")

    if matrix is None or vectorizer is None:
        return np.zeros(
            len(model["profiles"]),
            dtype=float,
        )

    query = clean_text(formulation_query)

    if not query:
        return np.zeros(
            matrix.shape[0],
            dtype=float,
        )

    query_vector = vectorizer.transform(
        [query]
    )

    return cosine_similarity(
        query_vector,
        matrix,
    )[0]


# ============================================================
# FORMULATION / PROFILE SIMILARITY
# ============================================================

def calculate_profile_scores(
    query_text: str,
    model: Dict[str, Any],
) -> np.ndarray:
    """
    Calculate formulation profile similarity using the
    profile vectorizer stored in the artifact.
    """

    matrix = model["profile_matrix"]
    vectorizer = model["profile_vectorizer"]

    query = clean_text(query_text)

    if not query:
        return np.zeros(
            matrix.shape[0],
            dtype=float,
        )

    query_vector = vectorizer.transform(
        [query]
    )

    return cosine_similarity(
        query_vector,
        matrix,
    )[0]


# ============================================================
# FORMULATION KEY NORMALIZATION
# ============================================================

def normalize_formulation_key(
    value: Any,
) -> str:
    """
    Normalize a formulation key.

    The trained artifact stores keys such as:

        ashwagandha
        ashwagandha | warm water
        ashwagandha | garlic | warm water
    """

    return clean_text(value)


def get_profile_formulation_key(
    profile: Dict[str, Any],
) -> str:
    """
    Get the normalized formulation key used by the artifact.

    The explicit profile `key` is preferred because it is the
    exact identifier used by disease_formulation_counts.
    """

    key = profile.get("key")

    if key:
        return normalize_formulation_key(key)

    # Compatibility fallback for older artifacts.
    formulation = profile.get(
        "formulation",
        "",
    )

    return normalize_formulation_key(formulation)


# ============================================================
# PRIOR
# ============================================================

def calculate_prior_scores(
    disease: str,
    model: Dict[str, Any],
) -> np.ndarray:
    """
    Calculate formulation prior probability for the requested
    disease using counts saved in the artifact.

    IMPORTANT:

    disease_formulation_counts uses normalized profile keys.

    Example:

        hypertension:
            {
                "ashwagandha | warm water": 5,
                "ashwagandha": 5,
                "ashwagandha | garlic | warm water": 5
            }

    Therefore the human-readable formulation is NOT used
    for dictionary lookup.
    """

    profiles = model["profiles"]

    disease_counts = model.get(
        "disease_formulation_counts",
        {},
    )

    disease_totals = model.get(
        "disease_total_counts",
        {},
    )

    query = normalize_text(disease)

    scores = np.zeros(
        len(profiles),
        dtype=float,
    )

    if not query:
        return scores

    counts_for_disease = disease_counts.get(
        query,
        {},
    )

    total = disease_totals.get(
        query,
        0,
    )

    if not total:
        return scores

    try:
        total_value = float(total)
    except (TypeError, ValueError):
        return scores

    if total_value <= 0:
        return scores

    for index, profile in enumerate(profiles):

        formulation_key = get_profile_formulation_key(
            profile
        )

        count = counts_for_disease.get(
            formulation_key,
            0,
        )

        try:
            count_value = float(count)
        except (TypeError, ValueError):
            count_value = 0.0

        scores[index] = (
            count_value / total_value
        )

    return scores


# ============================================================
# NORMALIZATION
# ============================================================

def safe_normalize_scores(
    scores: np.ndarray,
) -> np.ndarray:
    """
    Normalize a score vector to [0, 1].
    """

    scores = np.asarray(
        scores,
        dtype=float,
    )

    if scores.size == 0:
        return scores

    minimum = scores.min()
    maximum = scores.max()

    if maximum <= minimum:
        return np.zeros_like(scores)

    return (
        (scores - minimum)
        / (maximum - minimum)
    )


# ============================================================
# TOP-K
# ============================================================

def _resolve_top_k(
    requested_top_k: Any,
    config: Dict[str, Any],
) -> int:
    """
    Resolve Top-K while preserving the trained artifact's
    configured default.
    """

    configured_top_k = config.get(
        "top_k",
        5,
    )

    try:
        configured_top_k = int(
            configured_top_k
        )
    except (TypeError, ValueError):
        configured_top_k = 5

    if configured_top_k <= 0:
        configured_top_k = 5

    if requested_top_k is None:
        return configured_top_k

    try:
        requested = int(
            requested_top_k
        )
    except (TypeError, ValueError):
        return configured_top_k

    if requested <= 0:
        return configured_top_k

    return requested


# ============================================================
# MAIN RECOMMENDER
# ============================================================

def recommend(
    disease: str,
    patient_context: Optional[Dict[str, Any]] = None,
    formulation_query: str = "",
    top_k: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate the trained model's Top-K formulation ranking.
    """

    model = load_model()

    profiles = model["profiles"]

    config = model.get(
        "config",
        {},
    )

    columns = model.get(
        "columns",
        {},
    )

    disease = clean_text(disease)

    patient_context = (
        patient_context
        if isinstance(patient_context, dict)
        else {}
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if not disease:
        return {
            "status": "invalid_input",
            "message": (
                "Disease / condition is required."
            ),
            "recommendations": [],
            "model": get_model_info(),
        }

    # --------------------------------------------------------
    # Disease score
    # --------------------------------------------------------

    exact_disease_scores = (
        calculate_exact_disease_scores(
            disease,
            profiles,
        )
    )

    disease_tfidf_scores = (
        calculate_disease_tfidf_scores(
            disease,
            model,
        )
    )

    # --------------------------------------------------------
    # Context score
    # --------------------------------------------------------

    context_text = build_context_text(
        patient_context,
        columns,
    )

    context_scores = (
        calculate_context_scores(
            context_text,
            model,
        )
    )

    # --------------------------------------------------------
    # Profile similarity
    # --------------------------------------------------------

    profile_query = (
        disease
        + " "
        + context_text
    ).strip()

    profile_scores = (
        calculate_profile_scores(
            profile_query,
            model,
        )
    )

    # --------------------------------------------------------
    # Ingredient similarity
    # --------------------------------------------------------

    ingredient_scores = (
        calculate_ingredient_scores(
            formulation_query,
            model,
        )
    )

    # --------------------------------------------------------
    # Prior
    # --------------------------------------------------------

    prior_scores = (
        calculate_prior_scores(
            disease,
            model,
        )
    )

    # --------------------------------------------------------
    # Weights saved inside trained artifact
    # --------------------------------------------------------

    weight_exact_disease = float(
        config.get(
            "weight_exact_disease",
            0.34,
        )
    )

    weight_disease_tfidf = float(
        config.get(
            "weight_disease_tfidf",
            0.22,
        )
    )

    weight_context_tfidf = float(
        config.get(
            "weight_context_tfidf",
            0.16,
        )
    )

    weight_formulation_sim = float(
        config.get(
            "weight_formulation_sim",
            0.10,
        )
    )

    weight_ingredient_sim = float(
        config.get(
            "weight_ingredient_sim",
            0.10,
        )
    )

    weight_prior = float(
        config.get(
            "weight_prior",
            0.08,
        )
    )

    exact_disease_bonus = float(
        config.get(
            "exact_disease_bonus",
            0.10,
        )
    )

    seen_formulation_bonus = float(
        config.get(
            "seen_formulation_bonus",
            0.02,
        )
    )

    # --------------------------------------------------------
    # HYBRID SCORE
    # --------------------------------------------------------

    scores = (
        weight_exact_disease
        * exact_disease_scores
        + weight_disease_tfidf
        * disease_tfidf_scores
        + weight_context_tfidf
        * context_scores
        + weight_formulation_sim
        * profile_scores
        + weight_ingredient_sim
        * ingredient_scores
        + weight_prior
        * prior_scores
    )

    # --------------------------------------------------------
    # Exact disease bonus
    # --------------------------------------------------------

    scores = (
        scores
        + exact_disease_bonus
        * exact_disease_scores
    )

    # --------------------------------------------------------
    # Rank
    # --------------------------------------------------------

    ranked_indices = np.argsort(
        scores
    )[::-1]

    resolved_top_k = _resolve_top_k(
        top_k,
        config,
    )

    results: List[Dict[str, Any]] = []

    for index in ranked_indices:

        index = int(index)

        profile = profiles[index]

        formulation = profile.get(
            "formulation",
            "",
        )

        if not formulation:
            continue

        # ----------------------------------------------------
        # Seen formulation bonus
        # ----------------------------------------------------

        disease_counts = _profile_diseases(
            profile
        )

        seen_bonus = 0.0

        if disease in disease_counts:
            seen_bonus = seen_formulation_bonus

        final_score = (
            float(scores[index])
            + seen_bonus
        )

        # ----------------------------------------------------
        # Disease evidence
        # ----------------------------------------------------

        disease_evidence = float(
            disease_counts.get(
                disease,
                0,
            )
        )

        # ----------------------------------------------------
        # Artifact formulation key
        # ----------------------------------------------------

        formulation_key = (
            get_profile_formulation_key(
                profile
            )
        )

        results.append(
            {
                "rank": len(results) + 1,
                "formulation": formulation,
                "display_name": formulation,

                "score": round(
                    final_score,
                    6,
                ),

                "score_percent": round(
                    final_score * 100.0,
                    2,
                ),

                "disease_match": round(
                    float(
                        exact_disease_scores[index]
                    ),
                    6,
                ),

                "disease_similarity": round(
                    float(
                        disease_tfidf_scores[index]
                    ),
                    6,
                ),

                "context_similarity": round(
                    float(
                        context_scores[index]
                    ),
                    6,
                ),

                "profile_similarity": round(
                    float(
                        profile_scores[index]
                    ),
                    6,
                ),

                "ingredient_similarity": round(
                    float(
                        ingredient_scores[index]
                    ),
                    6,
                ),

                "prior_score": round(
                    float(
                        prior_scores[index]
                    ),
                    6,
                ),

                "disease_evidence": round(
                    disease_evidence,
                    6,
                ),

                # Internal artifact identifier.
                "formulation_key": formulation_key,
            }
        )

        if len(results) >= resolved_top_k:
            break

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "status": "success",
        "query": disease,
        "normalized_term": disease,
        "match_mode": (
            "exact_disease"
            if np.any(
                exact_disease_scores > 0
            )
            else "semantic"
        ),
        "recommendations": results,
        "model": {
            "version": model.get(
                "model_version"
            ),
            "artifact": str(
                MODEL_PATH
            ),
            "profiles": len(profiles),
            "metrics": model.get(
                "metrics",
                {},
            ),
        },
    }


# ============================================================
# BACKWARD-COMPATIBILITY ALIAS
# ============================================================

def get_recommendations(
    disease: str,
    patient_context: Optional[Dict[str, Any]] = None,
    formulation_query: str = "",
    top_k: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Backward-compatible wrapper around recommend().
    """

    return recommend(
        disease=disease,
        patient_context=patient_context,
        formulation_query=formulation_query,
        top_k=top_k,
    )


# ============================================================
# FRONTEND/API COMPATIBILITY FUNCTION
# ============================================================

def recommend_for_frontend(
    query: str = "",
    top_k: Optional[int] = None,
    patient_context: Optional[Dict[str, Any]] = None,
    formulation_query: str = "",
    disease: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Frontend/API compatibility wrapper.

    Existing ayurveda_api.py expects this function.

    Supported input styles:

        recommend_for_frontend(
            query="Hypertension",
            top_k=5,
            patient_context={...}
        )

    or:

        recommend_for_frontend(
            disease="Hypertension",
            top_k=5,
            patient_context={...}
        )

    Additional keyword arguments are tolerated so older API
    callers do not break if they send extra frontend fields.
    """

    # Prefer explicit disease when supplied.
    requested_disease = (
        disease
        if disease is not None
        else query
    )

    # Some API versions may send "condition".
    if not requested_disease:
        requested_disease = kwargs.get(
            "condition",
            "",
        )

    # Some API versions may send "search_query".
    if not requested_disease:
        requested_disease = kwargs.get(
            "search_query",
            "",
        )

    # Some API versions may send "formulation".
    if not formulation_query:
        formulation_query = kwargs.get(
            "formulation",
            "",
        )

    return recommend(
        disease=requested_disease,
        patient_context=patient_context,
        formulation_query=formulation_query,
        top_k=top_k,
    )


# ============================================================
# SIMPLE MODEL TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("AYURVEDA TRAINED MODEL TEST")
    print("=" * 70)

    info = get_model_info()

    print(
        f"Model version : {info['version']}"
    )

    print(
        f"Profiles      : {info['profiles']}"
    )

    print(
        f"Artifact      : {info['artifact']}"
    )

    print()
    print("Metrics:")

    for key, value in info["metrics"].items():
        print(
            f"  {key}: {value}"
        )

    print()
    print("Testing recommendation...")
    print()

    result = recommend_for_frontend(
        query="Hypertension",
        patient_context={
            "symptoms": (
                "High blood pressure, dizziness, "
                "headaches, shortness of breath"
            ),
            "symptom_severity": (
                "Moderate to Severe"
            ),
            "age_group": "Adults",
            "gender": "Both genders",
            "doshas": "Pitta",
            "constitution": "Vata-Kapha",
        },
        top_k=5,
    )

    print(
        f"Status: {result['status']}"
    )

    print(
        f"Disease: {result['query']}"
    )

    print()
    print("TOP-5:")

    for recommendation in result[
        "recommendations"
    ]:

        print(
            f"{recommendation['rank']}. "
            f"{recommendation['formulation']} "
            f"(score={recommendation['score']:.4f}, "
            f"prior={recommendation['prior_score']:.4f}, "
            f"evidence={recommendation['disease_evidence']})"
        )
