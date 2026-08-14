"""
Ayurveda Intelligence
Backend Configuration

This module contains configuration values used by the prototype
recommendation backend.

The current implementation uses CSV files as the local knowledge base.
The paths are resolved relative to the project root so that the backend
can be executed from different working directories.
"""

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

# backend/
#     config.py
#
# Project root is one level above the backend directory.

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

DATA_DIR = PROJECT_ROOT / "data"


# ============================================================
# KNOWLEDGE BASE FILES
# ============================================================

DISEASES_FILE = DATA_DIR / "diseases.csv"

FORMULATIONS_FILE = DATA_DIR / "formulations.csv"

SYNONYMS_FILE = DATA_DIR / "synonyms.csv"


# ============================================================
# RECOMMENDATION SETTINGS
# ============================================================

# Maximum number of formulation candidates returned by the
# recommendation engine.

MAX_RECOMMENDATIONS = 5


# Minimum prototype score required for a candidate to be
# considered a useful match.

MIN_MATCH_SCORE = 0


# ============================================================
# SEARCH SETTINGS
# ============================================================

# Whether user input should be converted to lowercase before
# performing basic text matching.

NORMALIZE_CASE = True


# Whether leading/trailing whitespace should be removed.

STRIP_INPUT = True


# ============================================================
# APPLICATION SETTINGS
# ============================================================

APP_NAME = "Ayurveda Intelligence"

APP_VERSION = "0.1.0"

APP_ENVIRONMENT = "prototype"


# ============================================================
# SAFETY / APPLICATION INFORMATION
# ============================================================

DISCLAIMER = (
    "This prototype is intended for educational and research purposes. "
    "It does not diagnose medical conditions, prescribe medicines, "
    "or replace advice from a qualified practitioner."
)


# ============================================================
# CONFIGURATION SUMMARY
# ============================================================

def get_config_summary():
    """
    Return the active backend configuration.

    This function is useful for debugging and verifying that the
    backend is reading the expected files.
    """

    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
        "data_directory": str(DATA_DIR),
        "diseases_file": str(DISEASES_FILE),
        "formulations_file": str(FORMULATIONS_FILE),
        "synonyms_file": str(SYNONYMS_FILE),
        "max_recommendations": MAX_RECOMMENDATIONS,
        "min_match_score": MIN_MATCH_SCORE,
    }
