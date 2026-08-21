import os
import re
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRAIN_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "train_augmented.csv"
)

TEST_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "test_augmented.csv"
)

MODEL_DIR = os.path.join(BASE_DIR, "ml", "models")

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "top5_recommendations.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading datasets...")

train_df = pd.read_csv(TRAIN_FILE)
test_df = pd.read_csv(TEST_FILE)

print(f"Training rows: {len(train_df)}")
print(f"Test rows:     {len(test_df)}")


# ============================================================
# FIND FORMULATION COLUMN
# ============================================================

TARGET = "Formulation"

if TARGET not in train_df.columns:
    raise ValueError(
        f"Could not find '{TARGET}' column.\n"
        f"Available columns: {list(train_df.columns)}"
    )


# ============================================================
# BUILD UNIQUE FORMULATION PROFILES
# ============================================================

print("\nBuilding formulation profiles...")

formulations = (
    train_df[TARGET]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

print(f"Unique formulations: {len(formulations)}")


# ============================================================
# BUILD PATIENT TEXT
# ============================================================

EXCLUDE_COLUMNS = {
    TARGET,
    "Prognosis",
    "Complications",
    "Prevention"
}

feature_columns = [
    col for col in train_df.columns
    if col not in EXCLUDE_COLUMNS
]


def make_patient_text(row):
    values = []

    for col in feature_columns:
        value = row.get(col, "")

        if pd.notna(value):
            text = str(value).strip()

            if text:
                values.append(f"{col}: {text}")

    return " | ".join(values)


train_text = train_df.apply(make_patient_text, axis=1)
test_text = test_df.apply(make_patient_text, axis=1)


# ============================================================
# TF-IDF
# ============================================================

print("\nCreating TF-IDF representations...")

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    min_df=1,
    max_features=20000,
    sublinear_tf=True
)

all_text = pd.concat(
    [
        train_text,
        pd.Series(formulations)
    ],
    ignore_index=True
)

vectorizer.fit(all_text)

train_matrix = vectorizer.transform(train_text)
test_matrix = vectorizer.transform(test_text)
formulation_matrix = vectorizer.transform(formulations)

print(f"TF-IDF features: {len(vectorizer.vocabulary_)}")


# ============================================================
# INGREDIENT EXTRACTION
# ============================================================

def extract_ingredients(formulation):
    """
    Extract the main ingredient names from a formulation.

    This intentionally ignores quantities such as:
    5g, 2g, 200ml, 1 tsp, etc.
    """

    text = str(formulation)

    parts = re.split(r",|\band\b", text, flags=re.IGNORECASE)

    ingredients = []

    for part in parts:

        part = part.strip()

        if not part:
            continue

        # Remove dosage / quantity information
        part = re.sub(
            r"\([^)]*\)",
            "",
            part
        )

        part = re.sub(
            r"\b\d+(\.\d+)?\s*(g|mg|ml|tsp|tbsp|drops?|cloves?|leaves?)\b",
            "",
            part,
            flags=re.IGNORECASE
        )

        part = re.sub(
            r"\s+",
            " ",
            part
        ).strip().lower()

        if part:
            ingredients.append(part)

    return set(ingredients)


formulation_ingredients = {
    formulation: extract_ingredients(formulation)
    for formulation in formulations
}


# ============================================================
# INGREDIENT OVERLAP
# ============================================================

def ingredient_overlap(actual, predicted):

    actual_set = extract_ingredients(actual)
    predicted_set = extract_ingredients(predicted)

    if not actual_set:
        return 0.0

    intersection = actual_set.intersection(predicted_set)

    return len(intersection) / len(actual_set)


# ============================================================
# RECOMMENDATIONS
# ============================================================

print("\nCalculating Top-5 recommendations...")

results = []

top5_exact = 0
top5_50 = 0
top5_75 = 0

overlaps = []


for i in range(len(test_df)):

    patient_vector = test_matrix[i]

    similarities = cosine_similarity(
        patient_vector,
        formulation_matrix
    )[0]

    ranked_indices = similarities.argsort()[::-1]

    actual = str(test_df.iloc[i][TARGET])

    top5 = []

    for rank, idx in enumerate(ranked_indices[:5], start=1):

        formulation = formulations[idx]
        score = float(similarities[idx])

        overlap = ingredient_overlap(
            actual,
            formulation
        )

        top5.append(
            {
                "rank": rank,
                "formulation": formulation,
                "score": score,
                "ingredient_overlap": overlap
            }
        )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    if any(
        item["formulation"] == actual
        for item in top5
    ):
        top5_exact += 1

    best_overlap = max(
        item["ingredient_overlap"]
        for item in top5
    )

    overlaps.append(best_overlap)

    if best_overlap >= 0.50:
        top5_50 += 1

    if best_overlap >= 0.75:
        top5_75 += 1

    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

    row = {
        "patient": str(test_df.iloc[i].get("Disease", "")),
        "actual_formulation": actual
    }

    for item in top5:

        rank = item["rank"]

        row[f"recommendation_{rank}"] = item["formulation"]
        row[f"score_{rank}"] = round(item["score"], 4)
        row[f"ingredient_overlap_{rank}"] = round(
            item["ingredient_overlap"],
            4
        )

    results.append(row)


# ============================================================
# FINAL METRICS
# ============================================================

total = len(test_df)

exact_accuracy = top5_exact / total * 100
match50_accuracy = top5_50 / total * 100
match75_accuracy = top5_75 / total * 100
average_overlap = sum(overlaps) / len(overlaps) * 100


print("\n")
print("=" * 65)
print("TOP-5 RECOMMENDATION QUALITY")
print("=" * 65)

print(f"\nTest samples: {total}")

print(
    f"\nExact formulation appears in Top-5: "
    f"{exact_accuracy:.2f}%"
)

print(
    f"Top-5 ingredient match >= 50%: "
    f"{match50_accuracy:.2f}%"
)

print(
    f"Top-5 ingredient match >= 75%: "
    f"{match75_accuracy:.2f}%"
)

print(
    f"Average best ingredient overlap: "
    f"{average_overlap:.2f}%"
)


# ============================================================
# SAVE RESULTS
# ============================================================

results_df = pd.DataFrame(results)

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SHOW EXAMPLES
# ============================================================

print("\n")
print("=" * 65)
print("SAMPLE TOP-5 RECOMMENDATIONS")
print("=" * 65)

for i in range(min(10, len(results))):

    row = results[i]

    print("\n" + "-" * 65)

    print(
        f"Patient: {row['patient']}"
    )

    print(
        f"Actual: {row['actual_formulation']}"
    )

    print("\nRecommendations:")

    for rank in range(1, 6):

        formulation = row[f"recommendation_{rank}"]
        score = row[f"score_{rank}"]
        overlap = row[f"ingredient_overlap_{rank}"]

        print(
            f"{rank}. {formulation}"
        )

        print(
            f"   similarity={score:.3f} | "
            f"ingredient match={overlap * 100:.1f}%"
        )


print("\n")
print("=" * 65)
print("EVALUATION COMPLETE")
print("=" * 65)

print("\nResults saved to:")
print(OUTPUT_FILE)
