"""
FINAL Ayurvedic Formulation Recommender
---------------------------------------

Run from the project root:

    python ml/train_model.py

Expected data:
    data/processed/train.csv
    data/processed/test.csv

Optional:
    data/processed/train_augmented.csv
    data/processed/test_augmented.csv

Uses:
    pandas
    numpy
    scikit-learn
    joblib

This version:
- Uses robust project-relative paths
- Automatically finds augmented datasets
- Automatically detects Disease/Formulation columns
- Uses all training observations
- Filters obvious non-formulation recommendations
- Canonicalizes ingredient order
- Uses disease evidence
- Uses disease TF-IDF similarity
- Uses context similarity
- Uses formulation similarity
- Uses ingredient similarity
- Uses empirical disease -> formulation priors
- Produces ONLY Top-5 recommendations
- Saves a single backend model artifact
- Saves CSV evaluation
- Saves frontend-ready JSON

IMPORTANT:
This is a recommendation/ranking model for a project/demo.
It is not a clinical decision system and should not be used to prescribe treatment.
"""

from __future__ import annotations

import json
import re
import warnings
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

import joblib
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


warnings.filterwarnings("ignore")


# ============================================================
# PATHS
# ============================================================

THIS_FILE = Path(__file__).resolve()

PROJECT_ROOT = THIS_FILE.parent.parent

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

MODEL_DIR = PROJECT_ROOT / "ml" / "models"
RESULT_DIR = PROCESSED_DIR

MODEL_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)


TRAIN_CANDIDATES = [
    PROCESSED_DIR / "train_augmented.csv",
    PROCESSED_DIR / "train.csv",
]

TEST_CANDIDATES = [
    PROCESSED_DIR / "test_augmented.csv",
    PROCESSED_DIR / "test.csv",
]


MODEL_PATH = (
    MODEL_DIR /
    "final_top5_formulation_ranker.joblib"
)

RESULT_CSV = (
    RESULT_DIR /
    "final_top5_results.csv"
)

RESULT_JSON = (
    RESULT_DIR /
    "final_top5_results.json"
)


# ============================================================
# CONFIGURATION
# ============================================================

TOP_K = 5


# Hybrid ranking weights
#
# Exact disease evidence is intentionally strongest because
# this dataset contains repeated disease -> formulation
# observations.
#
WEIGHT_EXACT_DISEASE = 0.34
WEIGHT_DISEASE_TFIDF = 0.22
WEIGHT_CONTEXT_TFIDF = 0.16
WEIGHT_FORMULATION_SIM = 0.10
WEIGHT_INGREDIENT_SIM = 0.10
WEIGHT_PRIOR = 0.08


# Additional deterministic bonuses
EXACT_DISEASE_BONUS = 0.10
SEEN_FORMULATION_BONUS = 0.02


# ============================================================
# NON-FORMULATION FILTER
# ============================================================

NON_FORMULATION_TERMS = {
    "early diagnosis",
    "supportive care",
    "regular monitoring",
    "regular checkups",
    "regular check-ups",
    "seek immediate medical attention",
    "medical attention",
    "avoid animal",
    "avoid animal contact",
    "avoid animal exposure",
    "avoid sun exposure",
    "avoid smoking",
    "avoid triggers",
    "avoid exposure",
    "good hygiene",
    "regular hygiene",
    "wound care",
    "hydration",
    "rest",
    "healthy lifestyle",
    "balanced diet",
    "healthy diet",
    "regular exercise",
    "stress management",
    "medication adherence",
    "follow prescribed medication",
    "monitor flare-ups",
    "therapy",
    "social support",
    "pulmonary rehab",
    "weight management",
    "mosquito control",
    "vaccination",
    "fly exposure",
    "regular lifestyle",
}


FORMULATION_SIGNALS = {
    "g",
    "kg",
    "mg",
    "mcg",
    "ml",
    "l",
    "tsp",
    "tbsp",
    "drop",
    "drops",
    "leaves",
    "powder",
    "oil",
    "milk",
    "water",
    "decoction",
    "paste",
    "juice",
    "extract",
    "daily",
    "capsule",
    "tablet",
}


# ============================================================
# COLUMN DETECTION
# ============================================================

def normalize_column_name(value: Any) -> str:
    return re.sub(
        r"[^a-z0-9]+",
        "_",
        str(value).strip().lower(),
    ).strip("_")


