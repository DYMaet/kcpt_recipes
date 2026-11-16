from pydantic import BaseModel, Field
from typing import Optional


class IngredientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class IngredientCreate(IngredientBase):
    pass


class IngredientResponse(IngredientBase):
    id: int

    class Config:
        from_attributes = True


class IngredientListResponse(BaseModel):
    ingredients: list[IngredientResponse]