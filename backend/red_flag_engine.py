"""
Ayurveda Intelligence
Red Flag Detection Engine

Step 3:
Detect potentially concerning symptoms, contraindications,
and risk factors from a structured PatientCase.

This module does NOT diagnose disease.
It only identifies safety flags for clinical decision support.
"""

from typing import Any, Dict, List


# ============================================================
# RED FLAG RULES
# ============================================================

RED_FLAG_RULES = {

    "severe_breathing_difficulty": {
        "keywords": [
            "severe shortness of breath",
            "difficulty breathing",
            "breathing difficulty",
            "cannot breathe",
            "unable to breathe",
        ],
        "severity": "critical",
        "message": (
            "Severe breathing difficulty reported. "
            "Urgent medical evaluation may be required."
        ),
    },

    "chest_pain": {
        "keywords": [
            "chest pain",
            "pressure in chest",
            "chest pressure",
            "tightness in chest",
        ],
        "severity": "critical",
        "message": (
            "Chest pain or pressure reported. "
            "Urgent medical evaluation may be required."
        ),
    },

    "loss_of_consciousness": {
        "keywords": [
            "fainted",
            "fainting",
            "loss of consciousness",
            "unconscious",
            "passed out",
        ],
        "severity": "critical",
        "message": (
            "Loss of consciousness reported. "
            "Urgent medical evaluation may be required."
        ),
    },

    "severe_bleeding": {
        "keywords": [
            "severe bleeding",
            "heavy bleeding",
            "vomiting blood",
            "coughing blood",
            "blood in vomit",
        ],
        "severity": "critical",
        "message": (
            "Significant bleeding reported. "
            "Urgent medical evaluation may be required."
        ),
    },

    "severe_allergic_reaction": {
        "keywords": [
            "anaphylaxis",
            "severe allergic reaction",
            "swelling of throat",
            "swollen throat",
            "difficulty swallowing",
        ],
        "severity": "critical",
        "message": (
            "Possible severe allergic reaction reported. "
            "Urgent medical evaluation may be required."
        ),
    },

    "severe_confusion": {
        "keywords": [
            "severe confusion",
            "confused and disoriented",
            "altered consciousness",
            "not responding normally",
        ],
        "severity": "critical",
        "message": (
            "Significant alteration in mental status reported. "
            "Urgent medical evaluation may be required."
        ),
    },

    "high_fever": {
        "keywords": [
            "very high fever",
            "high fever",
            "fever above 103",
            "fever above 104",
        ],
        "severity": "high",
        "message": (
            "High fever reported. Further clinical assessment "
            "is recommended."
        ),
    },

    "persistent_vomiting": {
        "keywords": [
            "persistent vomiting",
            "continuous vomiting",
            "cannot keep fluids down",
            "unable to keep fluids down",
        ],
        "severity": "high",
        "message": (
            "Persistent vomiting or inability to retain fluids "
            "reported. Further clinical assessment is recommended."
        ),
    },

    "severe_dehydration": {
        "keywords": [
            "severe dehydration",
            "extreme dehydration",
            "no urine",
            "very little urine",
        ],
        "severity": "high",
        "message": (
            "Possible severe dehydration reported. "
            "Further clinical assessment is recommended."
        ),
    },

    "pregnancy": {
        "keywords": [
            "pregnant",
            "pregnancy",
        ],
        "severity": "moderate",
        "message": (
            "Pregnancy reported. Formulation and herbal "
            "recommendations require additional safety review."
        ),
    },

    "drug_interaction_risk": {
        "keywords": [
            "blood thinner",
            "anticoagulant",
            "insulin",
            "chemotherapy",
            "immunosuppressant",
        ],
        "severity": "moderate",
        "message": (
            "Medication-related interaction risk may be present. "
            "Medication review is recommended before formulation guidance."
        ),
    },
}


# ============================================================
# TEXT EXTRACTION
# ============================================================

def _collect_case_text(patient_case: Any) -> str:
    """
    Convert relevant PatientCase fields into searchable text.
    """

    parts: List[str] = []

    def add(value: Any) -> None:
        if value is None:
            return

        if isinstance(value, str):
            if value.strip():
                parts.append(value)

        elif isinstance(value, list):
            for item in value:
                add(item)

        elif isinstance(value, dict):
            for item in value.values():
                add(item)

        else:
            parts.append(str(value))

    if hasattr(patient_case, "model_dump"):
        data = patient_case.model_dump()
    elif isinstance(patient_case, dict):
        data = patient_case
    else:
        return ""

    add(data)

    return " ".join(parts).lower()


# ============================================================
# RULE MATCHING
# ============================================================

def _matches_rule(
    text: str,
    keywords: List[str],
) -> bool:
    """
    Return True when any rule keyword occurs in the case text.
    """

    return any(
        keyword.lower() in text
        for keyword in keywords
    )


# ============================================================
# MAIN ENGINE
# ============================================================

def detect_red_flags(
    patient_case: Any,
) -> Dict[str, Any]:
    """
    Analyze a PatientCase and return structured safety flags.

    This engine does not diagnose the patient.
    """

    text = _collect_case_text(patient_case)

    flags: List[Dict[str, Any]] = []

    for rule_id, rule in RED_FLAG_RULES.items():

        if _matches_rule(
            text,
            rule["keywords"],
        ):
            flags.append(
                {
                    "id": rule_id,
                    "severity": rule["severity"],
                    "message": rule["message"],
                }
            )

    # --------------------------------------------------------
    # Overall status
    # --------------------------------------------------------

    if any(
        flag["severity"] == "critical"
        for flag in flags
    ):
        overall_status = "critical"

    elif any(
        flag["severity"] == "high"
        for flag in flags
    ):
        overall_status = "high"

    elif flags:
        overall_status = "moderate"

    else:
        overall_status = "none"

    return {
        "status": "success",
        "overall_status": overall_status,
        "red_flags_detected": len(flags) > 0,
        "count": len(flags),
        "flags": flags,
    }
