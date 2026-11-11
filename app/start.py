"""Inicializa la tabla y arranca Gunicorn."""
import os
from app import init_database

if __name__ == "__main__":
    init_database()
    os.execvp("gunicorn", [
        "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"
    ])
