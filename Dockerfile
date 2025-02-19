# Imagen base con Python
FROM python:3.9

# Instalar Tor y dependencias necesarias
RUN apt update && apt install -y tor

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos del proyecto
COPY . .

# Copiar configuración de Tor
COPY torrc /etc/tor/torrc

# Exponer el puerto del API
EXPOSE 8080

# Iniciar Tor y FastAPI en paralelo
# CMD tor & uvicorn proxy:app --host 0.0.0.0 --port ${PORT:-8080}

# Script de inicio
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Comando de inicio
CMD ["/start.sh"]