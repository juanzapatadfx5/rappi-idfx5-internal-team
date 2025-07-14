# Imagen base ligera con Python 3.11
FROM python:3.11-slim

# Evita archivos .pyc y habilita logs inmediatos
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copiamos dependencias y las instalamos
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de la app
COPY . .

# Puerto que expone DevEx por defecto (ajústalo si tu plataforma usa otro)
ENV PORT 8080
EXPOSE ${PORT}

# Comando de arranque
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