def find_column(
    df: pd.DataFrame,
    candidates: Sequence[str],
) -> Optional[str]:

    normalized = {
        normalize_column_name(c): c
        for c in df.columns
    }

    # Exact normalized match
    for candidate in candidates:

        key = normalize_column_name(candidate)

        if key in normalized:
            return normalized[key]

    # Substring match
    for candidate in candidates:

        key = normalize_column_name(candidate)

        for norm_name, original in normalized.items():

            if key and (
                key in norm_name
                or norm_name in key
            ):
                return original

    return None


DISEASE_CANDIDATES = [
    "Disease",
    "condition",
    "disease_name",
    "patient_condition",
    "diagnosis",
    "medical_condition",
]


FORMULATION_CANDIDATES = [
    "Formulation",
    "ayurvedic_formulation",
    "recommended_formulation",
    "recommendation",
    "treatment",
    "ayurvedic_recommendation",
]


CONTEXT_CANDIDATES = [
    "Symptoms",
    "Diagnosis & Tests",
    "Symptom Severity",
    "Duration of Treatment",
    "Medical History",
    "Current Medications",
    "Risk Factors",
    "Environmental Factors",
    "Sleep Patterns",
    "Stress Levels",
    "Physical Activity Levels",
    "Family History",
    "Dietary Habits",
    "Allergies (Food/Env)",
    "Seasonal Variation",
    "Age Group",
    "Gender",
    "Occupation and Lifestyle",
    "Cultural Preferences",
    "Herbal/Alternative Remedies",
    "Ayurvedic Herbs",
    "Doshas",
    "Constitution/Prakriti",
    "Diet and Lifestyle Recommendations",
    "Yoga & Physical Therapy",
    "Medical Intervention",
    "Patient Recommendations",
]


# ============================================================
# FILE HELPERS
# ============================================================

def first_existing(
    paths: Sequence[Path],
) -> Optional[Path]:

    for path in paths:

        if path.exists():
            return path

    return None


def load_csv(path: Path) -> pd.DataFrame:

    return pd.read_csv(
        path,
        low_memory=False,
    )


# ============================================================
# FIND DATASETS
# ============================================================

TRAIN_PATH = first_existing(
    TRAIN_CANDIDATES
)

TEST_PATH = first_existing(
    TEST_CANDIDATES
)


if TRAIN_PATH is None:

    raise FileNotFoundError(
        "\nCould not find training data.\n"
        f"Looked for:\n"
        + "\n".join(
            f"  - {p}"
            for p in TRAIN_CANDIDATES
        )
        + "\n\nRun this command from the project root:\n"
        "  python ml/train_model.py"
    )


if TEST_PATH is None:

    raise FileNotFoundError(
        "\nCould not find test data.\n"
        f"Looked for:\n"
        + "\n".join(
            f"  - {p}"
            for p in TEST_CANDIDATES
        )
    )


print("=" * 70)
print("FINAL AYURVEDIC TOP-5 FORMULATION RECOMMENDER")
print("=" * 70)

print("\nProject root:")
print(PROJECT_ROOT)

print("\nTraining file:")
print(TRAIN_PATH)

print("\nTest file:")
print(TEST_PATH)


# ============================================================
# LOAD DATA
# ============================================================

train_df = load_csv(TRAIN_PATH)
test_df = load_csv(TEST_PATH)


print("\nLoading datasets...")

print(
    f"Training rows: {len(train_df)}"
)

print(
    f"Test rows:     {len(test_df)}"
)


# ============================================================
# IDENTIFY COLUMNS
# ============================================================

disease_col = find_column(
    train_df,
    DISEASE_CANDIDATES,
)

formulation_col = find_column(
    train_df,
    FORMULATION_CANDIDATES,
)


if disease_col is None or formulation_col is None:

    raise ValueError(
        "\nCould not identify Disease/Formulation columns.\n\n"
        f"Available columns:\n{list(train_df.columns)}"
    )


test_disease_col = (
    find_column(
        test_df,
        DISEASE_CANDIDATES,
    )
    or disease_col
)


test_formulation_col = (
    find_column(
        test_df,
        FORMULATION_CANDIDATES,
    )
    or formulation_col
)


print("\nDisease column:")
print(disease_col)

print("\nFormulation column:")
print(formulation_col)


# ============================================================
# CONTEXT COLUMNS
# ============================================================

