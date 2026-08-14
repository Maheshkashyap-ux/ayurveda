"""
Ayurveda Intelligence
Backend Health Utilities

Provides simple checks for the prototype backend and its
local knowledge-base files.

This module does not perform recommendation logic.
"""


from pathlib import Path

from config import (
    APP_NAME,
    APP_VERSION,
    APP_ENVIRONMENT,
    DISEASES_FILE,
    FORMULATIONS_FILE,
    SYNONYMS_FILE,
)


# ============================================================
# FILE CHECK
# ============================================================

def check_file(path: Path):
    """
    Check whether a required knowledge-base file exists.
    """

    return {
        "file": path.name,
        "exists": path.exists(),
        "path": str(path),
    }


# ============================================================
# KNOWLEDGE BASE CHECK
# ============================================================

def check_knowledge_base():
    """
    Check the availability of all required prototype datasets.
    """

    files = [
        check_file(DISEASES_FILE),
        check_file(FORMULATIONS_FILE),
        check_file(SYNONYMS_FILE),
    ]

    available = all(
        item["exists"]
        for item in files
    )

    return {
        "status": "ready" if available else "incomplete",
        "files": files,
    }


# ============================================================
# BACKEND STATUS
# ============================================================

def get_backend_status():
    """
    Return an overall backend status summary.
    """

    knowledge_base = check_knowledge_base()

    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
        "status": (
            "ready"
            if knowledge_base["status"] == "ready"
            else "degraded"
        ),
        "knowledge_base": knowledge_base,
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    status = get_backend_status()

    print()
    print("==============================================")
    print(" Ayurveda Intelligence — Backend Status")
    print("==============================================")

    print(
        f"Application : {status['application']}"
    )

    print(
        f"Version     : {status['version']}"
    )

    print(
        f"Environment : {status['environment']}"
    )

    print(
        f"Status      : {status['status']}"
    )

    print()
    print("Knowledge Base:")

    for item in status["knowledge_base"]["files"]:

        state = (
            "OK"
            if item["exists"]
            else "MISSING"
        )

        print(
            f"  [{state}] {item['file']}"
        )

    print()
