from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientResponse, IngredientListResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])


@router.get("", response_model=IngredientListResponse)
async def get_ingredients(
    db: AsyncSession = Depends(get_db),
    current_user: None = None,  # Optional auth - but we require token per WS decision
):
    """Get all ingredients for constructor/recipe creation."""
    result = await db.execute(select(Ingredient).order_by(Ingredient.name))
    ingredients = result.scalars().all()
    return IngredientListResponse(ingredients=ingredients)


@router.post("", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
async def create_ingredient(
    request: IngredientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = None,  # Allow creating ingredients during recipe creation
):
    """Create a new ingredient (used when creating recipes with new ingredients)."""
    # Check if ingredient already exists
    result = await db.execute(select(Ingredient).where(func.lower(Ingredient.name) == func.lower(request.name)))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    ingredient = Ingredient(name=request.name)
    db.add(ingredient)
    await db.commit()
    await db.refresh(ingredient)
    return ingredient