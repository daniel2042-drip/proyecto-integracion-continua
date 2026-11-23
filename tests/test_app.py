"""Pruebas unitarias sin PostgreSQL: validación de rutas y errores HTTP."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from app import app

class FlaskUnitTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_inicio_responde_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get("estado"), "activo")

    def test_post_sin_json_devuelve_400(self):
        response = self.client.post("/mensajes", data="sin-json", content_type="text/plain")
        self.assertEqual(response.status_code, 400)

    def test_post_contenido_vacio_devuelve_400(self):
        response = self.client.post("/mensajes", json={"contenido": " "})
        self.assertEqual(response.status_code, 400)

    def test_post_demasiado_largo_devuelve_400(self):
        response = self.client.post("/mensajes", json={"contenido": "a" * 256})
        self.assertEqual(response.status_code, 400)

    def test_health_si_bd_no_disponible_devuelve_503(self):
        with patch("app.connect_database", side_effect=psycopg2.OperationalError("sin BD")):
            response = self.client.get("/health")
        self.assertEqual(response.status_code, 503)

if __name__ == "__main__":
    unittest.main()
