# Social Listening Project

## Poetry Setup

### Instalación inicial
1. Instalar Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
2. Reiniciar terminal o ejecutar: `source ~/.bashrc`

### Uso diario
```bash
# Conectar el entorno virtual con Poetry
poetry env use .venv/bin/python

# Instalar dependencias
poetry install

# Activar entorno virtual
poetry shell

# Agregar dependencia de producción
poetry add <package>

# Agregar dependencia de desarrollo
poetry add --group dev <package>

# Ejecutar scripts en el entorno
poetry run python script.py

# Ver dependencias instaladas
poetry show

# Actualizar dependencias
poetry update
```

### analytics_post.py
streamlit run analytics_post.py

### Configuración de credenciales
APIs: https://console.apify.com/


