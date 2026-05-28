"""
Script para cambiar la contraseña de un usuario existente.

Uso interactivo:
    python change_password.py

Con variables de entorno (útil en Railway CLI):
    TARGET_USERNAME=salvador NEW_PASSWORD=nuevapass python change_password.py
    $env:TARGET_USERNAME="salvador"; $env:NEW_PASSWORD="nuevapass"; python change_password.py  # PowerShell
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, init_db
from app.models.user import User
from app.utils.security import get_password_hash


def main():
    init_db()
    db = SessionLocal()

    username = os.getenv("TARGET_USERNAME", "")
    new_password = os.getenv("NEW_PASSWORD", "")

    if not username:
        username = input("Usuario a modificar: ").strip()
    if not username:
        print("Error: el nombre de usuario no puede estar vacío.")
        db.close()
        sys.exit(1)

    if not new_password:
        import getpass
        new_password = getpass.getpass(f"Nueva contraseña para '{username}': ")
        confirm = getpass.getpass("Confirmar nueva contraseña: ")
        if new_password != confirm:
            print("Error: las contraseñas no coinciden.")
            db.close()
            sys.exit(1)

    if not new_password:
        print("Error: la contraseña no puede estar vacía.")
        db.close()
        sys.exit(1)

    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"Error: el usuario '{username}' no existe.")
        db.close()
        sys.exit(1)

    user.password_hash = get_password_hash(new_password)
    db.commit()
    print(f"Contraseña de '{username}' actualizada correctamente.")
    db.close()


if __name__ == "__main__":
    main()
