"""
Ayurveda Intelligence
Backend Test Suite

Tests the main recommendation pipeline using representative
prototype queries.

Test coverage:
    1. Empty input
    2. Synonym-based search
    3. Direct canonical-term search
    4. Unknown search term
    5. Recommendation structure
"""

from recommendation import (
    normalize_input,
    resolve_terminology,
    find_disease,
    find_formulations,
    recommend,
)

from data_loader import load_knowledge_base


# ============================================================
# TEST HELPERS
# ============================================================

def check(condition, message):
    """
    Simple assertion helper for readable terminal output.
    """

    if not condition:
        raise AssertionError(message)

    print(f"[PASS] {message}")


# ============================================================
# TEST 1 — INPUT NORMALIZATION
# ============================================================

def test_input_normalization():

    result = normalize_input("  FEVER  ")

    check(
        result == "fever",
        "Input is correctly normalized."
    )


# ============================================================
# TEST 2 — TERMINOLOGY RESOLUTION
# ============================================================

def test_terminology_resolution():

    knowledge_base = load_knowledge_base()

    synonyms = knowledge_base["synonyms"]

    result = resolve_terminology(
        "fever",
        synonyms
    )

    check(
        result["canonical_term"] != "",
        "Terminology resolver returns a canonical term."
    )

    print(
        f"      fever → {result['canonical_term']}"
    )


# ============================================================
# TEST 3 — DISEASE LOOKUP
# ============================================================

def test_disease_lookup():

    knowledge_base = load_knowledge_base()

    diseases = knowledge_base["diseases"]

    result = find_disease(
        "jvara",
        diseases
    )

    check(
        result is not None,
        "Disease lookup finds the canonical condition."
    )


# ============================================================
# TEST 4 — FORMULATION RETRIEVAL
# ============================================================

def test_formulation_retrieval():

    knowledge_base = load_knowledge_base()

    diseases = knowledge_base["diseases"]
    formulations = knowledge_base["formulations"]

    disease = find_disease(
        "jvara",
        diseases
    )

    if disease is None:
        raise AssertionError(
            "Cannot test formulation retrieval because "
            "the Jvara disease record was not found."
        )

    candidates = find_formulations(
        disease,
        formulations
    )

    check(
        isinstance(candidates, list),
        "Formulation retrieval returns a list."
    )

    print(
        f"      Candidates found: {len(candidates)}"
    )


# ============================================================
# TEST 5 — COMPLETE RECOMMENDATION PIPELINE
# ============================================================

def test_recommendation_pipeline():

    result = recommend("fever")

    check(
        "status" in result,
        "Recommendation result contains a status."
    )

    check(
        "normalized_term" in result,
        "Recommendation result contains normalized terminology."
    )

    check(
        "recommendations" in result,
        "Recommendation result contains recommendations."
    )

    print(
        f"      Status: {result['status']}"
    )

    print(
        f"      Normalized term: "
        f"{result['normalized_term']}"
    )

    print(
        f"      Recommendations: "
        f"{len(result['recommendations'])}"
    )


# ============================================================
# TEST 6 — UNKNOWN TERM
# ============================================================

def test_unknown_term():

    result = recommend(
        "unknown_term_xyz"
    )

    check(
        result["status"] == "no_match",
        "Unknown terminology is handled safely."
    )

    check(
        result["recommendations"] == [],
        "Unknown terminology does not produce fabricated results."
    )


# ============================================================
# TEST 7 — EMPTY INPUT
# ============================================================

def test_empty_input():

    result = recommend("")

    check(
        result["status"] == "invalid_input",
        "Empty input is rejected safely."
    )

    check(
        result["recommendations"] == [],
        "Empty input produces no recommendations."
    )


# ============================================================
# TEST RUNNER
# ============================================================

def run_tests():

    print()
    print("==============================================")
    print(" Ayurveda Intelligence — Backend Tests")
    print("==============================================")

    tests = [
        test_input_normalization,
        test_terminology_resolution,
        test_disease_lookup,
        test_formulation_retrieval,
        test_recommendation_pipeline,
        test_unknown_term,
        test_empty_input,
    ]

    passed = 0

    for test in tests:

        print()
        print(f"Running: {test.__name__}")

        try:

            test()
            passed += 1

        except Exception as error:

            print(
                f"[FAIL] {error}"
            )

    print()
    print("==============================================")
    print(
        f"Result: {passed}/{len(tests)} tests passed"
    )
    print("==============================================")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_tests()
