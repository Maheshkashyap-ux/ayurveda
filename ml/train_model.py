import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
MODEL_DIR = BASE_DIR / "ml" / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_FILE = DATA_DIR / "train_augmented.csv"
VAL_FILE = DATA_DIR / "validation_augmented.csv"
TEST_FILE = DATA_DIR / "test_augmented.csv"

MODEL_FILE = MODEL_DIR / "ayurveda_tfidf_model.joblib"
VECTORIZER_FILE = MODEL_DIR / "ayurveda_tfidf_vectorizer.joblib"

TARGET = "Formulation"


# =========================================================
# LOAD DATA
# =========================================================

print("Loading augmented datasets...")

train_df = pd.read_csv(TRAIN_FILE)
val_df = pd.read_csv(VAL_FILE)
test_df = pd.read_csv(TEST_FILE)

print(f"Training rows:   {len(train_df)}")
print(f"Validation rows: {len(val_df)}")
print(f"Test rows:       {len(test_df)}")


# =========================================================
# PREPARE TEXT
# =========================================================

# Remove bookkeeping column
for df in [train_df, val_df, test_df]:
    if "_synthetic_training_variant" in df.columns:
        df.drop(columns=["_synthetic_training_variant"], inplace=True)


def make_text(df):
    """
    Combine the useful patient/formulation-related fields
    into one text representation.
    """

    columns = [
        "Disease",
        "Hindi Name",
        "Marathi Name",
        "Symptoms",
        "Diagnosis & Tests",
        "Symptom Severity",
        "Duration of Treatment",
        "Medical History",
        "Current Medications",
        "Risk Factors",
        "Environmental Factors",
        "Sleep Patterns",
        "Stress Levels",
        "Physical Activity Levels",
        "Family History",
        "Dietary Habits",
        "Allergies (Food/Env)",
        "Seasonal Variation",
        "Age Group",
        "Gender",
        "Occupation and Lifestyle",
        "Cultural Preferences",
        "Herbal/Alternative Remedies",
        "Ayurvedic Herbs",
        "Doshas",
        "Constitution/Prakriti",
        "Diet and Lifestyle Recommendations",
        "Yoga & Physical Therapy",
        "Medical Intervention",
        "Patient Recommendations",
    ]

    existing = [c for c in columns if c in df.columns]

    return (
        df[existing]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
    )


X_train_text = make_text(train_df)
X_val_text = make_text(val_df)
X_test_text = make_text(test_df)

y_train = train_df[TARGET].astype(str)
y_val = val_df[TARGET].astype(str)
y_test = test_df[TARGET].astype(str)


# =========================================================
# TF-IDF
# =========================================================

print("\nCreating TF-IDF representation...")

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    min_df=1,
    max_features=15000,
    sublinear_tf=True
)

X_train = vectorizer.fit_transform(X_train_text)
X_val = vectorizer.transform(X_val_text)
X_test = vectorizer.transform(X_test_text)

print(f"TF-IDF features: {X_train.shape[1]}")


# =========================================================
# TRAIN
# =========================================================

print("\nTraining Logistic Regression model...")

model = LogisticRegression(
    C=4.0,
    max_iter=2000,
    solver="liblinear",
    random_state=42
)

model.fit(X_train, y_train)

print("Training complete.")


# =========================================================
# TOP-1 ACCURACY
# =========================================================

print("\nEvaluating test set...")

predictions = model.predict(X_test)

top1 = accuracy_score(y_test, predictions)

print(f"Test Top-1 Accuracy: {top1:.2%}")


# =========================================================
# TOP-K ACCURACY
# =========================================================

probabilities = model.predict_proba(X_test)
classes = model.classes_


def calculate_top_k(k):
    correct = 0

    for i, actual in enumerate(y_test):
        top_indices = np.argsort(probabilities[i])[-k:]
        top_classes = classes[top_indices]

        if actual in top_classes:
            correct += 1

    return correct / len(y_test)


top3 = calculate_top_k(3)
top5 = calculate_top_k(5)

print(f"Top-3 Accuracy: {top3:.2%}")
print(f"Top-5 Accuracy: {top5:.2%}")


# =========================================================
# SHOW SAMPLE RECOMMENDATIONS
# =========================================================

print("\nSample Top-5 recommendations:")

for i in range(min(5, len(test_df))):

    top_indices = np.argsort(probabilities[i])[-5:][::-1]

    print("\nPatient:", test_df.iloc[i]["Disease"])
    print("Actual formulation:", y_test.iloc[i])

    for rank, idx in enumerate(top_indices, start=1):
        print(
            f"{rank}. {classes[idx]} "
            f"({probabilities[i][idx]:.2%})"
        )


# =========================================================
# CLASSIFICATION REPORT
# =========================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)


# =========================================================
# SAVE MODEL
# =========================================================

joblib.dump(model, MODEL_FILE)
joblib.dump(vectorizer, VECTORIZER_FILE)

print("\n" + "=" * 55)
print("MODEL TRAINING COMPLETE")
print("=" * 55)

print("Model saved:")
print(MODEL_FILE)

print("\nVectorizer saved:")
print(VECTORIZER_FILE)
