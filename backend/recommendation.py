"""
Ayurveda Intelligence
Recommendation Engine

This module contains the core prototype recommendation pipeline.

Pipeline:

    User Input
        ↓
    Input Normalization
        ↓
    Terminology Resolution
        ↓
    Disease / Condition Matching
        ↓
    Formulation Retrieval
        ↓
    Candidate Ranking
        ↓
    Explainable Result
"""

from data_loader import load_knowledge_base
from config import MAX_RECOMMENDATIONS, MIN_MATCH_SCORE


# ============================================================
# INPUT NORMALIZATION
# ============================================================

def normalize_input(query):
    """
    Normalize a user-provided search term.

    Current prototype operations:
        - Convert input to string
        - Remove leading/trailing whitespace
        - Convert to lowercase

    Returns:
        str: normalized search term
    """

    if query is None:
        return ""

    return str(query).strip().lower()


# ============================================================
# TERMINOLOGY RESOLUTION
# ============================================================

def resolve_terminology(query, synonyms):
    """
    Resolve a user term using the synonym dataset.

    Example:

        Input:
            fever

        Result:
            Jvara

    Returns:
        dict containing the normalized/canonical term
        and match information.
    """

    normalized_query = normalize_input(query)

    if not normalized_query:
        return {
            "canonical_term": "",
            "match_type": "empty",
            "matched": False,
        }

    for record in synonyms:

        synonym = str(
            record.get("synonym", "")
        ).strip().lower()

        canonical = str(
            record.get("canonical_term", "")
        ).strip()

        if synonym == normalized_query:
            return {
                "canonical_term": canonical,
                "match_type": "synonym",
                "matched": True,
            }

    # If no synonym exists, continue using the user's
    # original normalized term as the search term.

    return {
        "canonical_term": normalized_query,
        "match_type": "direct",
        "matched": False,
    }


# ============================================================
# DISEASE / CONDITION LOOKUP
# ============================================================

def find_disease(canonical_term, diseases):
    """
    Find a disease / condition record using the canonical term.

    The prototype checks:
        - canonical_name
        - common_name

    Returns:
        dict or None
    """

    search_term = normalize_input(canonical_term)

    if not search_term:
        return None

    for disease in diseases:

        canonical_name = str(
            disease.get("canonical_name", "")
        ).strip().lower()

        common_name = str(
            disease.get("common_name", "")
        ).strip().lower()

        if search_term == canonical_name:
            return disease

        if search_term == common_name:
            return disease

    return None


# ============================================================
# FORMULATION RETRIEVAL
# ============================================================

def find_formulations(disease, formulations):
    """
    Retrieve formulations associated with the identified disease.

    Returns:
        list[dict]
    """

    if not disease:
        return []

    canonical_name = str(
        disease.get("canonical_name", "")
    ).strip().lower()

    common_name = str(
        disease.get("common_name", "")
    ).strip().lower()

    candidates = []

    for formulation in formulations:

        associated_condition = str(
            formulation.get("associated_condition", "")
        ).strip().lower()

        if associated_condition in (
            canonical_name,
            common_name,
        ):
            candidates.append(formulation)

    return candidates


# ============================================================
# CANDIDATE SCORING
# ============================================================

def calculate_match_score(
    terminology_result,
    disease,
    formulation
):
    """
    Calculate a simple deterministic prototype match score.

    This is NOT a clinical probability.

    Score components:

        Terminology resolution  : 30 points
        Disease match           : 40 points
        Formulation association : 30 points

        Maximum                 : 100
    """

    score = 0
    reasons = []

    # --------------------------------------------------------
    # Terminology signal
    # --------------------------------------------------------

    if terminology_result.get("matched"):

        score += 30

        reasons.append(
            "User input matched a known synonym."
        )

    else:

        score += 15

        reasons.append(
            "User input was processed using direct terminology matching."
        )

    # --------------------------------------------------------
    # Disease signal
    # --------------------------------------------------------

    if disease:

        score += 40

        reasons.append(
            "A matching disease / condition record was found."
        )

    # --------------------------------------------------------
    # Formulation association
    # --------------------------------------------------------

    if formulation:

        score += 30

        reasons.append(
            "The formulation is associated with the identified condition."
        )

    return min(score, 100), reasons


# ============================================================
# RESULT EXPLANATION
# ============================================================

