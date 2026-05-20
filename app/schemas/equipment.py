from pydantic import BaseModel
from typing import List
from app.models.enums import EquipmentCategory


class EquipmentOut(BaseModel):
    id: int
    name: str
    category: EquipmentCategory
    is_bodyweight: bool

    model_config = {"from_attributes": True}


class EquipmentCatalogGroup(BaseModel):
    category: EquipmentCategory
    items: List[EquipmentOut]


class UserEquipmentUpdate(BaseModel):
    equipment_ids: List[int]
