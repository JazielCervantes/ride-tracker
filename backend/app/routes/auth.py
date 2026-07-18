import time
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, UserOut
from app.services.auth_service import login
from app.utils.dependencies import get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# --- Rate limit de login (anti fuerza bruta, en memoria) ---
# Solo cuenta intentos FALLIDOS; un login exitoso limpia el contador.
# Suficiente para una app de un solo usuario en una sola instancia.
_MAX_FAILED_ATTEMPTS = 5
_WINDOW_SECONDS = 15 * 60
_failed_logins: dict[str, list[float]] = {}


def _client_key(request: Request) -> str:
    # Railway agrega la IP real al final de X-Forwarded-For; el primer valor
    # puede venir falsificado por el cliente, por eso se toma el último.
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


def _prune(now: float) -> None:
    expired = [k for k, ts in _failed_logins.items() if not ts or now - ts[-1] > _WINDOW_SECONDS]
    for k in expired:
        _failed_logins.pop(k, None)


def _check_rate_limit(key: str, now: float) -> None:
    attempts = [t for t in _failed_logins.get(key, []) if now - t < _WINDOW_SECONDS]
    _failed_logins[key] = attempts
    if len(attempts) >= _MAX_FAILED_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos fallidos. Esperá unos minutos y probá de nuevo.",
        )


@router.post("/login")
def login_route(data: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    now = time.time()
    _prune(now)
    key = _client_key(request)
    _check_rate_limit(key, now)

    try:
        token = login(db, data.username, data.password)
    except HTTPException as exc:
        if exc.status_code == 401:
            _failed_logins.setdefault(key, []).append(now)
        raise

    _failed_logins.pop(key, None)

    cookie_kwargs = dict(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )
    if settings.PRODUCTION:
        cookie_kwargs.update(secure=True, samesite="none")
    else:
        cookie_kwargs.update(secure=False, samesite="lax")

    response.set_cookie(**cookie_kwargs)
    return {"message": "Login exitoso", "token": token}


@router.post("/logout")
def logout_route(response: Response):
    # Los flags deben coincidir con los del set_cookie para que el
    # navegador borre la cookie también en el escenario cross-site.
    if settings.PRODUCTION:
        response.delete_cookie("access_token", path="/", secure=True, samesite="none")
    else:
        response.delete_cookie("access_token", path="/")
    return {"message": "Sesión cerrada"}


@router.get("/me", response_model=UserOut)
def me_route(current_user=Depends(get_current_user)):
    return current_user
