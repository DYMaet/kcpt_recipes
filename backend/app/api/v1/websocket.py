from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict
import json
import asyncio

from app.database import get_db
from app.models.user import User
from app.models.recipe import Recipe
from app.utils.security import decode_token
from app.api.deps import get_current_user_ws

router = APIRouter(prefix="/ws", tags=["WebSocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user: User):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user.id] = websocket

    def disconnect(self, websocket: WebSocket, user: User):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user.id in self.user_connections:
            del self.user_connections[user.id]

    async def broadcast_new_recipe(self, recipe_data: dict):
        """Broadcast new recipe to all connected clients."""
        message = json.dumps({
            "type": "new_recipe",
            "recipe": recipe_data,
        })
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


manager = ConnectionManager()


async def get_recipe_summary(recipe: Recipe, db: AsyncSession) -> dict:
    """Get recipe summary for WebSocket broadcast."""
    from app.models.ingredient import Ingredient, RecipeIngredient

    # Get author name
    author_result = await db.execute(select(User.name).where(User.id == recipe.author_id))
    author_name = author_result.scalar_one_or_none() or "Unknown"

    # Get ingredients
    ingredients_result = await db.execute(
        select(RecipeIngredient, Ingredient)
        .join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id)
        .where(RecipeIngredient.recipe_id == recipe.id)
    )
    ingredients = []
    for ri, ing in ingredients_result.all():
        ingredients.append({
            "id": ing.id,
            "name": ing.name,
            "quantity": ri.quantity,
            "unit": ri.unit,
        })

    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "calories": recipe.calories,
        "cook_time": recipe.cook_time,
        "image_url": recipe.image_url,
        "author_id": recipe.author_id,
        "author_name": author_name,
        "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
        "ingredients": ingredients,
    }


@router.websocket("/recipes")
async def websocket_recipes(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """WebSocket endpoint for real-time recipe notifications."""
    user = await get_current_user_ws(db, token)
    if not user:
        await websocket.close(code=4001, reason="Unauthenticated")
        return

    await manager.connect(websocket, user)
    try:
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": "Connected to recipe notifications",
        }))

        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                # Handle incoming messages if needed (ping/pong)
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except WebSocketDisconnect:
                break
            except Exception:
                pass
    finally:
        manager.disconnect(websocket, user)


# Function to call when new recipe is created
async def notify_new_recipe(recipe: Recipe, db: AsyncSession):
    """Call this when a new public recipe is created."""
    recipe_data = await get_recipe_summary(recipe, db)
    await manager.broadcast_new_recipe(recipe_data)