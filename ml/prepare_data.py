import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "raw" / "AyurGenixAI_Dataset.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

print("Loading dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Original dataset: {df.shape[0]} rows × {df.shape[1]} columns")


# ---------------------------------------------------------
# REMOVE EXACT DUPLICATES
# ---------------------------------------------------------

df = df.drop_duplicates().reset_index(drop=True)

print(f"After duplicate removal: {len(df)} rows")


# ---------------------------------------------------------
# TARGET
# ---------------------------------------------------------

TARGET = "Formulation"

if TARGET not in df.columns:
    raise ValueError(
        f"Target column '{TARGET}' was not found.\n"
        f"Available columns: {list(df.columns)}"
    )


# Remove rows where the target is missing
df = df.dropna(subset=[TARGET]).reset_index(drop=True)


# ---------------------------------------------------------
# REMOVE DATA LEAKAGE
# ---------------------------------------------------------

# These fields describe the outcome/advice rather than the
# information available when making a formulation prediction.

LEAKAGE_COLUMNS = [
    "Prognosis",
    "Complications",
    "Prevention",
    "Management",
    "Recommendations",
]


existing_leakage_columns = [
    col for col in LEAKAGE_COLUMNS
    if col in df.columns
]

if existing_leakage_columns:
    df = df.drop(columns=existing_leakage_columns)

print("\nRemoved leakage columns:")
print(existing_leakage_columns)


# ---------------------------------------------------------
# CLEAN TEXT / CATEGORICAL VALUES
# ---------------------------------------------------------

for column in df.columns:
    if df[column].dtype == "object":
        df[column] = (
            df[column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )


# ---------------------------------------------------------
# CHECK FORMULATION FREQUENCY
# ---------------------------------------------------------

formulation_counts = df[TARGET].value_counts()

print("\nFormulation statistics:")
print(f"Unique formulations: {formulation_counts.size}")
print(f"Most common formulation count: {formulation_counts.max()}")
print(f"Formulations appearing once: {(formulation_counts == 1).sum()}")
print(f"Formulations appearing twice: {(formulation_counts == 2).sum()}")


# ---------------------------------------------------------
# REMOVE EXTREMELY RARE CLASSES
# ---------------------------------------------------------

# A class needs at least 2 examples for a stratified
# train/test split.

MIN_SAMPLES = 2

valid_formulations = formulation_counts[
    formulation_counts >= MIN_SAMPLES
].index

df = df[df[TARGET].isin(valid_formulations)].reset_index(drop=True)

print(
    f"\nAfter removing formulations with < {MIN_SAMPLES} examples:"
)
print(f"Rows: {len(df)}")
print(f"Formulations: {df[TARGET].nunique()}")


# ---------------------------------------------------------
# TRAIN / VALIDATION / TEST SPLIT
# ---------------------------------------------------------

# First: 80% training, 20% temporary
train_df, temp_df = train_test_split(
    df,
    test_size=0.20,
    random_state=42,
    stratify=df[TARGET],
)


# Split the remaining 20% into:
# 10% validation
# 10% test

validation_df, test_df = train_test_split(
    temp_df,
    test_size=0.50,
    random_state=42,
    stratify=temp_df[TARGET],
)


# ---------------------------------------------------------
# SAVE DATASETS
# ---------------------------------------------------------

train_path = OUTPUT_DIR / "train.csv"
validation_path = OUTPUT_DIR / "validation.csv"
test_path = OUTPUT_DIR / "test.csv"

train_df.to_csv(train_path, index=False)
validation_df.to_csv(validation_path, index=False)
test_df.to_csv(test_path, index=False)


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

print("\n" + "=" * 50)
print("DATA PREPARATION COMPLETE")
print("=" * 50)

print(f"\nTraining set:   {train_df.shape}")
print(f"Validation set: {validation_df.shape}")
print(f"Test set:       {test_df.shape}")

print("\nFiles created:")

print(f"✓ {train_path}")
print(f"✓ {validation_path}")
print(f"✓ {test_path}")

print("\nNext step: Train the CatBoost model.")
