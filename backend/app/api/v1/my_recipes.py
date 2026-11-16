from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List
from math import ceil
from app.api.v1.websocket import notify_new_recipe
from app.database import get_db
from app.models.user import User
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient, RecipeIngredient
from app.schemas.recipe import (
    RecipeCreate,
    RecipeUpdate,
    RecipeResponse,
    RecipeListResponse,
    RecipeIngredientCreate,
    IngredientItem,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/my-recipes", tags=["My Recipes"])


async def build_recipe_response(recipe: Recipe, db: AsyncSession) -> RecipeResponse:
    """Build RecipeResponse with ingredients and author name."""
    author_result = await db.execute(select(User.name).where(User.id == recipe.author_id))
    author_name = author_result.scalar_one_or_none() or "Unknown"

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
async def get_my_recipes(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's recipes (including private)."""
    query = select(Recipe).where(Recipe.author_id == current_user.id).order_by(Recipe.created_at.desc())
    count_query = select(func.count(Recipe.id)).where(Recipe.author_id == current_user.id)

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


@router.post("", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    request: RecipeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new recipe."""
    # Validate ingredients exist
    for ing_req in request.ingredients:
        result = await db.execute(select(Ingredient).where(Ingredient.id == ing_req.ingredient_id))
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": "Invalid fields", "errors": {"ingredients": [f"Ingredient with id {ing_req.ingredient_id} not found"]}},
            )

    # Create recipe
    recipe = Recipe(
        title=request.title,
        description=request.description,
        calories=request.calories,
        cook_time=request.cook_time,
        image_url=request.image_url,
        is_public=request.is_public,
        author_id=current_user.id,
    )
    db.add(recipe)
    await db.flush()  # Get recipe.id

    # Add ingredients
    for ing_req in request.ingredients:
        ri = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ing_req.ingredient_id,
            quantity=ing_req.quantity,
            unit=ing_req.unit,
        )
        db.add(ri)

    await db.commit()
    await db.refresh(recipe)
    if recipe.is_public:
        await notify_new_recipe(recipe, db)

    return await build_recipe_response(recipe, db)


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_my_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's own recipe by ID."""
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.author_id == current_user.id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Recipe not found"},
        )

    return await build_recipe_response(recipe, db)


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: int,
    request: RecipeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user's own recipe."""
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.author_id == current_user.id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Recipe not found"},
        )

    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    ingredients_data = update_data.pop("ingredients", None)

    for field, value in update_data.items():
        setattr(recipe, field, value)

    # Update ingredients if provided
    if ingredients_data is not None:
        # Validate ingredients exist
        for ing_req in ingredients_data:
            result = await db.execute(select(Ingredient).where(Ingredient.id == ing_req.ingredient_id))
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"message": "Invalid fields", "errors": {"ingredients": [f"Ingredient with id {ing_req.ingredient_id} not found"]}},
                )

        # Delete existing ingredients
        await db.execute(select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe.id).delete())

        # Add new ingredients
        for ing_req in ingredients_data:
            ri = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ing_req.ingredient_id,
                quantity=ing_req.quantity,
                unit=ing_req.unit,
            )
            db.add(ri)

    await db.commit()
    await db.refresh(recipe)

    return await build_recipe_response(recipe, db)


@router.delete("/{recipe_id}", status_code=status.HTTP_200_OK)
async def delete_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete user's own recipe."""
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.author_id == current_user.id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Recipe not found"},
        )

    await db.delete(recipe)
    await db.commit()

    return {"message": "Recipe deleted successfully"}