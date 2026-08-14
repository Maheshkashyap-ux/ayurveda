"""
Ayurveda Intelligence
Backend Data Loader

Responsible for loading the prototype Ayurveda knowledge base
from CSV files defined in config.py.

Current datasets:
    - diseases.csv
    - formulations.csv
    - synonyms.csv

The loader keeps file-handling logic separate from the
recommendation logic.
"""

import csv
from pathlib import Path

from config import (
    DISEASES_FILE,
    FORMULATIONS_FILE,
    SYNONYMS_FILE,
)


# ============================================================
# GENERIC CSV LOADER
# ============================================================

def _load_csv(file_path: Path):
    """
    Load a CSV file and return its records as a list of dictionaries.

    Each row is converted into a dictionary where the CSV column
    names become the dictionary keys.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Knowledge base file not found: {file_path}"
        )

    with file_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                f"CSV file has no header: {file_path}"
            )

        return list(reader)


# ============================================================
# DISEASE DATA
# ============================================================

def load_diseases():
    """
    Load disease / condition records.

    Returns:
        list[dict]: Disease records from diseases.csv
    """

    return _load_csv(DISEASES_FILE)


# ============================================================
# FORMULATION DATA
# ============================================================

def load_formulations():
    """
    Load formulation records.

    Returns:
        list[dict]: Formulation records from formulations.csv
    """

    return _load_csv(FORMULATIONS_FILE)


# ============================================================
# SYNONYM DATA
# ============================================================

def load_synonyms():
    """
    Load terminology / synonym mappings.

    Returns:
        list[dict]: Synonym records from synonyms.csv
    """

    return _load_csv(SYNONYMS_FILE)


# ============================================================
# COMPLETE KNOWLEDGE BASE
# ============================================================

def load_knowledge_base():
    """
    Load all prototype knowledge-base datasets.

    Returns:
        dict containing diseases, formulations and synonyms.
    """

    return {
        "diseases": load_diseases(),
        "formulations": load_formulations(),
        "synonyms": load_synonyms(),
    }


# ============================================================
# DATASET SUMMARY
# ============================================================

def get_dataset_summary():
    """
    Return basic statistics about the current knowledge base.

    This is useful for debugging and future dashboard statistics.
    """

    diseases = load_diseases()
    formulations = load_formulations()
    synonyms = load_synonyms()

    return {
        "diseases": len(diseases),
        "formulations": len(formulations),
        "synonyms": len(synonyms),
    }


# ============================================================
# SIMPLE LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print("Ayurveda Intelligence — Knowledge Base")
    print("---------------------------------------")

    summary = get_dataset_summary()

    print(f"Diseases      : {summary['diseases']}")
    print(f"Formulations  : {summary['formulations']}")
    print(f"Synonyms      : {summary['synonyms']}")
