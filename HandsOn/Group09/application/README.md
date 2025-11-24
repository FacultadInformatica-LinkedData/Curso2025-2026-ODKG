

# Guía de configuración

## 1. Configurar GraphDB Desktop

1. Crear un repositorio llamado **urban-sensors**.
2. Importar el archivo **graphdblatest.ttl.zip**.
3. En *GraphDB Workbench* ir a:
   - **Setup → Repositories**
   - Conectar el repositorio creado.

---

## 2. Preparar el entorno en VS Code

1. Abrir en VS Code la carpeta:  

`HandsOn/Group09/application`

2. Abrir la terminal integrada y ejecutar:

python -m venv .venv

3. Activar el entorno virtual:

.venv\Scripts\Activate.ps1

4. Instalar dependencias:

pip install flask requests

5. Ejecutar el proxy:

python .\graphdb-proxy\proxy.py

---

## 3. Abrir la aplicación web

Abrir el archivo pedestrian-microclimate-app.html.

Nota:
Si aparece el mensaje "Error loading from GraphDB", se recomienda:

Instalar la extensión Live Server en VS Code.

Abrir el HTML con Live Server en un puerto fijo.