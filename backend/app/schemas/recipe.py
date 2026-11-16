from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class IngredientItem(BaseModel):
    id: int
    name: str
    quantity: Optional[str] = None
    unit: Optional[str] = None

    class Config:
        from_attributes = True


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: Optional[str] = None
    unit: Optional[str] = None


class RecipeIngredientUpdate(BaseModel):
    ingredient_id: int
    quantity: Optional[str] = None
    unit: Optional[str] = None


class RecipeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    calories: int = Field(..., ge=0)
    cook_time: int = Field(..., ge=1)  # minutes
    image_url: Optional[str] = None
    is_public: bool = True


class RecipeCreate(RecipeBase):
    ingredients: List[RecipeIngredientCreate] = Field(..., min_length=1)


class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    calories: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=1)
    image_url: Optional[str] = None
    is_public: Optional[bool] = None
    ingredients: Optional[List[RecipeIngredientCreate]] = None


class RecipeResponse(RecipeBase):
    id: int
    author_id: int
    author_name: str
    created_at: datetime
    updated_at: datetime
    ingredients: List[IngredientItem] = []

    class Config:
        from_attributes = True


class RecipeListResponse(BaseModel):
    recipes: List[RecipeResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class RecipeSearchRequest(BaseModel):
    ingredient_ids: List[int] = Field(..., min_length=1)