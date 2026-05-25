from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, UserOut
from app.services.auth_service import login
from app.utils.dependencies import get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login_route(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    token = login(db, data.username, data.password)

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
    response.delete_cookie("access_token", path="/")
    return {"message": "Sesión cerrada"}


@router.get("/me", response_model=UserOut)
def me_route(current_user=Depends(get_current_user)):
    return current_user
