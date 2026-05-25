# Ride Tracker

App personal fullstack para registrar viajes en remis, con control financiero semanal.

## Características

- Registro de viajes individuales ($30) o en par ($25 c/u — $50 total)
- Semanas de **miércoles a martes**, cobro el **viernes siguiente** (semana + 9 días)
- Dashboard con resumen de la semana actual: ingresos, cantidad de viajes y próximo cobro
- CRUD completo de viajes con filtro por semana
- Historial de semanas expandible con detalle de viajes
- Autenticación por JWT en cookie HTTP-Only (usuario único, sin registro público)
- Interfaz 100% en español

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | Astro 4 + Vue 3 (output estático) |
| Estilos | Pico CSS (classless CDN) + CSS custom |
| Backend | FastAPI 0.115 + Python 3.12 |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| BD Producción | MySQL (Railway) |
| BD Desarrollo | SQLite |
| Deploy Frontend | Vercel |
| Deploy Backend | Railway |

## Estructura del proyecto

```
ride-tracker/
├── backend/
│   ├── app/
│   │   ├── config.py          # Pydantic settings, lee .env
│   │   ├── database.py        # Engine, sesión, Base, init_db()
│   │   ├── main.py            # FastAPI app, lifespan, routers
│   │   ├── models/
│   │   │   ├── user.py        # Tabla users
│   │   │   └── trip.py        # Tabla trips + enum TripType
│   │   ├── schemas/
│   │   │   ├── auth.py        # LoginRequest, UserOut
│   │   │   └── trip.py        # TripCreate, TripUpdate, TripOut, WeekSummary
│   │   ├── repositories/
│   │   │   ├── user_repository.py
│   │   │   └── trip_repository.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── trip_service.py   # Precios y lógica de semana
│   │   │   └── week_service.py   # get_week_start, get_week_end, get_payment_date
│   │   ├── routes/
│   │   │   ├── auth.py        # POST /auth/login, POST /auth/logout, GET /auth/me
│   │   │   ├── trips.py       # GET/POST /trips, PUT/DELETE /trips/{id}
│   │   │   └── weeks.py       # GET /weeks, GET /weeks/current, GET /weeks/{ws}
│   │   └── utils/
│   │       ├── security.py    # JWT create/decode, hash/verify password
│   │       └── dependencies.py # get_current_user (FastAPI dependency)
│   ├── tests/
│   │   ├── conftest.py        # Fixtures con SQLite + bcrypt 4 rounds
│   │   ├── test_auth.py       # 6 tests
│   │   ├── test_trips.py      # 10 tests
│   │   └── test_weeks.py      # 14 tests
│   ├── seed.py                # Crea el usuario inicial
│   ├── requirements.txt
│   ├── .env.example
│   ├── railway.json
│   └── Procfile
└── frontend/
    ├── src/
    │   ├── layouts/
    │   │   └── MainLayout.astro   # Header, nav, auth guard
    │   ├── pages/
    │   │   ├── index.astro        # Dashboard
    │   │   ├── login.astro        # Login
    │   │   ├── viajes.astro       # Listado de viajes
    │   │   └── semanas.astro      # Historial de semanas
    │   ├── components/
    │   │   ├── LoginForm.vue
    │   │   ├── DashboardWidget.vue
    │   │   ├── TripForm.vue       # Modal alta/edición
    │   │   ├── TripsManager.vue   # Tabla + filtros + delete
    │   │   └── WeekHistory.vue    # Semanas expandibles
    │   ├── lib/
    │   │   ├── api.js             # Fetch wrapper con credentials: include
    │   │   └── dates.js           # Helpers de fecha (semana, cobro)
    │   └── styles/
    │       └── global.css
    ├── astro.config.mjs
    ├── package.json
    ├── vercel.json
    └── .env.example
```

## Lógica de negocio

### Precios
- **Individual**: $30.00 por viaje
- **En par**: $25.00 por persona → $50.00 total por viaje

### Semanas
- Inicio de semana: **miércoles** (se calcula restando `(weekday - 2) % 7` días)
- Fin de semana: inicio + 6 días (**martes**)
- Fecha de cobro: inicio + 9 días (**viernes**)

## Desarrollo local

### Requisitos
- Python 3.12+
- Node.js 18+

### Backend

```bash
cd backend

# Crear entorno virtual e instalar dependencias
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt   # Windows
# source venv/bin/activate && pip install -r requirements.txt  # Linux/Mac

# Copiar y configurar variables de entorno
copy .env.example .env
# Editar .env con los valores locales

# Crear usuario inicial
python seed.py

# Iniciar servidor
# Windows (desde la raíz del proyecto):
& "backend\venv\Scripts\uvicorn.exe" --app-dir backend app.main:app --reload --port 8000
# Linux/Mac:
# cd backend && uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Copiar y configurar variables de entorno
copy .env.example .env
# Editar .env: PUBLIC_API_URL=http://localhost:8000

# Iniciar servidor de desarrollo
npm run dev
# Disponible en http://localhost:4321
```

### Tests

```bash
cd backend
.\venv\Scripts\python -m pytest tests/ -v
# 30 tests — auth (6), trips (10), weeks (14)
```

## Variables de entorno

### Backend (`backend/.env`)

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `DATABASE_URL` | ✅ | SQLite local o MySQL en Railway |
| `SECRET_KEY` | ✅ | Clave secreta para JWT (mínimo 32 chars) |
| `ALGORITHM` | — | Algoritmo JWT (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_DAYS` | — | Días de validez del token (default: `7`) |
| `PRODUCTION` | — | `true` en Railway para cookies `Secure` |
| `ALLOWED_ORIGINS` | — | Orígenes CORS separados por coma |

### Frontend (`frontend/.env`)

| Variable | Descripción |
|----------|-------------|
| `PUBLIC_API_URL` | URL base de la API (sin `/` final) |

## API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/auth/login` | Login, setea cookie HTTP-Only |
| `POST` | `/auth/logout` | Elimina la cookie |
| `GET` | `/auth/me` | Usuario autenticado |
| `GET` | `/trips` | Listar viajes (opcional: `?week_start=YYYY-MM-DD`) |
| `POST` | `/trips` | Crear viaje |
| `PUT` | `/trips/{id}` | Editar viaje |
| `DELETE` | `/trips/{id}` | Eliminar viaje |
| `GET` | `/weeks` | Listar semanas con actividad |
| `GET` | `/weeks/current` | Semana actual con resumen |
| `GET` | `/weeks/{week_start}` | Detalle de una semana |
| `GET` | `/health` | Health check |
