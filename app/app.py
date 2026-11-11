"""API de ejemplo para demostrar comunicación Flask <-> PostgreSQL por DNS Docker."""
import os
import time
from datetime import datetime

import psycopg2
from psycopg2 import OperationalError
from flask import Flask, jsonify, request

app = Flask(__name__)


def connect_database(max_attempts=10, delay=2):
    """Reintenta la conexión mientras PostgreSQL termina de inicializar."""
    settings = {
        "host": os.environ.get("DB_HOST", "db"),
        "port": int(os.environ.get("DB_PORT", "5432")),
        "dbname": os.environ.get("POSTGRES_DB", "polidb"),
        "user": os.environ.get("POSTGRES_USER", "poliuser"),
        "password": os.environ.get("POSTGRES_PASSWORD", ""),
        "connect_timeout": 5,
    }
    for attempt in range(1, max_attempts + 1):
        try:
            return psycopg2.connect(**settings)
        except OperationalError:
            if attempt == max_attempts:
                raise
            time.sleep(delay)


def init_database():
    connection = connect_database()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS mensajes (
                        id SERIAL PRIMARY KEY,
                        contenido VARCHAR(255) NOT NULL,
                        fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
    finally:
        connection.close()


@app.get("/")
def home():
    return jsonify({"servicio": "API de Integración Continua", "estado": "activo"}), 200


@app.get("/health")
def health():
    """Valida también la disponibilidad de la base de datos."""
    try:
        connection = connect_database(max_attempts=1)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        finally:
            connection.close()
        return jsonify({"estado": "OK", "base_datos": "conectada"}), 200
    except (OperationalError, ValueError):
        return jsonify({"estado": "ERROR", "base_datos": "no disponible"}), 503


@app.post("/mensajes")
def create_message():
    data = request.get_json(silent=True)
    contenido = data.get("contenido") if isinstance(data, dict) else None
    if not isinstance(contenido, str) or not contenido.strip():
        return jsonify({"error": "El campo 'contenido' es obligatorio"}), 400
    if len(contenido) > 255:
        return jsonify({"error": "El contenido no puede superar 255 caracteres"}), 400
    try:
        connection = connect_database()
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO mensajes (contenido) VALUES (%s) RETURNING id, fecha",
                        (contenido.strip(),),
                    )
                    new_id, created_at = cursor.fetchone()
        finally:
            connection.close()
        return jsonify({
            "estado": "Guardado exitosamente",
            "id": new_id,
            "contenido": contenido.strip(),
            "fecha": created_at.isoformat() if isinstance(created_at, datetime) else str(created_at),
        }), 201
    except OperationalError:
        return jsonify({"error": "Base de datos no disponible"}), 503


@app.get("/mensajes")
def list_messages():
    try:
        connection = connect_database()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, contenido, fecha FROM mensajes ORDER BY id")
                rows = cursor.fetchall()
        finally:
            connection.close()
        mensajes = [{"id": r[0], "contenido": r[1], "fecha": r[2].isoformat()} for r in rows]
        return jsonify({"total": len(mensajes), "mensajes": mensajes}), 200
    except OperationalError:
        return jsonify({"error": "Base de datos no disponible"}), 503
