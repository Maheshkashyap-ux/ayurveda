"""
Ayurveda Intelligence
FastAPI Backend

ML-backed formulation recommendation API.
"""

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import (
    APP_NAME,
    APP_VERSION,
    APP_ENVIRONMENT,
    DISCLAIMER,
)

from services.ml_recommender import (
    recommend_for_frontend,
    model_health,
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Ayurvedic formulation recommendation API "
        "powered by the trained Top-5 ranking artifact."
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class RecommendationRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=1,
        description="Disease or patient condition.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=5,
    )

    patient_context: dict[str, Any] | None = None


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    model = model_health()

    return {
        "status": (
            "ok"
            if model["status"] == "ready"
            else "degraded"
        ),
        "application": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
        "model": model,
    }


# ============================================================
# MODEL HEALTH
# ============================================================

@app.get("/model/health")
def model_status():

    return model_health()


# ============================================================
# RECOMMEND — GET
# ============================================================

@app.get("/recommend")
def recommend_get(
    q: str,
    top_k: int = 5,
):

    query = q.strip()

    if not query:

        raise HTTPException(
            status_code=400,
            detail="Search term cannot be empty.",
        )

    try:

        return recommend_for_frontend(
            query=query,
            top_k=top_k,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Recommendation engine failed: "
                f"{exc}"
            ),
        )


# ============================================================
# RECOMMEND — POST
# ============================================================

@app.post("/recommend")
def recommend_post(
    request: RecommendationRequest,
):

    try:

        return recommend_for_frontend(
            query=request.query,
            top_k=request.top_k,
            patient_context=request.patient_context,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Recommendation engine failed: "
                f"{exc}"
            ),
        )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
        "message": (
            "Ayurveda Intelligence ML API is running."
        ),
        "endpoints": [
            "/health",
            "/model/health",
            "/recommend?q=fever",
            "/docs",
        ],
        "disclaimer": DISCLAIMER,
    }
