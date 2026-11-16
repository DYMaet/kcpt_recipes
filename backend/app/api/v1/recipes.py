from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from math import ceil

from app.database import get_db
from app.models.user import User
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient, RecipeIngredient
from app.schemas.recipe import (
    RecipeCreate,
    RecipeUpdate,
    RecipeResponse,
    RecipeListResponse,
    RecipeSearchRequest,
    IngredientItem,
    RecipeIngredientCreate,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/recipes", tags=["Recipes"])


def format_cook_time(minutes: int) -> str:
    """Format cook time as human readable string."""
    if minutes >= 60:
        hours = minutes // 60
        mins = minutes % 60
        if mins == 0:
            return f"{hours} час" if hours == 1 else f"{hours} часа" if hours < 5 else f"{hours} часов"
        return f"{hours} час {mins} минут" if hours == 1 else f"{hours} часа {mins} минут"
    return f"{minutes} минут"


async def build_recipe_response(recipe: Recipe, db: AsyncSession) -> RecipeResponse:
    """Build RecipeResponse with ingredients and author name."""
    # Get author name
    author_result = await db.execute(select(User.name).where(User.id == recipe.author_id))
    author_name = author_result.scalar_one_or_none() or "Unknown"

    # Get ingredients with details
    ingredients_result = await db.execute(
        select(RecipeIngredient, Ingredient)
        .join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id)
        .where(RecipeIngredient.recipe_id == recipe.id)
    )
    ingredients = []
    for ri, ing in ingredients_result.all():
        ingredients.append(IngredientItem(
            id=ing.id,
            name=ing.name,
            quantity=ri.quantity,
            unit=ri.unit,
        ))

    return RecipeResponse(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        calories=recipe.calories,
        cook_time=recipe.cook_time,
        image_url=recipe.image_url,
        is_public=recipe.is_public,
        author_id=recipe.author_id,
        author_name=author_name,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
        ingredients=ingredients,
    )


@router.get("", response_model=RecipeListResponse)
async def get_recipes(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    sort: Optional[str] = Query(None, description="created_at_desc, created_at_asc, cook_time_asc, cook_time_desc, calories_asc, calories_desc"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    db: AsyncSession = Depends(get_db),
):
    """Get public recipes with filtering and sorting."""
    # Base query - only public recipes
    query = select(Recipe).where(Recipe.is_public == True)
    count_query = select(func.count(Recipe.id)).where(Recipe.is_public == True)

    # Search filter
    if search:
        search_term = f"%{search}%"
        query = query.where(or_(
            Recipe.title.ilike(search_term),
            Recipe.description.ilike(search_term),
        ))
        count_query = count_query.where(or_(
            Recipe.title.ilike(search_term),
            Recipe.description.ilike(search_term),
        ))

    # Sorting
    if sort == "created_at_asc":
        query = query.order_by(Recipe.created_at.asc())
    elif sort == "cook_time_asc":
        query = query.order_by(Recipe.cook_time.asc())
    elif sort == "cook_time_desc":
        query = query.order_by(Recipe.cook_time.desc())
    elif sort == "calories_asc":
        query = query.order_by(Recipe.calories.asc())
    elif sort == "calories_desc":
        query = query.order_by(Recipe.calories.desc())
    else:  # default: created_at_desc
        query = query.order_by(Recipe.created_at.desc())

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    recipes = result.scalars().all()

    # Build responses
    recipe_responses = []
    for recipe in recipes:
        recipe_responses.append(await build_recipe_response(recipe, db))

    return RecipeListResponse(
        recipes=recipe_responses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=ceil(total / per_page) if total > 0 else 1,
    )


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    """Get single public recipe by ID."""
    result = await db.execute(
        select(Recipe)
        .where(Recipe.id == recipe_id, Recipe.is_public == True)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Recipe not found"},
        )

    return await build_recipe_response(recipe, db)


@router.post("/search-by-ingredients", response_model=RecipeListResponse)
async def search_by_ingredients(
    request: RecipeSearchRequest,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Find recipes that contain ALL specified ingredients."""
    # Subquery to find recipe_ids that have all the ingredients
    subquery = (
        select(RecipeIngredient.recipe_id)
        .where(RecipeIngredient.ingredient_id.in_(request.ingredient_ids))
        .group_by(RecipeIngredient.recipe_id)
        .having(func.count(RecipeIngredient.ingredient_id) == len(request.ingredient_ids))
    )

    query = select(Recipe).where(
        Recipe.id.in_(subquery),
        Recipe.is_public == True
    ).order_by(Recipe.created_at.desc())

    count_query = select(func.count(Recipe.id)).where(
        Recipe.id.in_(subquery),
        Recipe.is_public == True
    )

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    recipes = result.scalars().all()

    recipe_responses = []
    for recipe in recipes:
        recipe_responses.append(await build_recipe_response(recipe, db))

    return RecipeListResponse(
        recipes=recipe_responses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=ceil(total / per_page) if total > 0 else 1,
    )