"""
Script para crear los usuarios iniciales.

Uso:
    python seed.py
    SEED_USERNAME=admin SEED_PASSWORD=mipass python seed.py

El usuario 'admin' se crea con las variables de entorno SEED_USERNAME / SEED_PASSWORD
(o se solicita la contraseña de forma interactiva si no están definidas).

Los usuarios adicionales definidos en EXTRA_USERS se crean siempre con sus
contraseñas fijas. Úsalo solo en entornos de confianza.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, init_db
from app.models.user import User
from app.utils.security import get_password_hash

# Usuarios adicionales que se crean junto al admin.
# Formato: (username, password)
EXTRA_USERS = [
    ("salvador", "contra"),
]


def create_user(db, username: str, password: str) -> None:
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"El usuario '{username}' ya existe. Se omite.")
        return
    user = User(username=username, password_hash=get_password_hash(password))
    db.add(user)
    db.commit()
    print(f"Usuario '{username}' creado exitosamente.")


def seed():
    print("Inicializando base de datos...")
    init_db()
    db = SessionLocal()

    # --- Usuario admin (configurable por env vars) ---
    username = os.getenv("SEED_USERNAME", "admin")
    password = os.getenv("SEED_PASSWORD", "")

    if not password:
        import getpass
        password = getpass.getpass(f"Contraseña para el usuario '{username}': ")

    if not password:
        print("Error: la contraseña no puede estar vacía.")
        db.close()
        sys.exit(1)

    create_user(db, username, password)

    # --- Usuarios extra ---
    for extra_username, extra_password in EXTRA_USERS:
        create_user(db, extra_username, extra_password)

    db.close()


if __name__ == "__main__":
    seed()
