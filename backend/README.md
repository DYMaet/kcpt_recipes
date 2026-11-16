# Recipes API - Module V

Backend API for the Recipe Platform SPA (Module V) built with FastAPI, SQLite, and WebSocket support.

## Features

- **Authentication**: JWT-based auth with register/login/refresh endpoints
- **Recipes**: Public recipe browsing with filtering, sorting, and search
- **My Recipes**: Authenticated users can CRUD their own recipes
- **Constructor**: Search recipes by ingredients (drag-and-drop)
- **WebSocket**: Real-time notifications for new recipes
- **Swagger Docs**: Auto-generated at `/docs` and `/redoc`

## Tech Stack

- FastAPI 0.115
- SQLAlchemy 2.0 (async) + aiosqlite
- python-jose (JWT)
- passlib (bcrypt)
- WebSockets (native FastAPI support)

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work for local dev)
```

### 3. Initialize Database

```bash
python init_db.py
```

This creates:
- SQLite database (`recipes.db`)
- Tables for users, recipes, ingredients
- Default users:
  - `user@champ2026.lan` / `Champ2026` (regular user)
  - `admin@champ2026.lan` / `champ2026` (admin)
- Sample ingredients and recipes

### 4. Run Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Server runs at `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login, get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user |

### Public Recipes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/recipes` | List public recipes (paginated, filterable, sortable) |
| GET | `/api/v1/recipes/{id}` | Get single recipe |
| POST | `/api/v1/recipes/search-by-ingredients` | Search recipes by ingredient IDs |

### My Recipes (Auth Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/my-recipes` | List own recipes |
| POST | `/api/v1/my-recipes` | Create recipe |
| GET | `/api/v1/my-recipes/{id}` | Get own recipe |
| PUT | `/api/v1/my-recipes/{id}` | Update own recipe |
| DELETE | `/api/v1/my-recipes/{id}` | Delete own recipe |

### Ingredients
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/ingredients` | List all ingredients |
| POST | `/api/v1/ingredients` | Create ingredient (auto-dedup) |

### WebSocket
| Method | Endpoint | Description |
|--------|----------|-------------|
| WS | `/api/v1/ws/recipes?token={access_token}` | Real-time new recipe notifications |

## WebSocket Usage

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/recipes?token=YOUR_ACCESS_TOKEN');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'new_recipe') {
    console.log('New recipe:', data.recipe);
    // Update UI
  }
};

ws.onopen = () => {
  // Send ping to keep alive
  setInterval(() => ws.send(JSON.stringify({type: 'pings'})), 30000);
};
```

Message format:
```json
{
  "type": "new_recipe",
  "recipe": {
    "id": 1,
    "title": "Recipe Title",
    "description": "...",
    "calories": 350,
    "cook_time": 40,
    "image_url": null,
    "author_id": 1,
    "author_name": "User",
    "created_at": "2024-01-15T10:30:00",
    "ingredients": [...]
  }
}
```

## Recipe Filtering & Sorting

Query parameters for `GET /api/v1/recipes`:
- `page` (default: 1)
- `per_page` (default: 10, max: 50)
- `sort`: `created_at_desc` (default), `created_at_asc`, `cook_time_asc`, `cook_time_desc`, `calories_asc`, `calories_desc`
- `search`: Search in title/description

## Error Responses

All errors follow the competition format:

**401 Unauthenticated**
```json
{"message": "Unauthenticated"}
```

**403 Forbidden**
```json
{"message": "Forbidden for you"}
```

**422 Validation Error**
```json
{
  "message": "Invalid fields",
  "errors": {
    "field_name": ["error description"]
  }
}
```

## Deployment Notes

- **LAN Access**: Server binds to `0.0.0.0:8000` by default
- **Reverse Proxy**: Use Nginx/Apache for production with SSL termination
- **CORS**: Configured permissive (`*`) for competition
- **Database**: SQLite file (`recipes.db`) - copy for backup
- **Static Files**: Uploads served at `/uploads/`

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings (Pydantic BaseSettings)
│   ├── database.py          # Async SQLAlchemy setup
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/
│   │   ├── deps.py          # Dependencies (get_current_user, get_db)
│   │   └── v1/              # API v1 routes
│   ├── services/            # Business logic
│   └── utils/               # Security, exceptions
├── alembic/                 # Database migrations
├── uploads/                 # Uploaded images
├── init_db.py               # Database initialization & seeding
├── requirements.txt
├── .env.example
└── alembic.ini
```

## Default Credentials

| Role | Email | Password |
|------|-------|----------|
| User | user@champ2026.lan | Champ2026 |
| Admin | admin@champ2026.lan | champ2026 |

## License

Competition project - Module V