import pandas as pd
import random
from pathlib import Path
from sklearn.model_selection import train_test_split

# =========================================================
# CONFIG
# =========================================================
SEED = 42
AUGMENT_FACTOR = 5   # each original training row -> up to 5 variants

random.seed(SEED)

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "raw" / "AyurGenixAI_Dataset.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "Formulation"

# These columns are removed because they leak outcome information.
LEAKAGE_COLUMNS = ["Prognosis", "Complications", "Prevention"]

# Text columns where we can make meaning-preserving variations.
TEXT_COLUMNS = [
    "Symptoms",
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
    "Occupation and Lifestyle",
    "Cultural Preferences",
    "Herbal/Alternative Remedies",
    "Ayurvedic Herbs",
    "Diet and Lifestyle Recommendations",
    "Yoga & Physical Therapy",
    "Patient Recommendations",
]

def clean_value(x):
    if pd.isna(x):
        return ""
    return str(x).strip()

def reorder_comma_list(value):
    """Reorder comma-separated items only; does not invent medical facts."""
    value = clean_value(value)
    if not value or "," not in value:
        return value

    parts = [p.strip() for p in value.split(",") if p.strip()]
    if len(parts) < 2:
        return value

    random.shuffle(parts)
    return ", ".join(parts)

def make_variant(row, variant_id):
    """Create a meaning-preserving training variant."""
    new_row = row.copy()

    # Only reorder existing comma-separated information.
    # No new disease, herb, formulation, dosage, or treatment is invented.
    cols = [c for c in TEXT_COLUMNS if c in new_row.index]

    if variant_id > 0:
        # Change a small number of existing list orderings.
        random.shuffle(cols)
        changed = 0
        for col in cols:
            if changed >= 3:
                break
            original = clean_value(new_row[col])
            updated = reorder_comma_list(original)
            if updated != original:
                new_row[col] = updated
                changed += 1

    return new_row

# =========================================================
# LOAD
# =========================================================
print("Loading dataset...")
df = pd.read_csv(INPUT_FILE)

print(f"Original dataset: {df.shape[0]} rows x {df.shape[1]} columns")

df = df.drop_duplicates().reset_index(drop=True)

# Remove leakage columns.
df = df.drop(columns=[c for c in LEAKAGE_COLUMNS if c in df.columns])

# Keep formulations with at least 2 original examples.
counts = df[TARGET].value_counts()
valid_formulations = counts[counts >= 2].index
df = df[df[TARGET].isin(valid_formulations)].reset_index(drop=True)

print(f"After filtering rare formulations: {len(df)} rows")
print(f"Formulations retained: {df[TARGET].nunique()}")

# =========================================================
# ORIGINAL HOLDOUT SPLIT
# =========================================================
# Keep the holdout rows ORIGINAL and untouched.
# Augmentation happens ONLY on the training set.
train_df, temp_df = train_test_split(
    df,
    test_size=0.20,
    random_state=SEED,
    shuffle=True
)

validation_df, test_df = train_test_split(
    temp_df,
    test_size=0.50,
    random_state=SEED,
    shuffle=True
)

# =========================================================
# AUGMENT TRAINING ONLY
# =========================================================
augmented_rows = []

for _, row in train_df.iterrows():
    for variant_id in range(AUGMENT_FACTOR):
        augmented_rows.append(make_variant(row, variant_id))

augmented_train = pd.DataFrame(augmented_rows)

# Remove exact duplicates created by rows that had no comma-separated fields.
augmented_train = augmented_train.drop_duplicates().reset_index(drop=True)

# Add a source flag so we know these are augmented training records.
# This column is removed again before model training.
augmented_train["_synthetic_training_variant"] = True

validation_out = validation_df.copy()
validation_out["_synthetic_training_variant"] = False

test_out = test_df.copy()
test_out["_synthetic_training_variant"] = False

# =========================================================
# SAVE
# =========================================================
augmented_train.to_csv(
    OUTPUT_DIR / "train_augmented.csv",
    index=False
)

validation_out.to_csv(
    OUTPUT_DIR / "validation_augmented.csv",
    index=False
)

test_out.to_csv(
    OUTPUT_DIR / "test_augmented.csv",
    index=False
)

# Also save the untouched original filtered data for auditing.
df.to_csv(
    OUTPUT_DIR / "filtered_original.csv",
    index=False
)

print("\n" + "=" * 55)
print("AUGMENTATION COMPLETE")
print("=" * 55)

print(f"Original filtered rows: {len(df)}")
print(f"Augmented training rows: {len(augmented_train)}")
print(f"Validation rows: {len(validation_out)}")
print(f"Test rows: {len(test_out)}")
print(f"Formulation classes: {df[TARGET].nunique()}")

print("\nFiles created:")
print(OUTPUT_DIR / "train_augmented.csv")
print(OUTPUT_DIR / "validation_augmented.csv")
print(OUTPUT_DIR / "test_augmented.csv")
print(OUTPUT_DIR / "filtered_original.csv")

print("\nIMPORTANT:")
print("- Only training data was augmented.")
print("- Validation/test rows remain original.")
print("- No new medical relationships, formulations, herbs, or dosages were invented.")
