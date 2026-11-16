# БЭКЭНД

Бэк для рецептов с использованием FastAPI и SQlite для worldskills.

## фичи

- **Авторизация**: JWT авторизация с эндпойнтами для логина\регистрации\рефреша
- **Рецепты**: Публичный список с фильтрацией, сортировкой и поиском
- **Свои рецепты**: CRUD для своих рецептов доступный для авторизованных пользователей
- **Конструктор**: поиск по ингредиентам
- **WebSocket**: Уведомления о новых рецептах
- **Swagger Docs**: Автоматическая документация `/docs` и `/redoc`

## Стэк

- FastAPI 0.115
- SQLAlchemy 2.0 (async) + aiosqlite
- python-jose (JWT)
- passlib (bcrypt)
- WebSockets (native FastAPI support)

## Первый запуск

### 1. Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Конфиг окружения

```bash
cp .env.example .env
```

### 3. Initialize Database

```bash
python init_db.py
```

Создаёт:
- SQLite базу (`recipes.db`)
- Таблицы юзеров, рецептов, ингредиентов.
- Дефолтных юзеров для тестов:
  - `user@champ2026.lan` / `Champ2026` (Обычный юзер)
  - `admin@champ2026.lan` / `champ2026` (админ)
- Тестовые рецепты и ингредиенты

### 4. Запуск сервера

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Сервер работает на `http://localhost:8001`
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## API эндпойнты

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

## пример использования WebSocket 

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

## Сортировка и фильтр рецептов

Параметры запроса для `GET /api/v1/recipes`:
- `page` (default: 1)
- `per_page` (default: 10, max: 50)
- `sort`: `created_at_desc` (default), `created_at_asc`, `cook_time_asc`, `cook_time_desc`, `calories_asc`, `calories_desc`
- `search`: Search in title/description

## Error Responses


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

## Заметки по разворачиванию

- **LAN Access**: Server binds to `0.0.0.0:8001` by default
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


# ФРОНТЭНД

## Стэк
- Vite
- React Router
- Axios

## Фичи

Проект создан для демонстрации работы api. На данный момент не реализован drag and drop в конструкторе. В остальном фронтэнд полностью использует функционал API.

## Запуск

```bash
cd frontend
npm install
npm run dev -- --host
```
- --host нужен для проверки работы вебсокетов. Находясь в одной сети wifi с устройством, на котором запущен фронт, можно будет подключиться с другого устройства к фронту и зайти в другую учётку, создать рецепт и другой пользователь сможет увидеть уведомление о созданном рецепте.

- Если бэк запускается на другом порту - нужно будет поменять порт в vite.config.js.