context_cols = [
    c
    for c in CONTEXT_CANDIDATES
    if c in train_df.columns
]


print("\nContext columns used:")

if context_cols:

    for c in context_cols:
        print(" -", c)

else:

    print(" - none found; disease-only mode")


# ============================================================
# BASIC TEXT CLEANING
# ============================================================

def clean_text(value: Any) -> str:

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass

    text = str(value).strip()

    if text.lower() in {
        "nan",
        "none",
        "null",
        "n/a",
        "na",
    }:
        return ""

    return text


# ============================================================
# FORMULATION VALIDATION
# ============================================================

def is_real_formulation(
    text: Any,
) -> bool:

    text = clean_text(text)

    if len(text) < 3:
        return False

    lower = text.lower()

    # Exact generic care instruction
    if lower in NON_FORMULATION_TERMS:
        return False

    matches = sum(
        1
        for term in NON_FORMULATION_TERMS
        if term in lower
    )

    # If it contains a generic care phrase but also
    # has an actual preparation signal, retain it.
    if matches >= 1:

        if not any(
            signal in lower
            for signal in FORMULATION_SIGNALS
        ):
            return False

    # Reject obvious instruction-style records.
    if (
        lower.startswith("avoid ")
        or lower.startswith("seek ")
        or lower.startswith("follow prescribed ")
        or lower.startswith("monitor ")
    ):

        if not any(
            signal in lower
            for signal in FORMULATION_SIGNALS
        ):
            return False

    return True


# ============================================================
# FORMULATION NORMALIZATION
# ============================================================

