"""Prueba automática real (smoke test) de API y persistencia vía HTTP."""
import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

URL = "http://127.0.0.1:5000"


def call(path, method="GET", payload=None):
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        URL + path,
        method=method,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=5) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def main():
    for _ in range(30):
        try:
            status, data = call("/health")
            if status == 200 and data.get("base_datos") == "conectada":
                break
        except (URLError, HTTPError, ValueError):
            pass
        time.sleep(2)
    else:
        raise AssertionError("API/BD no se encuentran disponibles")
    print("[OK] Healthcheck HTTP + PostgreSQL")

    contenido = "Integracion verificada por prueba automatizada"
    status, created = call("/mensajes", method="POST", payload={"contenido": contenido})
    assert status == 201, f"Estado HTTP inesperado: {status}"
    assert created["contenido"] == contenido
    print(f"[OK] POST /mensajes: registro creado con id={created['id']}")

    status, listing = call("/mensajes")
    assert status == 200
    assert any(item["id"] == created["id"] and item["contenido"] == contenido
               for item in listing["mensajes"]), "No se recuperó el mensaje creado"
    print("[OK] GET /mensajes: registro recuperado desde PostgreSQL")
    print("RESULTADO: PRUEBAS DE INTEGRACION APROBADAS")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, HTTPError, URLError, ValueError, KeyError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
