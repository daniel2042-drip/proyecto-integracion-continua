# Proyecto Integración Continua — Escenario 3, Entrega 1

**Autores del informe:** Daniel Felipe Fuentes López y Robinson Montoya González.  
**Institución:** Politécnico Grancolombiano.  
**Módulo:** Énfasis Profesional I — Integración Continua.  
**Grupo:** B01 — Subgrupo 04.  

## Objetivo
Demostrar que dos contenedores Docker —una API Flask y una base PostgreSQL— comparten una red privada, se comunican mediante el nombre DNS `db`, guardan y recuperan registros y pueden validarse mediante GitHub Actions.

## Arquitectura

```
Usuario / pruebas HTTP
        |
        v
http://127.0.0.1:5000
        |
        v
web (Python 3.11 + Flask + Gunicorn)
        | conexión SQL a host "db":5432
        v
 db (PostgreSQL 15)
        |
        v
volumen nombrado "datos_postgres"

web y db pertenecen a la red bridge privada "red_integracion".
```

## Requisitos
- Docker Desktop o Docker Engine y Docker Compose v2.
- Python 3 (para ejecutar el script de prueba desde el equipo).
- Acceso a GitHub (solo para la automatización CI).

## Cómo iniciar el proyecto (desde la raíz)

```bash
cp .env.example .env
# Antes de arrancar, cambia POSTGRES_PASSWORD en .env por una clave propia.
docker compose config
docker compose up --build -d --wait
```

**Nota:** la clave de `.env.example` es una plantilla para trabajo local/CI. No reutilizarla en servicios reales. Nunca subir `.env` a GitHub.

## Comprobar contenedores

```bash
docker compose ps
docker ps
docker compose logs --tail 40
```

## Probar la comunicación entre contenedores

```bash
curl http://127.0.0.1:5000/health
curl -X POST http://127.0.0.1:5000/mensajes \
  -H 'Content-Type: application/json' \
  -d '{"contenido":"Prueba real entre Flask y PostgreSQL"}'
curl http://127.0.0.1:5000/mensajes
```

La segunda petición crea un registro que PostgreSQL guarda. La tercera consulta lee ese registro por la misma API. La aplicación conecta a la base mediante `DB_HOST=db`, no mediante `localhost` ni una IP fija.

O ejecuta la prueba integrada de extremo a extremo:

```bash
python3 scripts/test_integracion.py
```

## Evidencias auténticas

```bash
bash scripts/capturar_evidencias.sh
```

Este comando guarda salidas verificables de ejecución local en `evidencias/*.txt`, excluidos de Git. Agrega capturas originales de los comandos y de **GitHub > Actions** al informe una vez ejecutados. No se adjuntan capturas ficticias.

## Automatización CI
El workflow `.github/workflows/ci.yml` se inicia en un `push`/`pull_request` a `main` o `master`, o manualmente. Construye y levanta ambos servicios, espera sus estados saludables, ejecuta `test_integracion.py` y recoge logs si algo falla. La ejecución exitosa debe comprobarse en la pestaña Actions del repositorio real.

## Finalizar

```bash
docker compose down
```

Los datos siguen guardados en el volumen `datos_postgres`.

Para **eliminar también los datos de prueba**:

```bash
docker compose down -v
```

Advertencia: este último comando borra definitivamente el volumen de la base local.

## Seguridad y alcance
- Puerto Flask expuesto solo en `127.0.0.1:5000` del equipo local.
- PostgreSQL no expone `5432` al host.
- Credenciales en `.env` local, excluido por `.gitignore`.
- El volumen persiste entre reinicios y el `healthcheck` valida la disponibilidad.
- Esta es una demostración académica, no una configuración productiva.
