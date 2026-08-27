"""
Pydantic models for Ayurveda Intelligence.

Step 1:
Backend data models for Patient Case intake.

Existing recommendation models are preserved.
"""

from typing import Any

from pydantic import BaseModel, Field


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
    """
    Complete patient case structure.

    This is the foundation for the new case-taking system.
    It does not replace the existing recommendation engine.
    """

    patient_id: str | None = None

    age: int | None = None
    gender: str = ""

    symptoms: Symptoms = Field(default_factory=Symptoms)

    prakriti: Prakriti = Field(default_factory=Prakriti)

    lifestyle: Lifestyle = Field(default_factory=Lifestyle)

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
# EXISTING RECOMMENDATION MODELS
# ============================================================

class RecommendationSignals(BaseModel):

    disease: float = 0.0
    context: float = 0.0
    profile: float = 0.0
    ingredients: float = 0.0
    prior: float = 0.0


class RecommendationItem(BaseModel):

    rank: int

    formulation: str

    display_name: str

    score: float

    score_percent: float

    ingredient_match: float | None = None

    ingredient_match_percent: float | None = None

    signals: RecommendationSignals


class RecommendationResponse(BaseModel):

    status: str

    query: str

    recommendations: list[RecommendationItem]

    model: dict[str, Any]
