"""
Script para crear un usuario.

Uso:
    python seed.py
    SEED_USERNAME=admin SEED_PASSWORD=mipass python seed.py

El usuario se crea con las variables de entorno SEED_USERNAME / SEED_PASSWORD
(o se solicita la contraseña de forma interactiva si no están definidas).
Ejecuta el script una vez por cada usuario que quieras crear.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, init_db
from app.models.user import User
from app.utils.security import get_password_hash


def seed():
    print("Inicializando base de datos...")
    init_db()
    db = SessionLocal()

    username = os.getenv("SEED_USERNAME", "admin")
    password = os.getenv("SEED_PASSWORD", "")

    if not password:
        import getpass
        password = getpass.getpass(f"Contraseña para el usuario '{username}': ")

    if not password:
        print("Error: la contraseña no puede estar vacía.")
        db.close()
        sys.exit(1)

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"El usuario '{username}' ya existe. No se creó ningún usuario.")
        db.close()
        return

    user = User(username=username, password_hash=get_password_hash(password))
    db.add(user)
    db.commit()
    print(f"Usuario '{username}' creado exitosamente.")
    db.close()


if __name__ == "__main__":
    seed()
