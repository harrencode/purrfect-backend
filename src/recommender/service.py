
from sqlalchemy.orm import Session
from ..entities.user import User
from ..entities.pet import Pet
from ..recommender.model import recommend

def get_recommended_pets(db: Session, user_id: str, top_k: int = 5):
    # Fetch user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise Exception("User not found")

    # Build preference dictionary
    pref = {
        "preferred_species": user.preferred_species.value if user.preferred_species else None,
        "preferred_size": user.preferred_size.value if user.preferred_size else None,
        "temperament": user.temperament.value if user.temperament else None,
        "activity_level": user.activity_level.value if user.activity_level else None
    }

    # Fetch available pets
    # pets = db.query(Pet).filter(Pet.is_adopted == False).all()
    pets = (
    db.query(Pet)
    .filter(Pet.is_adopted == False)
    .filter(Pet.user_id != user_id)  # exclude my own pets
    .all()
)
    pets_in_db = []
    pet_map = {}  #  To retrieve full pet details later

    for p in pets:
        pet_data = {
            "PetID": str(p.pet_id),
            "Name": p.name,
            "Species": p.species.value.lower(),
            "Size": p.size.value.lower() if p.size else None,
            "Temperament": p.temperament.value.lower() if p.temperament else None,
            "ActivityLevel": p.activity_level.value.lower() if p.activity_level else None,
            "Age": p.age if p.age else 0
        }
        pets_in_db.append(pet_data)
        pet_map[str(p.pet_id)] = p  #  Map pet_id to full DB object

    # Get recommended pets
    recommended_raw = recommend(pref, pets_in_db, top_k=top_k)

    # Attach full DB pet info
    recommended_full = []
    for r in recommended_raw:
        pet = pet_map.get(r["PetID"])
        if pet:
            recommended_full.append({
                "pet_id": pet.pet_id,
                "name": pet.name,
                "species": pet.species.value,
                "breed": pet.breed,
                "age": pet.age,
                "gender": pet.gender.value if pet.gender else None,
                "color": pet.color,
                "size": pet.size.value if pet.size else None,
                "temperament": pet.temperament.value if pet.temperament else None,
                "activity_level": pet.activity_level.value if pet.activity_level else None,
                "description": pet.description,
                "images": pet.images
            })

    return recommended_full


