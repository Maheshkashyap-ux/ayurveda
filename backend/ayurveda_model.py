"""
Ayurveda Intelligence
Trained Top-5 Formulation Model Adapter

IMPORTANT:
    This module loads ONLY the trained model artifact:

        ../ml/models/final_top5_formulation_ranker.joblib

    It does NOT use the old diseases.csv / formulations.csv
    recommendation engine.

    The artifact contains:
        - 48 formulation profiles
        - disease TF-IDF matrix
        - context TF-IDF matrix
        - formulation/profile TF-IDF matrix
        - ingredient TF-IDF matrix
        - disease/formulation priors
        - trained ranking configuration
        - evaluation metrics
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import re
import joblib
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PATHS
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parent
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

_model = None


def load_model():
    """
    Load the trained Ayurvedic Top-5 ranker.

    The model is loaded once and cached in memory.
    """

    global _model

    if _model is None:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Ayurvedic model artifact was not found:\n"
                f"{MODEL_PATH}"
            )

        _model = joblib.load(MODEL_PATH)

        if not isinstance(_model, dict):
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
            if key not in _model
        ]

        if missing:
            raise ValueError(
                "The trained Ayurvedic artifact is missing "
                f"required components: {missing}"
            )

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
        text
    )

    return text.strip()


# ============================================================
# DISEASE MATCHING
# ============================================================

def _profile_diseases(profile: Dict[str, Any]) -> Dict[str, int]:
    """
    Return the disease-count dictionary stored inside a profile.
    """

    diseases = profile.get("diseases", {})

    if hasattr(diseases, "items"):
        return {
            normalize_text(key): int(value)
            for key, value in diseases.items()
        }

    return {}


def calculate_exact_disease_scores(
    disease: str,
    profiles: List[Dict[str, Any]]
) -> np.ndarray:
    """
    Calculate the exact-disease signal.

    A formulation receives a positive score when the disease
    exists in the disease Counter stored in its profile.
    """

    query = normalize_text(disease)

    scores = np.zeros(
        len(profiles),
        dtype=float
    )

    if not query:
        return scores

    for index, profile in enumerate(profiles):

        disease_counts = _profile_diseases(
            profile
        )

        if query in disease_counts:
            scores[index] = 1.0

    return scores


# ============================================================
# DISEASE TF-IDF
# ============================================================

def calculate_disease_tfidf_scores(
    disease: str,
    model: Dict[str, Any]
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
            dtype=float
        )

    query_vector = vectorizer.transform(
        [query]
    )

    return cosine_similarity(
        query_vector,
        matrix
    )[0]


# ============================================================
# CONTEXT TEXT
# ============================================================

def build_context_text(
    patient: Dict[str, Any],
    columns: Dict[str, Any]
) -> str:
    """
    Build the same style of combined patient context used
    by the trained model.

    Accepts frontend-friendly snake_case as well as the
    original dataset column names.
    """

    context_columns = columns.get(
        "context",
        []
    )

    parts = []

    # --------------------------------------------------------
    # Direct dataset column names
    # --------------------------------------------------------

    for column in context_columns:

        value = patient.get(column)

        if value is not None:

            value = clean_text(value)

            if value:
                parts.append(value)

    # --------------------------------------------------------
    # Frontend-friendly aliases
    # --------------------------------------------------------

    aliases = {
        "symptoms": "Symptoms",
        "diagnosis_tests": "Diagnosis & Tests",
        "symptom_severity": "Symptom Severity",
        "duration_of_treatment": "Duration of Treatment",
        "medical_history": "Medical History",
        "current_medications": "Current Medications",
        "risk_factors": "Risk Factors",
        "environmental_factors": "Environmental Factors",
        "sleep_patterns": "Sleep Patterns",
        "stress_levels": "Stress Levels",
        "physical_activity_levels": "Physical Activity Levels",
        "family_history": "Family History",
        "dietary_habits": "Dietary Habits",
        "allergies": "Allergies (Food/Env)",
        "seasonal_variation": "Seasonal Variation",
        "age_group": "Age Group",
        "gender": "Gender",
        "occupation_lifestyle": "Occupation and Lifestyle",
        "cultural_preferences": "Cultural Preferences",
        "herbal_remedies": "Herbal/Alternative Remedies",
        "ayurvedic_herbs": "Ayurvedic Herbs",
        "doshas": "Doshas",
        "constitution": "Constitution/Prakriti",
        "diet_lifestyle_recommendations":
            "Diet and Lifestyle Recommendations",
        "yoga_physical_therapy":
            "Yoga & Physical Therapy",
        "medical_intervention":
            "Medical Intervention",
        "patient_recommendations":
            "Patient Recommendations",
    }

    for input_key, dataset_column in aliases.items():

        if dataset_column in context_columns:
            continue

        value = patient.get(input_key)

        if value is not None:

            value = clean_text(value)

            if value:
                parts.append(value)

    return " ".join(parts)


# ============================================================
# CONTEXT TF-IDF
# ============================================================

def calculate_context_scores(
    context_text: str,
    model: Dict[str, Any]
) -> np.ndarray:
    """
    Calculate patient-context similarity.
    """

    matrix = model.get(
        "context_matrix"
    )

    vectorizer = model.get(
        "context_vectorizer"
    )

    if matrix is None or vectorizer is None:

        return np.zeros(
            len(model["profiles"]),
            dtype=float
        )

    if not context_text.strip():

        return np.zeros(
            matrix.shape[0],
            dtype=float
        )

    query_vector = vectorizer.transform(
        [context_text]
    )

    return cosine_similarity(
        query_vector,
        matrix
    )[0]


# ============================================================
# INGREDIENT EXTRACTION
# ============================================================

def extract_ingredients(
    formulation: str
) -> set:
    """
    Extract approximate ingredient tokens from a formulation.

    This is used only for optional ingredient/context matching.
    """

    if not formulation:
        return set()

    text = normalize_text(
        formulation
    )

    # Remove quantities.
    text = re.sub(
        r"\([^)]*\)",
        " ",
        text
    )

    # Split formulation components.
    pieces = re.split(
        r",|;|\+",
        text
    )

    ingredients = set()

    for piece in pieces:

        piece = piece.strip()

        if not piece:
            continue

        # Remove common preparation words.
        piece = re.sub(
            r"\b\d+([./]\d+)?\b",
            " ",
            piece
        )

        piece = re.sub(
            r"\b(ml|mg|g|tsp|tbsp|daily|cloves?|fresh)\b",
            " ",
            piece
        )

        piece = re.sub(
            r"\s+",
            " ",
            piece
        ).strip()

        if piece:
            ingredients.add(piece)

    return ingredients


# ============================================================
# INGREDIENT TF-IDF
# ============================================================

def calculate_ingredient_scores(
    formulation_query: str,
    model: Dict[str, Any]
) -> np.ndarray:
    """
    Calculate ingredient TF-IDF similarity.

    If the frontend does not provide a formulation query,
    this signal remains zero.
    """

    matrix = model.get(
        "ingredient_matrix"
    )

    vectorizer = model.get(
        "ingredient_vectorizer"
    )

    if matrix is None or vectorizer is None:

        return np.zeros(
            len(model["profiles"]),
            dtype=float
        )

    query = clean_text(
        formulation_query
    )

    if not query:

        return np.zeros(
            matrix.shape[0],
            dtype=float
        )

    query_vector = vectorizer.transform(
        [query]
    )

    return cosine_similarity(
        query_vector,
        matrix
    )[0]


# ============================================================
# FORMULATION / PROFILE SIMILARITY
# ============================================================

def calculate_profile_scores(
    query_text: str,
    model: Dict[str, Any]
) -> np.ndarray:
    """
    Calculate formulation profile similarity using the
    profile vectorizer stored in the artifact.
    """

    matrix = model["profile_matrix"]
    vectorizer = model["profile_vectorizer"]

    query = clean_text(
        query_text
    )

    if not query:

        return np.zeros(
            matrix.shape[0],
            dtype=float
        )

    query_vector = vectorizer.transform(
        [query]
    )

    return cosine_similarity(
        query_vector,
        matrix
    )[0]


# ============================================================
# PRIOR
# ============================================================

def calculate_prior_scores(
    disease: str,
    model: Dict[str, Any]
) -> np.ndarray:
    """
    Calculate formulation prior probability for the requested
    disease using the counts saved in the artifact.
    """

    profiles = model["profiles"]

    disease_counts = model.get(
        "disease_formulation_counts",
        {}
    )

    disease_totals = model.get(
        "disease_total_counts",
        {}
    )

    query = normalize_text(
        disease
    )

    scores = np.zeros(
        len(profiles),
        dtype=float
    )

    if not query:
        return scores

    counts_for_disease = disease_counts.get(
        query,
        {}
    )

    total = disease_totals.get(
        query,
        0
    )

    if not total:
        return scores

    for index, profile in enumerate(profiles):

        formulation = profile.get(
            "formulation",
            ""
        )

        count = counts_for_disease.get(
            formulation,
            0
        )

        scores[index] = (
            float(count) / float(total)
        )

    return scores


# ============================================================
# NORMALIZATION
# ============================================================

def safe_normalize_scores(
    scores: np.ndarray
) -> np.ndarray:
    """
    Normalize a score vector to [0, 1].
    """

    scores = np.asarray(
        scores,
        dtype=float
    )

    if scores.size == 0:
        return scores

    minimum = scores.min()
    maximum = scores.max()

    if maximum <= minimum:
        return np.zeros_like(
            scores
        )

    return (
        scores - minimum
    ) / (
        maximum - minimum
    )


# ============================================================
# MAIN RECOMMENDER
# ============================================================

def recommend(
    disease: str,
    patient_context: Optional[Dict[str, Any]] = None,
    formulation_query: str = ""
) -> Dict[str, Any]:
    """
    Generate the trained model's Top-5 formulation ranking.

    Parameters
    ----------
    disease:
        Disease / condition supplied by the user.

    patient_context:
        Optional patient/context fields.

    formulation_query:
        Optional formulation/ingredient query.

    Returns
    -------
    dict
        API-ready Top-5 recommendation response.
    """

    model = load_model()

    profiles = model["profiles"]

    config = model.get(
        "config",
        {}
    )

    columns = model.get(
        "columns",
        {}
    )

    disease = clean_text(
        disease
    )

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
            "message": "Disease / condition is required.",
            "recommendations": [],
            "model": get_model_info(),
        }

    # --------------------------------------------------------
    # Disease score
    # --------------------------------------------------------

    exact_disease_scores = (
        calculate_exact_disease_scores(
            disease,
            profiles
        )
    )

    disease_tfidf_scores = (
        calculate_disease_tfidf_scores(
            disease,
            model
        )
    )

    # --------------------------------------------------------
    # Context score
    # --------------------------------------------------------

    context_text = build_context_text(
        patient_context,
        columns
    )

    context_scores = (
        calculate_context_scores(
            context_text,
            model
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
            model
        )
    )

    # --------------------------------------------------------
    # Ingredient similarity
    # --------------------------------------------------------

    ingredient_scores = (
        calculate_ingredient_scores(
            formulation_query,
            model
        )
    )

    # --------------------------------------------------------
    # Prior
    # --------------------------------------------------------

    prior_scores = (
        calculate_prior_scores(
            disease,
            model
        )
    )

    # --------------------------------------------------------
    # Weights saved inside the trained artifact
    # --------------------------------------------------------

    weight_exact_disease = float(
        config.get(
            "weight_exact_disease",
            0.34
        )
    )

    weight_disease_tfidf = float(
        config.get(
            "weight_disease_tfidf",
            0.22
        )
    )

    weight_context_tfidf = float(
        config.get(
            "weight_context_tfidf",
            0.16
        )
    )

    weight_formulation_sim = float(
        config.get(
            "weight_formulation_sim",
            0.10
        )
    )

    weight_ingredient_sim = float(
        config.get(
            "weight_ingredient_sim",
            0.10
        )
    )

    weight_prior = float(
        config.get(
            "weight_prior",
            0.08
        )
    )

    exact_disease_bonus = float(
        config.get(
            "exact_disease_bonus",
            0.10
        )
    )

    seen_formulation_bonus = float(
        config.get(
            "seen_formulation_bonus",
            0.02
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

    # Exact disease bonus.
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

    top_k = int(
        config.get(
            "top_k",
            5
        )
    )

    results = []

    for index in ranked_indices:

        profile = profiles[
            int(index)
        ]

        formulation = profile.get(
            "formulation",
            ""
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

        results.append(
            {
                "rank": len(results) + 1,
                "formulation": formulation,
                "score": round(
                    final_score,
                    6
                ),
                "disease_match": round(
                    float(
                        exact_disease_scores[index]
                    ),
                    6
                ),
                "disease_similarity": round(
                    float(
                        disease_tfidf_scores[index]
                    ),
                    6
                ),
                "context_similarity": round(
                    float(
                        context_scores[index]
                    ),
                    6
                ),
                "profile_similarity": round(
                    float(
                        profile_scores[index]
                    ),
                    6
                ),
                "ingredient_similarity": round(
                    float(
                        ingredient_scores[index]
                    ),
                    6
                ),
                "prior_score": round(
                    float(
                        prior_scores[index]
                    ),
                    6
                ),
            }
        )

        if len(results) >= top_k:
            break

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "status": "success",
        "query": disease,
        "recommendations": results,
        "model": {
            "version": model.get(
                "model_version"
            ),
            "artifact": str(
                MODEL_PATH
            ),
            "profiles": len(
                profiles
            ),
            "metrics": model.get(
                "metrics",
                {}
            ),
        },
    }


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

    result = recommend(
        disease="Hypertension",
        patient_context={
            "symptoms": (
                "High blood pressure, dizziness, "
                "headaches, shortness of breath"
            ),
            "symptom_severity": "Moderate to Severe",
            "age_group": "Adults",
            "gender": "Both genders",
            "doshas": "Pitta",
            "constitution": "Vata-Kapha",
        }
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
            f"(score={recommendation['score']:.4f})"
        )
