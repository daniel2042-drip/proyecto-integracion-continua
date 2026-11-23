# Semana 5 — Entrega 2: Jenkins (continuación de la Entrega 1)

**Autores:** Daniel Felipe Fuentes López y Robinson Montoya González.  
**Proyecto base:** https://github.com/daniel2042-drip/proyecto-integracion-continua

Este paquete mantiene la aplicación Flask/PostgreSQL que funcionó en la semana 3 y añade **Jenkinsfile**,
pruebas unitarias e infraestructura Jenkins en `jenkins/`. No sustituye GitHub Actions.

## Estado de verificación
- Entrega 1: Docker, POST/GET y GitHub Actions fueron verificados en el Mac del estudiante.
- Entrega 2: **Jenkins aún no se ha ejecutado en el Mac**. Los comandos de abajo permiten hacerlo y recoger evidencias reales.
- Los archivos Python y YAML se revisaron de forma estática; no son pruebas de una ejecución Jenkins.

## Advertencia de seguridad obligatoria
El laboratorio monta `/var/run/docker.sock` en Jenkins y ejecuta el controlador como `root` para administrar
los contenedores del Docker Desktop local. **Esto concede control privilegiado sobre el motor Docker del host.**
Úsalo únicamente en tu Mac personal y con repositorios confiables; el servicio se expone solo en `127.0.0.1:8080`.
No es una configuración adecuada para producción. No ejecutes Jenkinsfiles de desconocidos.

## 1. Arrancar Jenkins desde la raíz del proyecto
```bash
docker compose -f jenkins/docker-compose.yml up -d --build
docker compose -f jenkins/docker-compose.yml ps
docker compose -f jenkins/docker-compose.yml logs --tail=40
```
La primera construcción puede descargar varios paquetes y plugins.

## 2. Abrir Jenkins
Abre `http://localhost:8080` en el Mac. Para obtener la clave de desbloqueo:
```bash
docker exec jenkins_semana5 cat /var/jenkins_home/secrets/initialAdminPassword
```
Sigue el asistente inicial, instala los plugins sugeridos y crea tu usuario personal. Nunca publiques
contraseñas ni tokens en las capturas.

## 3. Añadir el código al repositorio
Desde la raíz del proyecto, una vez que hayas inspeccionado los cambios:
```bash
git status --short
git add Jenkinsfile tests/ jenkins/ README_SEMANA_5.md
git diff --cached --stat
git commit -m 'feat: entrega 2 Jenkins pipeline y pruebas'
git push origin main
```
El proyecto subido a GitHub debe contener el `Jenkinsfile` en la raíz.

## 4. Crear el pipeline en Jenkins
- Dashboard → New Item → nombre `proyecto-integracion-continua` → Pipeline.
- En **Pipeline → Definition**, elige `Pipeline script from SCM`.
- SCM: Git → Repository URL: `https://github.com/daniel2042-drip/proyecto-integracion-continua.git`.
- Branch Specifier: `*/main`; Script Path: `Jenkinsfile`.
- Save → **Build Now**. Mira Stage View y Console Output.

## 5. Qué comprueba
1. Cinco pruebas unitarias de Flask en una imagen temporal de Python (sin red ni PostgreSQL).
2. Construcción de la imagen Docker de Flask.
3. Red y contenedores temporales para PostgreSQL + Flask; verifica `/health`, POST y GET; realiza limpieza al acabar.

Los nombres temporales llevan `${BUILD_NUMBER}` y no publican puertos. Por ello no chocan con los
contenedores `python_app_integracion` y `postgres_db_integracion` de la Entrega 1.

## 6. Capturas auténticas para el informe
1. `docker compose -f jenkins/docker-compose.yml ps` con Jenkins activo.
2. Pantalla del Jenkins Dashboard.
3. Configuración del job apuntando al repositorio (ocultar tokens).
4. Stage View con las tres etapas verdes (solo cuando suceda).
5. Console Output con `Ran 5 tests` y las pruebas POST/GET aprobadas.
6. Opcional: fallo controlado en una rama de prueba, sin editar directamente `main`.

## 7. Detener Jenkins (sin borrar historial)
```bash
docker compose -f jenkins/docker-compose.yml down
```
No ejecutar `down -v` a menos que quieras borrar definitivamente el volumen con la configuración de Jenkins.

## Problemas frecuentes
- **Puerto 8080 ocupado**: otra aplicación local usa ese puerto; libera el puerto o cambia solo el puerto del host.
- **Docker permission denied**: el socket no se montó o no es accesible; comprueba Docker Desktop.
- **No se encuentra Jenkinsfile**: confirma que `git push` publicó los cambios en `main`.
- **Fallo en pruebas**: abre `Console Output`, no supongas que el pipeline pasó.
