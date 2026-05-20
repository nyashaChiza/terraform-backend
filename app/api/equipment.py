from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from collections import defaultdict

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.equipment import Equipment, UserEquipment
from app.models.enums import EquipmentCategory
from app.schemas.equipment import EquipmentOut, EquipmentCatalogGroup, UserEquipmentUpdate

router = APIRouter(tags=["Equipment"])


@router.get("/", response_model=List[EquipmentCatalogGroup])
def get_equipment_catalog(db: Session = Depends(get_db)):
    """Return the full equipment catalog grouped by category."""
    all_equipment = db.query(Equipment).order_by(Equipment.category, Equipment.name).all()

    grouped: dict[EquipmentCategory, list] = defaultdict(list)
    for item in all_equipment:
        grouped[item.category].append(item)

    return [
        EquipmentCatalogGroup(category=cat, items=items)
        for cat, items in grouped.items()
    ]


@router.get("/mine", response_model=List[EquipmentOut])
def get_my_equipment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the current user's selected equipment."""
    rows = (
        db.query(Equipment)
        .join(UserEquipment, UserEquipment.equipment_id == Equipment.id)
        .filter(UserEquipment.user_id == current_user.id)
        .all()
    )
    # Always include bodyweight equipment
    bodyweight = db.query(Equipment).filter(Equipment.is_bodyweight == True).all()
    seen = {e.id for e in rows}
    combined = rows + [e for e in bodyweight if e.id not in seen]
    return combined


@router.put("/mine", response_model=List[EquipmentOut])
def update_my_equipment(
    payload: UserEquipmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Replace the user's equipment selection entirely."""
    # Delete existing selections (excluding bodyweight — always on)
    db.query(UserEquipment).filter(UserEquipment.user_id == current_user.id).delete()

    # Re-insert new selections
    new_rows = [
        UserEquipment(user_id=current_user.id, equipment_id=eid)
        for eid in payload.equipment_ids
    ]
    db.add_all(new_rows)
    db.commit()

    # Return updated list (same as GET /mine)
    rows = (
        db.query(Equipment)
        .join(UserEquipment, UserEquipment.equipment_id == Equipment.id)
        .filter(UserEquipment.user_id == current_user.id)
        .all()
    )
    bodyweight = db.query(Equipment).filter(Equipment.is_bodyweight == True).all()
    seen = {e.id for e in rows}
    return rows + [e for e in bodyweight if e.id not in seen]
