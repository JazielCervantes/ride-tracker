from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories import user_repository
from app.utils.security import verify_password, create_access_token


def login(db: Session, username: str, password: str) -> str:
    user = user_repository.get_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = create_access_token({"user_id": user.id, "username": user.username})
    return token
