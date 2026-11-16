#!/usr/bin/env python3
"""
Database initialization script.
Creates tables and seeds initial data.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, AsyncSessionLocal
from app.models.user import User
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient, RecipeIngredient
from app.utils.security import hash_password
from sqlalchemy import select


async def init_database():
    """Initialize database with tables and seed data."""
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created.")

    # Seed data
    async with AsyncSessionLocal() as db:
        # Check if already seeded
        result = await db.execute(select(User).where(User.email == "user@champ2026.lan"))
        if result.scalar_one_or_none():
            print("Database already seeded, skipping...")
            return

        print("Seeding initial data...")

        # Create default user (from competition requirements)
        user = User(
            email="user@champ2026.lan",
            name="Test User",
            hashed_password=hash_password("Champ2026"),
        )
        db.add(user)

        # Create admin user
        admin = User(
            email="admin@champ2026.lan",
            name="Admin",
            hashed_password=hash_password("champ2026"),
        )
        db.add(admin)

        await db.flush()  # Get IDs

        # Create some common ingredients
        ingredients_data = [
            "Куриная грудка", "Свинина", "Говядина", "Рыба", "Креветки",
            "Рис", "Макароны", "Картофель", "Морковь", "Лук репчатый",
            "Чеснок", "Помидоры", "Огурцы", "Перец сладкий", "Капуста",
            "Яйца", "Молоко", "Сыр", "Масло растительное", "Масло сливочное",
            "Мука", "Сахар", "Соль", "Перец черный", "Зелень (петрушка, укроп)",
            "Лимон", "Соевый соус", "Сметана", "Томатная паста", "Специи",
        ]

        ingredients = []
        for name in ingredients_data:
            ing = Ingredient(name=name)
            db.add(ing)
            ingredients.append(ing)

        await db.flush()

        # Create sample recipes
        recipes_data = [
            {
                "title": "Курица с рисом и овощами",
                "description": "Простое и сытное блюдо на каждый день. Куриная грудка тушится с рисом и свежими овощами до мягкости.",
                "calories": 350,
                "cook_time": 40,
                "is_public": True,
                "ingredients": [
                    (ingredients[0], "300", "г"),  # Куриная грудка
                    (ingredients[5], "200", "г"),  # Рис
                    (ingredients[8], "1", "шт"),   # Морковь
                    (ingredients[9], "1", "шт"),   # Лук репчатый
                    (ingredients[18], "2", "ст.л."), # Масло растительное
                ],
            },
            {
                "title": "Паста карбонара",
                "description": "Классическое итальянское блюдо из спагетти с беконом, яйцами и сыром пармезан.",
                "calories": 550,
                "cook_time": 25,
                "is_public": True,
                "ingredients": [
                    (ingredients[6], "300", "г"),  # Макароны
                    (ingredients[15], "3", "шт"),  # Яйца
                    (ingredients[17], "100", "г"), # Сыр
                    (ingredients[10], "2", "зубч"), # Чеснок
                    (ingredients[19], "2", "ст.л."), # Масло сливочное
                ],
            },
            {
                "title": "Овощной салат с соевым соусом",
                "description": "Легкий и полезный салат из свежих овощей с заправкой из соевого соуса и лимонного сока.",
                "calories": 120,
                "cook_time": 15,
                "is_public": True,
                "ingredients": [
                    (ingredients[11], "2", "шт"),  # Помидоры
                    (ingredients[12], "2", "шт"),  # Огурцы
                    (ingredients[13], "1", "шт"),  # Перец сладкий
                    (ingredients[14], "200", "г"), # Капуста
                    (ingredients[23], "2", "ст.л."), # Соевый соус
                    (ingredients[22], "1", "шт"),  # Лимон
                ],
            },
            {
                "title": "Запеченная рыба с картофелем",
                "description": "Нежная рыба запекается с молодым картофелем и травами под сырной коркой.",
                "calories": 400,
                "cook_time": 50,
                "is_public": True,
                "ingredients": [
                    (ingredients[3], "400", "г"),  # Рыба
                    (ingredients[7], "500", "г"),  # Картофель
                    (ingredients[17], "50", "г"),  # Сыр
                    (ingredients[24], "по вкусу", ""), # Зелень
                    (ingredients[18], "2", "ст.л."), # Масло растительное
                ],
            },
            {
                "title": "Креветки в сливочном соусе",
                "description": "Креветки быстро готовятся в сливочном соусе с чесноком и травами. Идеально к рису или пасте.",
                "calories": 300,
                "cook_time": 20,
                "is_public": True,
                "ingredients": [
                    (ingredients[4], "300", "г"),  # Креветки
                    (ingredients[19], "2", "ст.л."), # Масло сливочное
                    (ingredients[10], "3", "зубч"), # Чеснок
                    (ingredients[23], "100", "мл"), # Сметана
                    (ingredients[24], "по вкусу", ""), # Зелень
                ],
            },
        ]

        for i, recipe_data in enumerate(recipes_data):
            recipe = Recipe(
                title=recipe_data["title"],
                description=recipe_data["description"],
                calories=recipe_data["calories"],
                cook_time=recipe_data["cook_time"],
                is_public=recipe_data["is_public"],
                author_id=user.id if i % 2 == 0 else admin.id,
            )
            db.add(recipe)
            await db.flush()

            for ing, qty, unit in recipe_data["ingredients"]:
                ri = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ing.id,
                    quantity=qty,
                    unit=unit,
                )
                db.add(ri)

        await db.commit()
        print("Seed data created successfully!")
        print(f"- 2 users (user@champ2026.lan / Champ2026, admin@champ2026.lan / champ2026)")
        print(f"- {len(ingredients_data)} ingredients")
        print(f"- {len(recipes_data)} sample recipes")


if __name__ == "__main__":
    asyncio.run(init_database())