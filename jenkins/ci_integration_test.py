"""Prueba de extremo a extremo Jenkins -> API Flask -> PostgreSQL en la red CI."""
import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = os.environ.get("CI_BASE_URL", "http://web_ci:5000").rstrip("/")

def request(path, method="GET", payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(BASE_URL + path, data=data, method=method,
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=5) as response:
        return response.status, json.loads(response.read().decode("utf-8"))

def main():
    for attempt in range(40):
        try:
            code, body = request("/health")
            if code == 200 and body.get("base_datos") == "conectada":
                break
        except (URLError, HTTPError, ValueError):
            pass
        time.sleep(2)
    else:
        raise AssertionError("Flask y PostgreSQL no alcanzaron estado listo")
    print("[OK] /health: API conectada a PostgreSQL")

    contenido = "CI Jenkins - mensaje de prueba real"
    code, created = request("/mensajes", "POST", {"contenido": contenido})
    assert code == 201 and created["contenido"] == contenido, "POST incorrecto"
    print(f"[OK] POST /mensajes: id={created['id']}")
    code, listing = request("/mensajes")
    assert code == 200 and any(x["id"] == created["id"] and x["contenido"] == contenido
                               for x in listing["mensajes"]), "GET no recuperó el registro"
    print("[OK] GET /mensajes: registro recuperado")
    print("RESULTADO: INTEGRACION JENKINS APROBADA")

if __name__ == "__main__":
    main()
