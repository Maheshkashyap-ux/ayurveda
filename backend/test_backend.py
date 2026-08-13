from recommendation import recommend


def test_recommendation():
    result = recommend("fever")

    print("\n========== BACKEND TEST ==========")
    print("User Input       :", result["input"])
    print("Normalized Term  :", result["normalized_term"])

    if result["disease"]:
        print("Disease Found    :", result["disease"]["canonical_name"])
    else:
        print("Disease Found    : None")

    print("\nRecommendations:")

    if result["recommendations"]:
        for formulation in result["recommendations"]:
            print("-", formulation["name"])
    else:
        print("No formulations found.")

    print("==================================\n")


if __name__ == "__main__":
    test_recommendation()
