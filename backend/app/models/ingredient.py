from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    recipe_ingredients = relationship("RecipeIngredient", back_populates="ingredient", lazy="selectin")


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(String(50), nullable=True)  # e.g., "200", "1.5"
    unit = Column(String(20), nullable=True)      # e.g., "г", "мл", "шт"

    # Relationships
    recipe = relationship("Recipe", back_populates="ingredients", lazy="selectin")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients", lazy="selectin")

    # Ensure unique ingredient per recipe
    __table_args__ = (UniqueConstraint("recipe_id", "ingredient_id", name="uq_recipe_ingredient"),)