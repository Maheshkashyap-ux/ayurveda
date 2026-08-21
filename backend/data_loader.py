"""
Ayurveda Intelligence
Backend Test Suite
"""

from recommendation import (
    normalize_text,
    extract_ingredients,
    calculate_ingredient_match,
    recommend,
    get_model_status,
)


def check(
    condition,
    message,
):

    if not condition:

        raise AssertionError(
            message
        )

    print(
        f"[PASS] {message}"
    )


# ============================================================
# TEST 1
# ============================================================

def test_text_normalization():

    result = normalize_text(
        "  Leigh   Syndrome  "
    )

    check(
        result == "leigh syndrome",
        "Text normalization works.",
    )


# ============================================================
# TEST 2
# ============================================================

def test_ingredient_extraction():

    result = extract_ingredients(
        "Ashwagandha (5g), Brahmi (2g), Warm water (200ml)"
    )

    check(
        "ashwagandha" in result,
        "Ashwagandha extracted.",
    )

    check(
        "brahmi" in result,
        "Brahmi extracted.",
    )

    check(
        "warm water" in result,
        "Warm water extracted.",
    )


# ============================================================
# TEST 3
# ============================================================

def test_ingredient_match():

    score = calculate_ingredient_match(
        "Ashwagandha (5g), Brahmi (2g), Warm water (200ml)",
        "Ashwagandha (5g), Warm water (200ml)",
    )

    check(
        score > 0,
        "Ingredient overlap calculation works.",
    )

    print(
        f"      Match: {score}%"
    )


# ============================================================
# TEST 4
# ============================================================

def test_model_exists():

    status = get_model_status()

    check(
        status["exists"],
        "Final ML model exists.",
    )

    print(
        f"      Model: {status['path']}"
    )


# ============================================================
# TEST 5
# ============================================================

def test_recommendation():

    result = recommend(
        "Leigh Syndrome",
        limit=3,
    )

    check(
        "status" in result,
        "Recommendation contains status.",
    )

    check(
        "recommendations" in result,
        "Recommendation contains recommendations.",
    )

    check(
        len(
            result["recommendations"]
        ) <= 3,
        "Recommendation respects Top-3 limit.",
    )

    print()

    for item in result[
        "recommendations"
    ]:

        print(
            f"      {item['rank']}. "
            f"{item['formulation']}"
        )


# ============================================================
# TEST 6
# ============================================================

def test_empty_query():

    result = recommend(
        "",
        limit=3,
    )

    check(
        result["status"] == "invalid_input",
        "Empty query is rejected.",
    )


# ============================================================
# TEST RUNNER
# ============================================================

def run_tests():

    print()
    print("=" * 70)
    print(
        "AYURVEDA INTELLIGENCE — BACKEND TESTS"
    )
    print("=" * 70)

    tests = [
        test_text_normalization,
        test_ingredient_extraction,
        test_ingredient_match,
        test_model_exists,
        test_recommendation,
        test_empty_query,
    ]

    passed = 0

    for test in tests:

        print()

        print(
            f"Running: {test.__name__}"
        )

        try:

            test()

            passed += 1

        except Exception as error:

            print(
                f"[FAIL] {error}"
            )

    print()
    print("=" * 70)

    print(
        f"RESULT: {passed}/{len(tests)} tests passed"
    )

    print("=" * 70)

    return passed == len(tests)


if __name__ == "__main__":

    success = run_tests()

    raise SystemExit(
        0 if success else 1
    )
