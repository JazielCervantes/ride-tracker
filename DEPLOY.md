# Guía de Deploy

## Resumen

| Servicio | Plataforma | URL de ejemplo |
|----------|-----------|----------------|
| Backend (FastAPI) | Railway | `https://ride-tracker-api.up.railway.app` |
| Frontend (Astro) | Vercel | `https://ride-tracker.vercel.app` |
| Base de datos | Railway (MySQL plugin) | (interna, Railway provee `DATABASE_URL`) |

---

## 1. Backend en Railway

### 1.1 Crear proyecto en Railway

1. Ir a [railway.app](https://railway.app) → **New Project**
2. Seleccionar **Deploy from GitHub repo** → autorizar y elegir `ride-tracker`
3. Railway detecta el `Procfile` automáticamente

### 1.2 Agregar MySQL

1. En el proyecto de Railway → **+ New** → **Database** → **Add MySQL**
2. Railway crea el servicio MySQL y expone la variable `DATABASE_URL` (o `MYSQL_URL`) automáticamente al servicio del backend

> **Nota:** Railway puede nombrar la variable `MYSQL_URL` en lugar de `DATABASE_URL`. Si es así, copiar el valor y crear una variable `DATABASE_URL` manualmente (ver paso 1.3).

### 1.3 Configurar variables de entorno

En Railway → servicio del backend → **Variables** → agregar:

| Variable | Valor |
|----------|-------|
| `DATABASE_URL` | Copiar la URL del MySQL plugin. Si empieza con `mysql://`, el código la convierte automáticamente a `mysql+pymysql://` |
| `SECRET_KEY` | Generar con: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_DAYS` | `7` |
| `PRODUCTION` | `true` |
| `ALLOWED_ORIGINS` | `https://ride-tracker.vercel.app` (URL de Vercel, sin `/` final) |

> `PRODUCTION=true` activa las cookies con `Secure=True` y `SameSite=none`, requerido para que el frontend en Vercel pueda enviar la cookie al backend en Railway (dominios cruzados).

### 1.4 Crear el usuario inicial (seed)

Una vez que el primer deploy esté activo:

1. En Railway → servicio del backend → **Shell** (o usar Railway CLI)
2. Ejecutar:

```bash
SEED_USERNAME=admin SEED_PASSWORD=TuPasswordSeguro python seed.py
```

O con Railway CLI:

```bash
railway run python seed.py
# El script pedirá el username (default: admin) y el password por stdin
```

### 1.5 Verificar el deploy

```bash
curl https://ride-tracker-api.up.railway.app/health
# Debe retornar: {"status":"ok","app":"Ride Tracker API","version":"1.0.0"}
```

### Archivos de deploy incluidos

- `backend/Procfile` — comando de inicio para Railway:
  ```
  web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- `backend/railway.json` — configuración de build, healthcheck en `/health`

---

## 2. Frontend en Vercel

### 2.1 Importar proyecto

1. Ir a [vercel.com](https://vercel.com) → **Add New Project**
2. Importar el repositorio `ride-tracker` desde GitHub
3. En la configuración del proyecto:
   - **Framework Preset:** Astro (Vercel lo detecta automáticamente)
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build` (se toma de `package.json`)
   - **Output Directory:** `dist` (Astro static output)

### 2.2 Variables de entorno

En Vercel → proyecto → **Settings** → **Environment Variables** → agregar:

| Variable | Valor | Entorno |
|----------|-------|---------|
| `PUBLIC_API_URL` | `https://ride-tracker-api.up.railway.app` | Production, Preview, Development |

> La variable **debe** empezar con `PUBLIC_` para que Astro la exponga en el cliente.

### 2.3 Configurar dominio (opcional)

En Vercel → **Domains** → agregar dominio personalizado si corresponde.

### 2.4 Verificar el deploy

1. Abrir la URL de Vercel (ej: `https://ride-tracker.vercel.app`)
2. Debe redirigir a `/login`
3. Ingresar con las credenciales creadas en el seed
4. Verificar que el dashboard carga sin errores CORS

---

## 3. Configuración CORS (post-deploy)

Una vez conocidas ambas URLs, actualizar en Railway la variable `ALLOWED_ORIGINS`:

```
ALLOWED_ORIGINS=https://ride-tracker.vercel.app,https://mi-dominio-personalizado.com
```

Railway reiniciará el servicio automáticamente al guardar la variable.

---

## 4. Flujo de autenticación entre dominios

El backend en Railway y el frontend en Vercel están en dominios distintos. La autenticación funciona así:

1. Login → el backend responde el token JWT en el body **y además** setea la cookie `access_token` con `Secure=True, SameSite=none, HttpOnly=True`
2. El frontend (`frontend/src/lib/api.js`) guarda el token del body en `localStorage` (`rt_token`) y lo envía como header `Authorization: Bearer` en cada request — **este es el mecanismo que se usa realmente** (no se configura `credentials: 'include'`)
3. La cookie queda como vía alternativa de autenticación que el backend también acepta (`utils/dependencies.py`), pero el frontend no depende de ella

> **Requisito:** El backend **debe** estar en HTTPS (Railway lo provee por defecto). Las cookies `SameSite=none` solo funcionan sobre HTTPS.

---

## 5. Comandos útiles

### Regenerar SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Cambiar password del usuario

Conectarse a la Railway Shell y ejecutar:

```bash
python -c "
from app.database import SessionLocal, init_db
from app.repositories.user_repository import get_by_username
from app.utils.security import get_password_hash
init_db()
db = SessionLocal()
user = get_by_username(db, 'admin')
user.password_hash = get_password_hash('NuevoPassword123!')
db.commit()
print('Password actualizado')
"
```

### Migrar la tabla `trips` en una BD existente (viajes triple + propinas)

El proyecto no usa una herramienta de migraciones: `init_db()` solo ejecuta
`create_all`, que **no** modifica tablas ya creadas. Si el servicio se desplegó
antes de agregar los viajes triple, hay que actualizar la tabla `trips` a mano
**una sola vez** en la MySQL de Railway (Railway Shell → `mysql` o cualquier cliente):

```sql
-- Agregar columnas nuevas (si aún no existen)
ALTER TABLE trips ADD COLUMN client3_name VARCHAR(100) NULL;
ALTER TABLE trips ADD COLUMN tip_amount DECIMAL(10,2) NOT NULL DEFAULT 0;

-- Cambiar trip_type de ENUM nativo a VARCHAR para aceptar 'triple'
-- (la validación de valores vive en los schemas Pydantic del backend)
ALTER TABLE trips MODIFY COLUMN trip_type VARCHAR(20) NOT NULL;
```

> En SQLite local basta con borrar `backend/ride_tracker.db` y volver a correr
> `seed.py`, o aplicar los mismos `ALTER TABLE ... ADD COLUMN` si querés conservar datos.

### Ver logs en Railway

```bash
railway logs --tail
```

### Build local del frontend (verificar antes de deploy)

```bash
cd frontend
npm run build
# Genera dist/ — lo que Vercel va a servir
```

---

## 6. Checklist de deploy

### Backend (Railway)
- [ ] Repositorio conectado a Railway
- [ ] Plugin MySQL agregado y activo
- [ ] `DATABASE_URL` apunta a la MySQL de Railway (formato `mysql+pymysql://`)
- [ ] `SECRET_KEY` generada y configurada
- [ ] `PRODUCTION=true` configurado
- [ ] `ALLOWED_ORIGINS` contiene la URL de Vercel
- [ ] Health check en `/health` responde 200
- [ ] Usuario inicial creado con `seed.py`

### Frontend (Vercel)
- [ ] Root directory configurado como `frontend`
- [ ] `PUBLIC_API_URL` apunta a la URL de Railway (sin `/` final)
- [ ] Build exitoso (`npm run build` sin errores)
- [ ] Login funciona y la cookie se setea correctamente
- [ ] Dashboard, Viajes y Semanas cargan datos reales
