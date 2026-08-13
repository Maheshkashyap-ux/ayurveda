from data_loader import (
    load_diseases,
    load_formulations,
    load_synonyms
)


def normalize_input(user_input, synonyms):
    """Convert a common term into its canonical Ayurvedic term."""
    user_input = user_input.strip().lower()

    for item in synonyms:
        if item["synonym"].lower() == user_input:
            return item["canonical_term"]

        if item["canonical_term"].lower() == user_input:
            return item["canonical_term"]

    return user_input


def find_disease(term, diseases):
    """Find a disease using its canonical or common name."""
    term = term.lower()

    for disease in diseases:
        if disease["canonical_name"].lower() == term:
            return disease

        if disease["common_name"].lower() == term:
            return disease

    return None


def find_formulations(disease, formulations):
    """Find formulations associated with the identified condition."""
    results = []

    condition = disease["canonical_name"].lower()

    for formulation in formulations:
        if condition in formulation["associated_condition"].lower():
            results.append(formulation)

    return results


def recommend(user_input):
    diseases = load_diseases()
    formulations = load_formulations()
    synonyms = load_synonyms()

    canonical_term = normalize_input(user_input, synonyms)

    disease = find_disease(canonical_term, diseases)

    if not disease:
        return {
            "input": user_input,
            "normalized_term": canonical_term,
            "disease": None,
            "recommendations": []
        }

    recommendations = find_formulations(disease, formulations)

    return {
        "input": user_input,
        "normalized_term": canonical_term,
        "disease": disease,
        "recommendations": recommendations
    }


if __name__ == "__main__":
    result = recommend("fever")

    print("Input:", result["input"])
    print("Normalized:", result["normalized_term"])

    if result["disease"]:
        print("Disease:", result["disease"]["canonical_name"])

    print("Recommendations:")

    for formulation in result["recommendations"]:
        print("-", formulation["name"])
