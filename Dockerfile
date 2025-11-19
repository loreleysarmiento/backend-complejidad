# Imagen base
FROM python:3.12-slim

# Directorio de trabajo
WORKDIR /app

# Variables para que Python no genere .pyc y haga flush de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependencias de sistema (para psycopg2 y pandas)
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Comando de arranque
# Render setea $PORT; si no existe, usamos 8000 por defecto
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
