"""
Ayurveda Intelligence
Backend API

Provides a lightweight REST API around the prototype
recommendation engine.

Current endpoints:

    GET  /health
    GET  /search?q=fever
    GET  /recommend?q=fever
    GET  /diseases
    GET  /formulations

The API is intentionally simple for the hackathon prototype.
"""

from fastapi import FastAPI, HTTPException
from recommendation import recommend
from data_loader import (
    load_diseases,
    load_formulations,
    load_synonyms,
)
from config import APP_NAME, APP_VERSION, APP_ENVIRONMENT


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Evidence-aware Ayurvedic formulation discovery "
        "backend for the hackathon prototype."
    ),
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    """
    Check whether the backend API is running.
    """

    return {
        "status": "ok",
        "application": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
    }


# ============================================================
# SEARCH
# ============================================================

@app.get("/search")
def search(q: str):
    """
    Resolve a user search term into its canonical terminology.

    Example:

        /search?q=fever
    """

    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search term cannot be empty."
        )

    synonyms = load_synonyms()

    from recommendation import resolve_terminology

    result = resolve_terminology(
        query,
        synonyms
    )

    return {
        "query": query,
        "normalized_term": result["canonical_term"],
        "match_type": result["match_type"],
        "matched": result["matched"],
    }


# ============================================================
# RECOMMENDATION
# ============================================================

@app.get("/recommend")
def get_recommendation(q: str):
    """
    Run the complete recommendation pipeline.

    Example:

        /recommend?q=fever
    """

    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search term cannot be empty."
        )

    return recommend(query)


# ============================================================
# DISEASES
# ============================================================

@app.get("/diseases")
def get_diseases():
    """
    Return disease / condition records from the prototype
    knowledge base.
    """

    diseases = load_diseases()

    return {
        "count": len(diseases),
        "diseases": diseases,
    }


# ============================================================
# FORMULATIONS
# ============================================================

@app.get("/formulations")
def get_formulations():
    """
    Return formulation records from the prototype
    knowledge base.
    """

    formulations = load_formulations()

    return {
        "count": len(formulations),
        "formulations": formulations,
    }


# ============================================================
# API INFORMATION
# ============================================================

@app.get("/")
def root():
    """
    Basic API information.
    """

    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
        "message": "Ayurveda Intelligence API is running.",
        "endpoints": [
            "/health",
            "/search?q=fever",
            "/recommend?q=fever",
            "/diseases",
            "/formulations",
            "/docs",
        ],
    }
