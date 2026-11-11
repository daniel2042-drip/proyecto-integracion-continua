#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env ]]; then
    echo "Falta el archivo .env. Copia .env.example a .env y configura tu contraseña." >&2
    exit 1
fi
mkdir -p evidencias
{
  echo "Prueba 1: docker compose build"
  docker compose build
} 2>&1 | tee evidencias/01_compilacion.txt
{
  echo "Prueba 2: docker compose up -d --wait"
  docker compose up -d --wait
} 2>&1 | tee evidencias/02_levantamiento.txt
{
  echo "Prueba 3: docker ps"
  docker ps --filter name=python_app_integracion --filter name=postgres_db_integracion
} 2>&1 | tee evidencias/03_contenedores.txt
{
  echo "Prueba 4: inspección de la red compartida"
  red=$(docker compose ps -q db | xargs docker inspect --format '{{range $name, $_ := .NetworkSettings.Networks}}{{$name}}{{end}}')
  docker network inspect "$red" --format '{{json .Containers}}'
} 2>&1 | tee evidencias/04_red.txt
{
  echo "Prueba 5: POST y GET integrados"
  python3 scripts/test_integracion.py
} 2>&1 | tee evidencias/05_comunicacion.txt
cat <<'EOF'
Evidencias REALES guardadas en evidencias/*.txt (no se versionan).
Para la captura 6, abre el repositorio en GitHub > Actions y captura la ejecución real.
EOF
