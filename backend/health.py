"""
Ayurveda Intelligence
Backend Health Utilities
"""

from config import (
    APP_NAME,
    APP_VERSION,
    APP_ENVIRONMENT,
    MODEL_PATH,
)


def get_backend_status():

    model_exists = MODEL_PATH.exists()

    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,

        "status": (
            "ready"
            if model_exists
            else "model_missing"
        ),

        "model": {
            "path": str(
                MODEL_PATH
            ),
            "exists": model_exists,
        },
    }


if __name__ == "__main__":

    print()
    print("=" * 60)
    print("AYURVEDA INTELLIGENCE — BACKEND STATUS")
    print("=" * 60)

    status = get_backend_status()

    print(
        f"Application : "
        f"{status['application']}"
    )

    print(
        f"Version     : "
        f"{status['version']}"
    )

    print(
        f"Environment : "
        f"{status['environment']}"
    )

    print(
        f"Status      : "
        f"{status['status']}"
    )

    print()

    print(
        f"Model exists: "
        f"{status['model']['exists']}"
    )

    print(
        f"Model path: "
        f"{status['model']['path']}"
    )

    print()
