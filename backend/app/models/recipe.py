from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    calories = Column(Integer, nullable=False)
    cook_time = Column(Integer, nullable=False)  # in minutes
    image_url = Column(String(500), nullable=True)
    is_public = Column(Boolean, default=True, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    author = relationship("User", back_populates="recipes", lazy="selectin")
    ingredients = relationship("RecipeIngredient", back_populates="recipe", lazy="selectin", cascade="all, delete-orphan")