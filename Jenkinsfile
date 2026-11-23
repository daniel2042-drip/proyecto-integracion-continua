pipeline {
    agent any
    options {
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
    }
    // Para Jenkins local: consulta GitHub cada ~15 minutos si el servicio está activo.
    triggers {
        pollSCM('H/15 * * * *')
    }
    stages {
        stage('1. Pruebas unitarias') {
            steps {
                sh '''#!/bin/sh
                    set -eu
                    docker build -t "poli-ci-tests:${BUILD_NUMBER}" -f jenkins/Dockerfile.tests .
                    docker run --rm --network none "poli-ci-tests:${BUILD_NUMBER}" \
                      python -m unittest discover -s tests -v
                '''
            }
        }
        stage('2. Construir imagen Flask') {
            steps {
                sh '''#!/bin/sh
                    set -eu
                    docker build -t "poli-ci-flask:${BUILD_NUMBER}" ./app
                '''
            }
        }
        stage('3. Integracion Flask + PostgreSQL') {
            steps {
                sh '''#!/bin/sh
                    set -eu
                    set +x  # Evita mostrar la contraseña efímera en los logs
                    NET="poli_ci_net_${BUILD_NUMBER}"
                    DB="poli_ci_db_${BUILD_NUMBER}"
                    WEB="poli_ci_web_${BUILD_NUMBER}"
                    PASS="$(openssl rand -hex 18)"
                    cleanup() {
                        docker rm -f "$WEB" "$DB" >/dev/null 2>&1 || true
                        docker network rm "$NET" >/dev/null 2>&1 || true
                    }
                    trap cleanup EXIT

                    docker network create "$NET" >/dev/null
                    docker run -d --name "$DB" --network "$NET" \
                        -e POSTGRES_DB=polidb -e POSTGRES_USER=poliuser \
                        -e POSTGRES_PASSWORD="$PASS" \
                        --health-cmd="pg_isready -U poliuser -d polidb" \
                        --health-interval=3s --health-retries=20 \
                        postgres:15-alpine >/dev/null
                    READY=0
                    for i in $(seq 1 40); do
                        STATUS="$(docker inspect --format='{{.State.Health.Status}}' "$DB")"
                        if [ "$STATUS" = healthy ]; then READY=1; break; fi
                        if [ "$STATUS" = unhealthy ]; then echo 'PostgreSQL falló healthcheck'; exit 1; fi
                        sleep 2
                    done
                    [ "$READY" -eq 1 ] || { echo 'PostgreSQL no inició'; exit 1; }

                    docker run -d --name "$WEB" --network "$NET" \
                        -e DB_HOST="$DB" -e DB_PORT=5432 \
                        -e POSTGRES_DB=polidb -e POSTGRES_USER=poliuser \
                        -e POSTGRES_PASSWORD="$PASS" \
                        "poli-ci-flask:${BUILD_NUMBER}" >/dev/null
                    echo '[CI] PostgreSQL y Flask iniciados en red temporal'
                    docker run --rm --network "$NET" \
                        -e CI_BASE_URL="http://$WEB:5000" \
                        "poli-ci-tests:${BUILD_NUMBER}" \
                        python /work/jenkins/ci_integration_test.py
                '''
            }
        }
    }
    post {
        always {
            echo 'Revisa los resultados y conserva capturas reales del build.'
        }
    }
}
