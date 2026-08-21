"""
Ayurveda Intelligence
Legacy Knowledge-Base Loader

The recommendation engine does NOT use this loader.

The production/presentation recommendation path uses:

    ml/models/final_top5_formulation_ranker.joblib

This module is retained for compatibility with older prototype
components.
"""

import csv
from pathlib import Path


PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"


def load_csv(
    file_path: Path,
):

    if not file_path.exists():

        return []

    with file_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        return list(reader)


def load_diseases():

    return load_csv(
        DATA_DIR / "diseases.csv"
    )


def load_formulations():

    return load_csv(
        DATA_DIR / "formulations.csv"
    )


def load_synonyms():

    return load_csv(
        DATA_DIR / "synonyms.csv"
    )


def load_knowledge_base():

    return {
        "diseases": load_diseases(),
        "formulations": load_formulations(),
        "synonyms": load_synonyms(),
    }


def get_dataset_summary():

    return {
        "diseases": len(
            load_diseases()
        ),

        "formulations": len(
            load_formulations()
        ),

        "synonyms": len(
            load_synonyms()
        ),
    }


if __name__ == "__main__":

    print(
        get_dataset_summary()
    )
