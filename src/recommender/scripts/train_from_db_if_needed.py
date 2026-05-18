from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.database.core import SessionLocal
from src.entities.pet import Pet
from src.recommender.scripts.train import SCALER_OUT, train_from_dataframe


def _enum_value(value: Any) -> Any:
    return value.value if value is not None and hasattr(value, "value") else value


def _latest_artifact_time() -> datetime | None:
    artifact = Path(SCALER_OUT)
    if not artifact.exists():
        return None
    return datetime.fromtimestamp(artifact.stat().st_mtime, tz=timezone.utc)


def _available_pets_dataframe() -> tuple[pd.DataFrame, datetime | None]:
    db = SessionLocal()
    try:
        pets = db.query(Pet).filter(Pet.is_adopted == False).all()
        latest_updated_at = None

        rows = []
        for pet in pets:
            if pet.updated_at and (latest_updated_at is None or pet.updated_at > latest_updated_at):
                latest_updated_at = pet.updated_at

            rows.append(
                {
                    "pet_id": str(pet.pet_id),
                    "name": pet.name,
                    "species": _enum_value(pet.species),
                    "breed": pet.breed,
                    "age_months": pet.age or 0,
                    "gender": _enum_value(pet.gender),
                    "color": pet.color,
                    "size": _enum_value(pet.size),
                    "temperament": _enum_value(pet.temperament),
                    "activity_level": _enum_value(pet.activity_level),
                    "description": pet.description,
                    "is_adopted": pet.is_adopted,
                }
            )

        return pd.DataFrame(rows), latest_updated_at
    finally:
        db.close()


def should_retrain(latest_pet_updated_at: datetime | None) -> bool:
    latest_artifact_time = _latest_artifact_time()
    if latest_artifact_time is None:
        return True

    if latest_pet_updated_at is None:
        return False

    if latest_pet_updated_at.tzinfo is None:
        latest_pet_updated_at = latest_pet_updated_at.replace(tzinfo=timezone.utc)

    return latest_pet_updated_at > latest_artifact_time


def retrain_from_db_if_needed(force: bool = False) -> dict[str, Any]:
    df, latest_pet_updated_at = _available_pets_dataframe()

    if df.empty:
        return {
            "status": "empty_db",
            "trained": False,
            "pet_count": 0,
            "message": "No available pets found in DB. Keeping existing recommender artifacts.",
        }

    if not force and not should_retrain(latest_pet_updated_at):
        return {
            "status": "skipped",
            "trained": False,
            "pet_count": len(df),
            "message": "No new pet changes found. Skipping recommender retrain.",
        }

    train_from_dataframe(df)
    return {
        "status": "trained",
        "trained": True,
        "pet_count": len(df),
        "message": f"Recommender retrained from {len(df)} available DB pets.",
    }


def main() -> None:
    result = retrain_from_db_if_needed()
    print(result["message"])


if __name__ == "__main__":
    main()
