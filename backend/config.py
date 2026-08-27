"""
Ayurveda Intelligence
Backend Configuration
"""

from pathlib import Path


# ============================================================
# PROJECT
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent


# ============================================================
# MODEL
# ============================================================

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
)

MODEL_FILE = (
    MODEL_DIR
    / "final_top5_formulation_ranker.joblib"
)


# ============================================================
# DATA
# ============================================================

DATA_DIR = (
    PROJECT_ROOT
    / "data"
)

DISEASES_FILE = (
    DATA_DIR
    / "diseases.csv"
)

FORMULATIONS_FILE = (
    DATA_DIR
    / "formulations.csv"
)

SYNONYMS_FILE = (
    DATA_DIR
    / "synonyms.csv"
)


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "Ayurveda Intelligence"

APP_VERSION = "1.0.0"

APP_ENVIRONMENT = "development"


# ============================================================
# RECOMMENDATION
# ============================================================

MAX_RECOMMENDATIONS = 5

MIN_MATCH_SCORE = 0.0


# ============================================================
# SAFETY
# ============================================================

DISCLAIMER = (
    "This system is an educational/research decision-support "
    "prototype. It does not diagnose disease, prescribe "
    "treatment, or replace advice from a qualified healthcare "
    "professional."
)


# ============================================================
# SUMMARY
# ============================================================

def get_config_summary():

    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
        "project_root": str(PROJECT_ROOT),
        "model_file": str(MODEL_FILE),
        "model_exists": MODEL_FILE.exists(),
        "data_directory": str(DATA_DIR),
        "max_recommendations": MAX_RECOMMENDATIONS,
    }
