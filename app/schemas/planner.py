# app/schemas/planner.py
from pydantic import BaseModel
from datetime import date

class GeneratePlanRequest(BaseModel):
    planned_date: date
