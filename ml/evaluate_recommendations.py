import os
import re
import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEST_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "test_augmented.csv"
)

MODEL_FILE = os.path.join(
    BASE_DIR,
    "ml",
    "models",
    "weighted_formulation_ranker.joblib"
)

VECTORIZER_FILE = os.path.join(
    BASE_DIR,
    "ml",
    "models",
    "weighted_formulation_vectorizer.joblib"
)


# ============================================================
# LOAD FILES
# ============================================================

print("Loading test dataset...")

test_df = pd.read_csv(TEST_FILE)

print(f"Test rows: {len(test_df)}")


print("\nLoading ranking model...")

model = joblib.load(MODEL_FILE)
vectorizer = joblib.load(VECTORIZER_FILE)


# ============================================================
# FIND COLUMNS
# ============================================================

TARGET = "Formulation"

if TARGET not in test_df.columns:
    raise ValueError(
        f"Could not find '{TARGET}' column.\n"
        f"Available columns:\n{list(test_df.columns)}"
    )


feature_columns = [
    c for c in test_df.columns
    if c != TARGET
]


# ============================================================
# CREATE PATIENT TEXT
# ============================================================

def row_to_text(row):
    parts = []

    for column in feature_columns:
        value = row[column]

        if pd.notna(value):
            text = str(value).strip()

            if text:
                parts.append(
                    f"{column}: {text}"
                )

    return " | ".join(parts)


print("\nCreating patient representations...")

test_text = test_df.apply(
    row_to_text,
    axis=1
)


# ============================================================
# GET FORMULATION PROFILES
# ============================================================

print("Building formulation profiles...")

# The ranking model stores the formulation profiles.
# We try the common attribute names used by our previous scripts.

formulations = None

if hasattr(model, "formulations"):
    formulations = model.formulations

elif hasattr(model, "classes_"):
    formulations = model.classes_

elif isinstance(model, dict):

    for key in [
        "formulations",
        "classes",
        "labels",
        "targets"
    ]:
        if key in model:
            formulations = model[key]
            break


if formulations is None:
    raise ValueError(
        "Could not find formulation list inside the saved model."
    )


formulations = list(formulations)

print(f"Unique formulations: {len(formulations)}")


# ============================================================
# CREATE FORMULATION TEXT
# ============================================================

formulation_text = [
    str(x)
    for x in formulations
]


# ============================================================
# TF-IDF
# ============================================================

print("\nCreating TF-IDF representations...")

patient_vectors = vectorizer.transform(test_text)

formulation_vectors = vectorizer.transform(
    formulation_text
)


# ============================================================
# SIMILARITY
# ============================================================

print("Calculating similarities...")

similarity_matrix = cosine_similarity(
    patient_vectors,
    formulation_vectors
)


# ============================================================
# INGREDIENT EXTRACTION
# ============================================================

def normalize(text):
    text = str(text).lower()

    # Remove quantities
    text = re.sub(
        r"\([^)]*\)",
        "",
        text
    )

    # Remove common preparation words
    remove_words = [
        "daily",
        "warm water",
        "water",
        "milk",
        "apply on skin or consume",
        "as needed"
    ]

    for word in remove_words:
        text = text.replace(word, "")

    return text


def extract_ingredients(formulation):
    """
    Extract the main ingredient/herb names.

    This is intentionally simple.
    It is used only for evaluating similarity,
    NOT for medical recommendations.
    """

    text = normalize(formulation)

    # Split formulation into components
    pieces = re.split(
        r",|\+",
        text
    )

    ingredients = set()

    for piece in pieces:

        piece = piece.strip()

        if not piece:
            continue

        # Remove remaining punctuation
        piece = re.sub(
            r"[^a-zA-Z ]",
            " ",
            piece
        )

        words = piece.split()

        if not words:
            continue

        # Keep the meaningful words
        meaningful = [
            word
            for word in words
            if len(word) > 2
        ]

        if meaningful:
            ingredients.add(
                " ".join(meaningful)
            )

    return ingredients


