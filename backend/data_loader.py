import csv
from config import DISEASES_FILE, FORMULATIONS_FILE, SYNONYMS_FILE


def load_csv(filename):
    """Load records from a CSV file."""
    with open(filename, "r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def load_diseases():
    return load_csv(DISEASES_FILE)


def load_formulations():
    return load_csv(FORMULATIONS_FILE)


def load_synonyms():
    return load_csv(SYNONYMS_FILE)


if __name__ == "__main__":
    diseases = load_diseases()
    formulations = load_formulations()
    synonyms = load_synonyms()

    print("Diseases:", len(diseases))
    print("Formulations:", len(formulations))
    print("Synonyms:", len(synonyms))