def build_explanation(
    query,
    terminology_result,
    disease,
    formulation,
    score,
    reasons
):
    """
    Build the explainability information for a recommendation.
    """

    return {
        "query": query,
        "normalized_term": terminology_result.get(
            "canonical_term",
            ""
        ),
        "match_type": terminology_result.get(
            "match_type",
            "unknown"
        ),
        "condition": (
            disease.get("canonical_name")
            if disease
            else None
        ),
        "formulation": (
            formulation.get("name")
            if formulation
            else None
        ),
        "match_score": score,
        "reasons": reasons,
    }


# ============================================================
# MAIN RECOMMENDATION FUNCTION
# ============================================================

def recommend(query):
    """
    Run the complete recommendation pipeline.

    Returns a structured result suitable for future API
    or frontend integration.
    """

    knowledge_base = load_knowledge_base()

    diseases = knowledge_base["diseases"]
    formulations = knowledge_base["formulations"]
    synonyms = knowledge_base["synonyms"]

    normalized_query = normalize_input(query)

    # --------------------------------------------------------
    # Empty input
    # --------------------------------------------------------

    if not normalized_query:

        return {
            "query": query,
            "normalized_term": "",
            "condition": None,
            "recommendations": [],
            "status": "invalid_input",
            "message": "Please provide a search term.",
        }

    # --------------------------------------------------------
    # Stage 1 — Terminology Resolution
    # --------------------------------------------------------

    terminology_result = resolve_terminology(
        normalized_query,
        synonyms
    )

    canonical_term = terminology_result[
        "canonical_term"
    ]

    # --------------------------------------------------------
    # Stage 2 — Disease Lookup
    # --------------------------------------------------------

    disease = find_disease(
        canonical_term,
        diseases
    )

    # --------------------------------------------------------
    # No disease found
    # --------------------------------------------------------

    if disease is None:

        return {
            "query": query,
            "normalized_term": canonical_term,
            "condition": None,
            "recommendations": [],
            "status": "no_match",
            "message": (
                "No matching disease or condition was "
                "found in the current prototype dataset."
            ),
        }

    # --------------------------------------------------------
    # Stage 3 — Formulation Retrieval
    # --------------------------------------------------------

    candidates = find_formulations(
        disease,
        formulations
    )

    # --------------------------------------------------------
    # No formulation found
    # --------------------------------------------------------

    if not candidates:

        return {
            "query": query,
            "normalized_term": canonical_term,
            "condition": disease,
            "recommendations": [],
            "status": "no_formulation",
            "message": (
                "The condition was identified, but no associated "
                "formulation was found in the current dataset."
            ),
        }

    # --------------------------------------------------------
    # Stage 4 — Candidate Ranking
    # --------------------------------------------------------

    ranked_candidates = []

    for formulation in candidates:

        score, reasons = calculate_match_score(
            terminology_result,
            disease,
            formulation
        )

        if score < MIN_MATCH_SCORE:
            continue

        explanation = build_explanation(
            query,
            terminology_result,
            disease,
            formulation,
            score,
            reasons
        )

        ranked_candidates.append(
            {
                "formulation": formulation,
                "match_score": score,
                "explanation": explanation,
            }
        )

    # Highest score first

    ranked_candidates.sort(
        key=lambda item: item["match_score"],
        reverse=True
    )

    # Limit result count

    ranked_candidates = ranked_candidates[
        :MAX_RECOMMENDATIONS
    ]

    # --------------------------------------------------------
    # Final Result
    # --------------------------------------------------------

    return {
        "query": query,
        "normalized_term": canonical_term,
        "condition": disease,
        "recommendations": ranked_candidates,
        "status": "success",
        "message": (
            "Matching formulation candidates "
            "were retrieved from the prototype knowledge base."
        ),
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print("Ayurveda Intelligence — Recommendation Test")
    print("-------------------------------------------")

    test_queries = [
        "fever",
        "Jvara",
        "unknown_term",
    ]

    for query in test_queries:

        print()
        print(f"Query: {query}")

        result = recommend(query)

        print(
            f"Status: {result['status']}"
        )

        print(
            f"Normalized term: "
            f"{result['normalized_term']}"
        )

        if result["recommendations"]:

            for item in result["recommendations"]:

                formulation = item["formulation"]

                print(
                    f"  → {formulation.get('name')} "
                    f"({item['match_score']}/100)"
                )

        else:

            print(
                f"Message: {result['message']}"
            )