# ============================================================
# OVERLAP SCORE
# ============================================================

def ingredient_overlap(actual, predicted):

    actual_set = extract_ingredients(actual)
    predicted_set = extract_ingredients(predicted)

    if not actual_set:
        return 0.0

    intersection = (
        actual_set &
        predicted_set
    )

    return len(intersection) / len(actual_set)


# ============================================================
# EVALUATION
# ============================================================

top1 = 0
top3 = 0
top5 = 0

close_50 = 0
close_75 = 0

overlap_scores = []

results = []


print("\n")
print("=" * 65)
print("RECOMMENDATION QUALITY EVALUATION")
print("=" * 65)


for i in range(len(test_df)):

    actual = str(
        test_df.iloc[i][TARGET]
    )

    scores = similarity_matrix[i]

    ranked_indices = scores.argsort()[::-1]

    ranked_formulations = [
        formulations[j]
        for j in ranked_indices
    ]

    # --------------------------------------------------------
    # TOP K
    # --------------------------------------------------------

    if actual == str(ranked_formulations[0]):
        top1 += 1

    if actual in [
        str(x)
        for x in ranked_formulations[:3]
    ]:
        top3 += 1

    if actual in [
        str(x)
        for x in ranked_formulations[:5]
    ]:
        top5 += 1


    # --------------------------------------------------------
    # BEST INGREDIENT MATCH IN TOP 5
    # --------------------------------------------------------

    best_overlap = 0.0
    best_prediction = None

    for prediction in ranked_formulations[:5]:

        overlap = ingredient_overlap(
            actual,
            prediction
        )

        if overlap > best_overlap:

            best_overlap = overlap
            best_prediction = prediction


    overlap_scores.append(
        best_overlap
    )

    if best_overlap >= 0.50:
        close_50 += 1

    if best_overlap >= 0.75:
        close_75 += 1


    results.append({
        "patient": test_df.iloc[i].get(
            "Disease",
            "Unknown"
        ),
        "actual": actual,
        "top_prediction": ranked_formulations[0],
        "best_top5_match": best_prediction,
        "best_overlap": best_overlap
    })


# ============================================================
# RESULTS
# ============================================================

total = len(test_df)

print()
print(f"Test samples: {total}")

print()
print(
    f"Exact Top-1 Accuracy: "
    f"{top1 / total * 100:.2f}%"
)

print(
    f"Exact Top-3 Accuracy: "
    f"{top3 / total * 100:.2f}%"
)

print(
    f"Exact Top-5 Accuracy: "
    f"{top5 / total * 100:.2f}%"
)

print()
print(
    f"Ingredient Match >= 50%: "
    f"{close_50 / total * 100:.2f}%"
)

print(
    f"Ingredient Match >= 75%: "
    f"{close_75 / total * 100:.2f}%"
)

print()
print(
    f"Average Best Top-5 Ingredient Overlap: "
    f"{sum(overlap_scores) / len(overlap_scores) * 100:.2f}%"
)


# ============================================================
# SHOW EXAMPLES
# ============================================================

print()
print("=" * 65)
print("EXAMPLES")
print("=" * 65)

for result in results[:10]:

    print()
    print("-" * 65)

    print(
        f"Patient: "
        f"{result['patient']}"
    )

    print(
        f"Actual formulation:\n"
        f"  {result['actual']}"
    )

    print(
        f"Top prediction:\n"
        f"  {result['top_prediction']}"
    )

    print(
        f"Best Top-5 ingredient match:\n"
        f"  {result['best_top5_match']}"
    )

    print(
        f"Ingredient overlap: "
        f"{result['best_overlap'] * 100:.1f}%"
    )


# ============================================================
# SAVE RESULTS
# ============================================================

output_file = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "recommendation_evaluation.csv"
)

pd.DataFrame(results).to_csv(
    output_file,
    index=False
)

print()
print("=" * 65)
print("EVALUATION COMPLETE")
print("=" * 65)

print()
print(
    f"Detailed results saved to:\n"
    f"{output_file}"
)
