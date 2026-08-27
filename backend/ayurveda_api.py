"""
Ayurveda Intelligence API

Connects:
- Patient case validation
- Red flag detection
- Trained ML formulation recommender

Uses the existing trained artifact through:
    services.ml_recommender

Does NOT retrain the model.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ============================================================
# OPTIONAL SERVICE IMPORTS
# ============================================================

try:
    from services.red_flag_engine import detect_red_flags
except Exception as exc:
    detect_red_flags = None
    RED_FLAG_IMPORT_ERROR = str(exc)


try:
    from services.ml_recommender import (
        recommend_for_frontend,
        model_health,
    )
except Exception as exc:
    recommend_for_frontend = None
    model_health = None
    ML_IMPORT_ERROR = str(exc)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Ayurveda Intelligence API",
    version="1.0.0",
)
# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# PATIENT CASE MODELS
# ============================================================

class Symptoms(BaseModel):
    chief_complaint: str = ""
    symptoms: list[str] = Field(default_factory=list)
    severity: str = ""
    duration: str = ""
    associated_symptoms: list[str] = Field(default_factory=list)


class Prakriti(BaseModel):
    constitution: str = ""
    dosha: str = ""
    vikriti: str = ""


class Lifestyle(BaseModel):
    diet: str = ""
    sleep: str = ""
    physical_activity: str = ""
    stress_level: str = ""
    occupation: str = ""
    lifestyle_notes: str = ""


class MedicalHistory(BaseModel):
    conditions: list[str] = Field(default_factory=list)
    previous_treatments: list[str] = Field(default_factory=list)
    surgeries: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    family_history: list[str] = Field(default_factory=list)


class Medications(BaseModel):
    current_medications: list[str] = Field(default_factory=list)
    supplements: list[str] = Field(default_factory=list)
    herbal_remedies: list[str] = Field(default_factory=list)


class Comorbidities(BaseModel):
    conditions: list[str] = Field(default_factory=list)


class PatientCase(BaseModel):
    patient_id: str = ""
    age: Optional[int] = None
    gender: str = ""

    symptoms: Symptoms = Field(
        default_factory=Symptoms
    )

    prakriti: Prakriti = Field(
        default_factory=Prakriti
    )

    lifestyle: Lifestyle = Field(
        default_factory=Lifestyle
    )

    medical_history: MedicalHistory = Field(
        default_factory=MedicalHistory
    )

    medications: Medications = Field(
        default_factory=Medications
    )

    comorbidities: Comorbidities = Field(
        default_factory=Comorbidities
    )


# ============================================================
# RECOMMENDATION REQUEST
# ============================================================

class RecommendationRequest(BaseModel):
    query: str
    top_k: int = 5
    patient_context: Optional[Dict[str, Any]] = None


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "status": "ready",
        "service": "ayurveda_intelligence",
        "api": "ayurveda_api",
    }


# ============================================================
# CASE HEALTH
# ============================================================

@app.get("/case/health")
def case_health():
    return {
        "status": "ready",
        "service": "patient_case",
        "api": "ayurveda_api",
    }


# ============================================================
# MODEL HEALTH
# ============================================================

@app.get("/model/health")
def model_health_endpoint():

    if model_health is None:
        return {
            "status": "error",
            "message": (
                "ML recommendation service could not be imported."
            ),
            "error": globals().get(
                "ML_IMPORT_ERROR",
                "Unknown import error",
            ),
        }

    try:
        result = model_health()

        if isinstance(result, dict):
            return result

        return {
            "status": "error",
            "message": "ML health service returned an invalid response.",
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": "ML model health check failed.",
            "error": str(exc),
        }


# ============================================================
# RED FLAG HEALTH
# ============================================================

@app.get("/red-flags/health")
def red_flag_health():

    if detect_red_flags is None:
        return {
            "status": "error",
            "message": (
                "Red flag detection service could not be imported."
            ),
            "error": globals().get(
                "RED_FLAG_IMPORT_ERROR",
                "Unknown import error",
            ),
        }

    return {
        "status": "ready",
        "service": "red_flag_engine",
        "api": "ayurveda_api",
    }


# ============================================================
# PATIENT CASE ANALYSIS
# ============================================================

@app.post("/case/analyze")
def analyze_patient_case(
    patient_case: PatientCase,
):

    # --------------------------------------------------------
    # Red flag analysis
    # --------------------------------------------------------

    if detect_red_flags is None:
        red_flags = {
            "status": "error",
            "overall_status": "unknown",
            "red_flags_detected": False,
            "count": 0,
            "flags": [],
            "error": globals().get(
                "RED_FLAG_IMPORT_ERROR",
                "Red flag engine unavailable.",
            ),
        }

    else:
        try:
            red_flags = detect_red_flags(
                patient_case
            )
        except Exception as exc:
            red_flags = {
                "status": "error",
                "overall_status": "unknown",
                "red_flags_detected": False,
                "count": 0,
                "flags": [],
                "error": str(exc),
            }

    return {
        "status": "success",
        "message": "Patient case analyzed successfully.",
        "patient_case": patient_case.model_dump(),
        "red_flags": red_flags,
    }


# ============================================================
# RED FLAG DETECTION DIRECT ENDPOINT
# ============================================================

@app.post("/red-flags/check")
def check_red_flags(
    patient_case: PatientCase,
):

    if detect_red_flags is None:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Red flag engine could not be imported.",
                "error": globals().get(
                    "RED_FLAG_IMPORT_ERROR",
                    "Unknown import error",
                ),
            },
        )

    try:
        return detect_red_flags(
            patient_case
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# ML RECOMMENDATION
# ============================================================

@app.post("/recommend")
def recommend_formulations(
    request: RecommendationRequest,
):

    if recommend_for_frontend is None:
        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "ML recommendation service "
                    "could not be imported."
                ),
                "error": globals().get(
                    "ML_IMPORT_ERROR",
                    "Unknown import error",
                ),
            },
        )

    try:

        result = recommend_for_frontend(
            query=request.query,
            top_k=request.top_k,
            patient_context=request.patient_context,
        )

        return result

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Recommendation failed.",
                "error": str(exc),
            },
        )


# ============================================================
# PATIENT CASE + ML RECOMMENDATION
# ============================================================

@app.post("/case/recommend")
def recommend_for_patient_case(
    patient_case: PatientCase,
    top_k: int = 5,
):

    # --------------------------------------------------------
    # Red flags first
    # --------------------------------------------------------

    if detect_red_flags is not None:
        try:
            red_flags = detect_red_flags(
                patient_case
            )
        except Exception as exc:
            red_flags = {
                "status": "error",
                "overall_status": "unknown",
                "red_flags_detected": False,
                "count": 0,
                "flags": [],
                "error": str(exc),
            }
    else:
        red_flags = {
            "status": "error",
            "overall_status": "unknown",
            "red_flags_detected": False,
            "count": 0,
            "flags": [],
            "error": globals().get(
                "RED_FLAG_IMPORT_ERROR",
                "Red flag engine unavailable.",
            ),
        }

    # --------------------------------------------------------
    # Build ML query
    # --------------------------------------------------------

    symptoms = patient_case.symptoms

    query = (
        symptoms.chief_complaint
        or (
            symptoms.symptoms[0]
            if symptoms.symptoms
            else ""
        )
    )

    if not query:
        return {
            "status": "invalid_input",
            "message": (
                "A chief complaint or symptom "
                "is required for recommendation."
            ),
            "red_flags": red_flags,
            "recommendations": [],
        }

    # --------------------------------------------------------
    # Build patient context
    # --------------------------------------------------------

    context = {
        "patient_id": patient_case.patient_id,
        "age": patient_case.age,
        "gender": patient_case.gender,

        "symptoms": ", ".join(
            symptoms.symptoms
        ),

        "chief_complaint": (
            symptoms.chief_complaint
        ),

        "symptom_severity": (
            symptoms.severity
        ),

        "duration": symptoms.duration,

        "associated_symptoms": ", ".join(
            symptoms.associated_symptoms
        ),

        "constitution": (
            patient_case.prakriti.constitution
        ),

        "doshas": (
            patient_case.prakriti.dosha
        ),

        "vikriti": (
            patient_case.prakriti.vikriti
        ),

        "diet": (
            patient_case.lifestyle.diet
        ),

        "sleep": (
            patient_case.lifestyle.sleep
        ),

        "physical_activity": (
            patient_case.lifestyle.physical_activity
        ),

        "stress_level": (
            patient_case.lifestyle.stress_level
        ),

        "occupation": (
            patient_case.lifestyle.occupation
        ),

        "lifestyle_notes": (
            patient_case.lifestyle.lifestyle_notes
        ),

        "medical_history": ", ".join(
            patient_case.medical_history.conditions
        ),

        "current_medications": ", ".join(
            patient_case.medications.current_medications
        ),

        "herbal_remedies": ", ".join(
            patient_case.medications.herbal_remedies
        ),

        "allergies": ", ".join(
            patient_case.medical_history.allergies
        ),

        "family_history": ", ".join(
            patient_case.medical_history.family_history
        ),

        "comorbidities": ", ".join(
            patient_case.comorbidities.conditions
        ),
    }

    # Remove empty values
    context = {
        key: value
        for key, value in context.items()
        if value not in (
            None,
            "",
            [],
        )
    }

    # --------------------------------------------------------
    # Safety behavior
    # --------------------------------------------------------

    # The ML service may still be queried for information,
    # but a critical red flag is explicitly surfaced to the
    # caller and should prevent autonomous treatment use.
    safety_block = (
        red_flags.get("overall_status")
        == "critical"
    )

    # --------------------------------------------------------
    # ML recommendation
    # --------------------------------------------------------

    if recommend_for_frontend is None:

        recommendation_result = {
            "status": "error",
            "recommendations": [],
            "error": globals().get(
                "ML_IMPORT_ERROR",
                "ML recommendation service unavailable.",
            ),
        }

    else:

        try:

            recommendation_result = (
                recommend_for_frontend(
                    query=query,
                    top_k=top_k,
                    patient_context=context,
                )
            )

        except Exception as exc:

            recommendation_result = {
                "status": "error",
                "recommendations": [],
                "error": str(exc),
            }

    return {
        "status": "success",
        "patient_id": patient_case.patient_id,
        "query": query,

        "safety": {
            "red_flags": red_flags,
            "treatment_recommendation_blocked": safety_block,
        },

        "recommendation": recommendation_result,
    }


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():

    print("=" * 60)
    print("Ayurveda Intelligence API")
    print("=" * 60)

    if detect_red_flags is None:
        print(
            "WARNING: Red flag engine import failed:"
        )
        print(
            globals().get(
                "RED_FLAG_IMPORT_ERROR",
                "Unknown error",
            )
        )
    else:
        print(
            "Red flag engine: READY"
        )

    if recommend_for_frontend is None:
        print(
            "WARNING: ML recommender import failed:"
        )
        print(
            globals().get(
                "ML_IMPORT_ERROR",
                "Unknown error",
            )
        )
    else:
        print(
            "ML recommender: READY"
        )

    print("=" * 60)