def normalize_formulation(
    text: Any,
) -> str:

    text = clean_text(text).lower()

    # Remove dose details for semantic comparison.
    text = re.sub(
        r"\([^)]*\)",
        " ",
        text,
    )

    text = text.replace(
        ";",
        ",",
    )

    text = text.replace(
        "&",
        ",",
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# INGREDIENT NORMALIZATION
# ============================================================

def canonical_ingredient_name(
    part: str,
) -> str:

    part = clean_text(part).lower()

    # Remove parenthetical details.
    part = re.sub(
        r"\([^)]*\)",
        " ",
        part,
    )

    # Remove quantities.
    part = re.sub(
        r"\b\d+(?:\.\d+)?\s*"
        r"(?:g|kg|mg|mcg|ml|l|tsp|tbsp|drops?|"
        r"cloves?|leaves?)\b",
        " ",
        part,
        flags=re.I,
    )

    # Remove common preparation phrases.
    part = re.sub(
        r"\b(?:as needed|daily|fresh|in water|at bedtime)\b",
        " ",
        part,
        flags=re.I,
    )

    part = re.sub(
        r"[^a-z0-9\s\-]",
        " ",
        part,
    )

    part = re.sub(
        r"\s+",
        " ",
        part,
    )

    return part.strip()


def extract_ingredients(
    text: Any,
) -> Set[str]:

    text = clean_text(text)

    if not text:
        return set()

    parts = [
        p.strip()
        for p in re.split(
            r",|;|\n",
            text,
        )
        if p.strip()
    ]

    ingredients: Set[str] = set()

    for part in parts:

        normalized = canonical_ingredient_name(
            part
        )

        if normalized:
            ingredients.add(
                normalized
            )

    return ingredients


# ============================================================
# CANONICAL FORMULATION KEY
# ============================================================

def formulation_key(
    text: Any,
) -> str:

    ingredients = extract_ingredients(
        text
    )

    if ingredients:

        return " | ".join(
            sorted(ingredients)
        )

    return normalize_formulation(
        text
    )


# ============================================================
# INGREDIENT METRICS
# ============================================================

def ingredient_overlap(
    predicted: Set[str],
    actual: Set[str],
) -> float:

    if not actual:
        return 0.0

    return (
        len(
            predicted.intersection(actual)
        )
        / len(actual)
        * 100.0
    )


def ingredient_jaccard(
    a: Set[str],
    b: Set[str],
) -> float:

    if not a and not b:
        return 1.0

    union = a.union(b)

    if not union:
        return 0.0

    return (
        len(a.intersection(b))
        / len(union)
    )


# ============================================================
# FILTER DATA
# ============================================================

train_df = train_df.copy()
test_df = test_df.copy()


train_df = train_df[
    train_df[
        formulation_col
    ].apply(is_real_formulation)
].copy()


test_df = test_df[
    test_df[
        test_formulation_col
    ].apply(is_real_formulation)
].copy()


train_df["__disease"] = (
    train_df[disease_col]
    .map(clean_text)
)


train_df["__formulation"] = (
    train_df[formulation_col]
    .map(clean_text)
)


test_df["__disease"] = (
    test_df[test_disease_col]
    .map(clean_text)
)


test_df["__formulation"] = (
    test_df[test_formulation_col]
    .map(clean_text)
)


train_df = train_df[
    (train_df["__disease"] != "")
    & (train_df["__formulation"] != "")
].copy()


test_df = test_df[
    (test_df["__disease"] != "")
    & (test_df["__formulation"] != "")
].copy()


train_df["__key"] = (
    train_df["__formulation"]
    .map(formulation_key)
)


train_df["__ingredients"] = (
    train_df["__formulation"]
    .map(extract_ingredients)
)


test_df["__key"] = (
    test_df["__formulation"]
    .map(formulation_key)
)


test_df["__ingredients"] = (
    test_df["__formulation"]
    .map(extract_ingredients)
)


print("\nRows after filtering:")

print(
    "Training:",
    len(train_df)
)

print(
    "Test:    ",
    len(test_df)
)


# ============================================================
# FORMULATION PROFILES
# ============================================================

formulation_records: Dict[
    str,
    Dict[str, Any]
] = {}


for _, row in train_df.iterrows():

    key = row["__key"]

    formulation = row[
        "__formulation"
    ]

    ingredients = set(
        row["__ingredients"]
    )


    if key not in formulation_records:

        formulation_records[key] = {
            "key": key,
            "formulation": formulation,
            "ingredients": ingredients,
            "diseases": Counter(),
            "contexts": [],
            "row_count": 0,
        }


    rec = formulation_records[key]

    disease = row["__disease"].lower()

    rec["diseases"][disease] += 1

    rec["row_count"] += 1


    if (
        not rec["ingredients"]
        and ingredients
    ):

        rec["ingredients"] = ingredients


    context_parts = []

    for col in context_cols:

        value = clean_text(
            row.get(col, "")
        )

        if value:
            context_parts.append(
                value
            )


    if context_parts:

        rec["contexts"].append(
            " ".join(context_parts)
        )


profiles = list(
    formulation_records.values()
)


print(
    "\nUnique real formulations:",
    len(profiles)
)


if len(profiles) < 2:

    raise ValueError(
        "Not enough unique formulations after filtering."
    )


# ============================================================
# PROFILE DATAFRAME
# ============================================================

profiles_df = pd.DataFrame(
    [
        {
            "key": r["key"],
            "formulation": r["formulation"],
            "ingredients": r["ingredients"],
            "diseases": dict(
                r["diseases"]
            ),
            "contexts": r["contexts"],
            "row_count": r["row_count"],
        }
        for r in profiles
    ]
)


# ============================================================
# DISEASE -> FORMULATION EVIDENCE
# ============================================================

disease_formulation_counts = (
    defaultdict(Counter)
)

disease_total_counts = Counter()


for _, row in train_df.iterrows():

    disease = (
        row["__disease"]
        .lower()
        .strip()
    )

    key = row["__key"]

    disease_formulation_counts[
        disease
    ][key] += 1

    disease_total_counts[
        disease
    ] += 1


# ============================================================
# DISEASE NORMALIZATION
# ============================================================

def normalize_disease(
    value: Any,
) -> str:

    text = clean_text(
        value
    ).lower()

    text = text.replace(
        "&",
        " and ",
    )

    text = re.sub(
        r"[^a-z0-9\s\-]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# PRIOR SCORE
# ============================================================

def prior_score(
    disease: str,
    formulation_key_value: str,
) -> float:

    disease = normalize_disease(
        disease
    )

    counts = disease_formulation_counts.get(
        disease
    )

    if not counts:
        return 0.0

    total = disease_total_counts[
        disease
    ]

    if total <= 0:
        return 0.0

    count = counts.get(
        formulation_key_value,
        0,
    )

    return count / total


# ============================================================
# EXACT DISEASE EVIDENCE
# ============================================================

def exact_disease_evidence(
    disease: str,
    formulation_key_value: str,
) -> float:

    return (
        1.0
        if prior_score(
            disease,
            formulation_key_value,
        ) > 0
        else 0.0
    )


# ============================================================
# PROFILE TEXT
# ============================================================

def profile_text(
    profile: Dict[str, Any],
) -> str:

    disease_text = " ".join(
        disease
        for disease, count
        in profile["diseases"].items()
        for _ in range(
            min(
                int(count),
                5,
            )
        )
    )


    ingredient_text = " ".join(
        sorted(
            profile["ingredients"]
        )
    )


    context_text = " ".join(
        profile["contexts"][:20]
    )


    return " ".join(
        part
        for part in [
            disease_text,
            disease_text,
            ingredient_text,
            ingredient_text,
            context_text,
            normalize_formulation(
                profile["formulation"]
            ),
        ]
        if part
    )


profile_texts = [
    profile_text(profile)
    for profile in profiles
]


# ============================================================
# TF-IDF — FORMULATION PROFILE
# ============================================================

print(
    "\nCreating TF-IDF representations..."
)


profile_vectorizer = TfidfVectorizer(
    lowercase=True,
    strip_accents="unicode",
    analyzer="word",
    ngram_range=(1, 2),
    min_df=1,
    sublinear_tf=True,
    max_features=20000,
)


profile_matrix = (
    profile_vectorizer.fit_transform(
        profile_texts
    )
)


print(
    "Profile TF-IDF features:",
    profile_matrix.shape[1],
)


# ============================================================
# TF-IDF — DISEASE
# ============================================================

disease_names = [
    " ".join(
        sorted(
            profile["diseases"].keys()
        )
    )
    for profile in profiles
]


disease_vectorizer = TfidfVectorizer(
    lowercase=True,
    strip_accents="unicode",
    analyzer="word",
    ngram_range=(1, 2),
    min_df=1,
    sublinear_tf=True,
)


disease_matrix = (
    disease_vectorizer.fit_transform(
        disease_names
    )
)


# ============================================================
# TF-IDF — CONTEXT
# ============================================================

profile_contexts = [
    " ".join(
        profile["contexts"]
    )
    for profile in profiles
]


context_vectorizer = TfidfVectorizer(
    lowercase=True,
    strip_accents="unicode",
    analyzer="word",
    ngram_range=(1, 2),
    min_df=1,
    sublinear_tf=True,
)


if any(
    text.strip()
    for text in profile_contexts
):

    context_matrix = (
        context_vectorizer.fit_transform(
            profile_contexts
        )
    )

else:

    context_matrix = None


# ============================================================
# TF-IDF — INGREDIENTS
# ============================================================

ingredient_texts = [
    " ".join(
        sorted(
            profile["ingredients"]
        )
    )
    for profile in profiles
]


ingredient_vectorizer = TfidfVectorizer(
    lowercase=True,
    strip_accents="unicode",
    analyzer="word",
    ngram_range=(1, 2),
    min_df=1,
    sublinear_tf=True,
)


ingredient_matrix = (
    ingredient_vectorizer.fit_transform(
        ingredient_texts
    )
)


# ============================================================
# RANKER
# ============================================================

def recommend(
    disease: str,
    context: Optional[
        Dict[str, Any]
    ] = None,
    top_k: int = TOP_K,
) -> List[
    Dict[str, Any]
]:

    disease = clean_text(
        disease
    )

    normalized_disease = (
        normalize_disease(
            disease
        )
    )


    if not disease:
        return []


    # --------------------------------------------------------
    # Disease TF-IDF
    # --------------------------------------------------------

    q_disease = (
        disease_vectorizer.transform(
            [normalized_disease]
        )
    )


    disease_scores = (
        cosine_similarity(
            q_disease,
            disease_matrix,
        )[0]
    )


    # --------------------------------------------------------
    # Profile semantic similarity
    # --------------------------------------------------------

    q_profile_text = (
        normalized_disease
    )


    if context:

        context_values = [
            clean_text(v)
            for v in context.values()
            if clean_text(v)
        ]

        if context_values:

            q_profile_text += (
                " "
                + " ".join(
                    context_values
                )
            )


    q_profile = (
        profile_vectorizer.transform(
            [q_profile_text]
        )
    )


    profile_scores = (
        cosine_similarity(
            q_profile,
            profile_matrix,
        )[0]
    )


    # --------------------------------------------------------
    # Context similarity
    # --------------------------------------------------------

    if (
        context_matrix is not None
        and context
    ):

        context_text = " ".join(
            clean_text(v)
            for v in context.values()
            if clean_text(v)
        )


        if context_text.strip():

            q_context = (
                context_vectorizer.transform(
                    [context_text]
                )
            )


            context_scores = (
                cosine_similarity(
                    q_context,
                    context_matrix,
                )[0]
            )

        else:

            context_scores = np.zeros(
                len(profiles),
                dtype=float,
            )

    else:

        context_scores = np.zeros(
            len(profiles),
            dtype=float,
        )


    # --------------------------------------------------------
    # Ingredient similarity
    # --------------------------------------------------------

    query_ingredients: Set[str] = set()


    if context:

        for key in (
            "Ayurvedic Herbs",
            "Herbal/Alternative Remedies",
            "herbs",
            "ingredients",
            "formulation",
        ):

            if key in context:

                query_ingredients.update(
                    extract_ingredients(
                        context[key]
                    )
                )


    ingredient_scores = np.zeros(
        len(profiles),
        dtype=float,
    )


    if query_ingredients:

        for i, profile in enumerate(
            profiles
        ):

            ingredient_scores[i] = (
                ingredient_jaccard(
                    query_ingredients,
                    profile[
                        "ingredients"
                    ],
                )
            )


    # --------------------------------------------------------
    # Disease -> formulation prior
    # --------------------------------------------------------

    priors = np.array(
        [
            prior_score(
                normalized_disease,
                profile["key"],
            )
            for profile in profiles
        ],
        dtype=float,
    )


    exact_evidence = np.array(
        [
            exact_disease_evidence(
                normalized_disease,
                profile["key"],
            )
            for profile in profiles
        ],
        dtype=float,
    )


    # --------------------------------------------------------
    # HYBRID SCORE
    # --------------------------------------------------------

    scores = (
        WEIGHT_EXACT_DISEASE
        * exact_evidence

        + WEIGHT_DISEASE_TFIDF
        * disease_scores

        + WEIGHT_CONTEXT_TFIDF
        * context_scores

        + WEIGHT_FORMULATION_SIM
        * profile_scores

        + WEIGHT_INGREDIENT_SIM
        * ingredient_scores

        + WEIGHT_PRIOR
        * priors
    )


    # --------------------------------------------------------
    # Exact disease bonus
    # --------------------------------------------------------

    scores = (
        scores
        + (
            EXACT_DISEASE_BONUS
            * exact_evidence
        )
    )


    # --------------------------------------------------------
    # Rank
    # --------------------------------------------------------

    ranked = np.argsort(
        scores
    )[::-1]


    results: List[
        Dict[str, Any]
    ] = []


    # --------------------------------------------------------
    # Diversity
    # --------------------------------------------------------

    seen_keys: Set[str] = set()


    for idx in ranked:

        profile = profiles[
            int(idx)
        ]


        if profile["key"] in seen_keys:
            continue


        seen_keys.add(
            profile["key"]
        )


        results.append(
            {
                "rank": len(results) + 1,

                "formulation":
                    profile[
                        "formulation"
                    ],

                "score":
                    float(
                        scores[idx]
                    ),

                "ingredient_match":
                    0.0,

                "ingredients":
                    sorted(
                        profile[
                            "ingredients"
                        ]
                    ),

                "key":
                    profile[
                        "key"
                    ],

                "disease_match":
                    float(
                        disease_scores[
                            idx
                        ]
                    ),

                "context_match":
                    float(
                        context_scores[
                            idx
                        ]
                    ),

                "prior":
                    float(
                        priors[
                            idx
                        ]
                    ),
            }
        )


        if len(results) >= top_k:
            break


    return results


# ============================================================
# FRONTEND FORMATTER
# ============================================================

def display_formulation(
    formulation: str,
) -> str:

    """
    Converts dataset formulation text into a
    cleaner frontend display.

    Example:

        Ashwagandha (5g), Brahmi (2g),
        Warm water (200ml)

    becomes:

        Ashwagandha + Brahmi + Warm water
    """

    text = clean_text(
        formulation
    )

    parts = [
        p.strip()
        for p in re.split(
            r",|;|\n",
            text,
        )
        if p.strip()
    ]


    cleaned_parts = []


    for part in parts:

        # Remove parenthetical dose.
        part = re.sub(
            r"\([^)]*\)",
            "",
            part,
        )

        part = re.sub(
            r"\s+",
            " ",
            part,
        ).strip()


        if part:
            cleaned_parts.append(
                part
            )


    if cleaned_parts:

        return " + ".join(
            cleaned_parts
        )


    return text


def format_frontend_recommendations(
    recommendations: List[
        Dict[str, Any]
    ],
) -> List[
    Dict[str, Any]
]:

    medals = {
        1: "🥇",
        2: "🥈",
        3: "🥉",
        4: "4️⃣",
        5: "5️⃣",
    }


    output = []


    for rec in recommendations[:5]:

        output.append(
            {
                "rank":
                    rec["rank"],

                "medal":
                    medals.get(
                        rec["rank"],
                        str(
                            rec["rank"]
                        ),
                    ),

                "formulation":
                    display_formulation(
                        rec[
                            "formulation"
                        ]
                    ),

                "ingredient_match":
                    round(
                        float(
                            rec.get(
                                "ingredient_match",
                                0.0,
                            )
                        ),
                        1,
                    ),
            }
        )


    return output


# ============================================================
# EVALUATION
# ============================================================

print(
    "\nCalculating Top-5 recommendations..."
)


evaluation_rows = []

exact_top5 = 0
match_50 = 0
match_75 = 0

overlap_values = []

sample_rows = []


for _, row in test_df.iterrows():

    disease = row[
        "__disease"
    ]

    actual = row[
        "__formulation"
    ]

    actual_key = row[
        "__key"
    ]

    actual_ingredients = set(
        row[
            "__ingredients"
        ]
    )


    # Build context
    context: Dict[
        str,
        Any
    ] = {}


    for col in context_cols:

        if col in test_df.columns:

            value = clean_text(
                row.get(
                    col,
                    "",
                )
            )

            if value:

                context[col] = value


    recommendations = recommend(
        disease,
        context=context,
        top_k=TOP_K,
    )


    best_overlap = 0.0

    exact_found = False


    for rec in recommendations:

        overlap = ingredient_overlap(
            set(
                rec[
                    "ingredients"
                ]
            ),
            actual_ingredients,
        )


        rec[
            "ingredient_match"
        ] = overlap


        if (
            rec["key"]
            == actual_key
        ):

            exact_found = True


        best_overlap = max(
            best_overlap,
            overlap,
        )


        evaluation_rows.append(
            {
                "disease":
                    disease,

                "actual_formulation":
                    actual,

                "recommended_formulation":
                    rec[
                        "formulation"
                    ],

                "rank":
                    rec[
                        "rank"
                    ],

                "score":
                    rec[
                        "score"
                    ],

                "ingredient_match":
                    overlap,
            }
        )


    if exact_found:
        exact_top5 += 1


    if best_overlap >= 50:
        match_50 += 1


    if best_overlap >= 75:
        match_75 += 1


    overlap_values.append(
        best_overlap
    )


    if len(sample_rows) < 10:

        sample_rows.append(
            (
                disease,
                actual,
                recommendations,
            )
        )


# ============================================================
# METRICS
# ============================================================

total = len(test_df)


exact_accuracy = (
    exact_top5 / total * 100
    if total
    else 0.0
)


match50_accuracy = (
    match_50 / total * 100
    if total
    else 0.0
)


match75_accuracy = (
    match_75 / total * 100
    if total
    else 0.0
)


average_overlap = (
    float(
        np.mean(
            overlap_values
        )
    )
    if overlap_values
    else 0.0
)


# ============================================================
# PRINT RESULTS
# ============================================================

print(
    "\n"
    + "=" * 65
)

print(
    "FINAL AYURVEDIC TOP-5 RECOMMENDATION MODEL"
)

print(
    "=" * 65
)


print(
    f"\nTest samples: {total}"
)


print(
    f"Exact formulation in Top-5: "
    f"{exact_accuracy:.2f}%"
)


print(
    f"Top-5 ingredient match >= 50%: "
    f"{match50_accuracy:.2f}%"
)


print(
    f"Top-5 ingredient match >= 75%: "
    f"{match75_accuracy:.2f}%"
)


print(
    f"Average best ingredient overlap: "
    f"{average_overlap:.2f}%"
)


# ============================================================
# SAMPLE RECOMMENDATIONS
# ============================================================

print(
    "\n"
    + "=" * 65
)

print(
    "SAMPLE TOP-5 RECOMMENDATIONS"
)

print(
    "=" * 65
)


for (
    disease,
    actual,
    recommendations,
) in sample_rows:

    print(
        "\n"
        + "-" * 65
    )

    print(
        "Patient:",
        disease,
    )

    print(
        "Actual:",
        actual,
    )

    print(
        "\nRecommendations:"
    )


    for rec in recommendations:

        print(
            f'{rec["rank"]}. '
            f'{rec["formulation"]}'
        )

        print(
            f'   score='
            f'{rec["score"]:.3f}'
            f' | ingredient match='
            f'{rec["ingredient_match"]:.1f}%'
        )


# ============================================================
# SAVE CSV
# ============================================================

evaluation_df = pd.DataFrame(
    evaluation_rows
)


evaluation_df.to_csv(
    RESULT_CSV,
    index=False,
)


# ============================================================
# SAVE FRONTEND JSON
# ============================================================

json_results = []


for (
    disease,
    actual,
    recommendations,
) in sample_rows:

    json_results.append(
        {
            "disease":
                disease,

            "actual_formulation":
                actual,

            "recommendations":
                format_frontend_recommendations(
                    recommendations
                ),
        }
    )


with open(
    RESULT_JSON,
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        {
            "metrics": {
                "test_samples":
                    total,

                "exact_top5_accuracy":
                    round(
                        exact_accuracy,
                        2,
                    ),

                "ingredient_match_50":
                    round(
                        match50_accuracy,
                        2,
                    ),

                "ingredient_match_75":
                    round(
                        match75_accuracy,
                        2,
                    ),

                "average_best_ingredient_overlap":
                    round(
                        average_overlap,
                        2,
                    ),
            },

            "samples":
                json_results,
        },

        f,

        ensure_ascii=False,

        indent=2,
    )


# ============================================================
# SAVE COMPLETE BACKEND ARTIFACT
# ============================================================

artifact = {

    "model_version":
        "final_top5_v2",

    "project_root":
        str(PROJECT_ROOT),


    "config": {

        "top_k":
            TOP_K,

        "weight_exact_disease":
            WEIGHT_EXACT_DISEASE,

        "weight_disease_tfidf":
            WEIGHT_DISEASE_TFIDF,

        "weight_context_tfidf":
            WEIGHT_CONTEXT_TFIDF,

        "weight_formulation_sim":
            WEIGHT_FORMULATION_SIM,

        "weight_ingredient_sim":
            WEIGHT_INGREDIENT_SIM,

        "weight_prior":
            WEIGHT_PRIOR,

        "exact_disease_bonus":
            EXACT_DISEASE_BONUS,

        "seen_formulation_bonus":
            SEEN_FORMULATION_BONUS,
    },


    "columns": {

        "disease":
            disease_col,

        "formulation":
            formulation_col,

        "context":
            context_cols,
    },


    "profiles":
        profiles,


    "profile_vectorizer":
        profile_vectorizer,

    "profile_matrix":
        profile_matrix,


    "disease_vectorizer":
        disease_vectorizer,

    "disease_matrix":
        disease_matrix,


    "context_vectorizer":
        context_vectorizer,

    "context_matrix":
        context_matrix,


    "ingredient_vectorizer":
        ingredient_vectorizer,

    "ingredient_matrix":
        ingredient_matrix,


    "disease_formulation_counts":
        {
            disease: dict(counter)
            for disease, counter
            in disease_formulation_counts.items()
        },


    "disease_total_counts":
        dict(
            disease_total_counts
        ),


    "metrics": {

        "test_samples":
            total,

        "exact_top5_accuracy":
            exact_accuracy,

        "ingredient_match_50":
            match50_accuracy,

        "ingredient_match_75":
            match75_accuracy,

        "average_best_ingredient_overlap":
            average_overlap,
    },
}


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    artifact,
    MODEL_PATH,
)


# ============================================================
# FINAL OUTPUT
# ============================================================

print(
    "\n"
    + "=" * 65
)

print(
    "FINAL MODEL SAVED"
)

print(
    "=" * 65
)


print(
    "\nModel:"
)

print(
    MODEL_PATH
)


print(
    "\nEvaluation CSV:"
)

print(
    RESULT_CSV
)


print(
    "\nFrontend JSON:"
)

print(
    RESULT_JSON
)


print(
    "\nTraining complete."
)


print(
    "\nIMPORTANT:"
)

print(
    "The backend should load ONLY this model artifact:"
)

print(
    MODEL_PATH
)
