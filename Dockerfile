# Imagen base con Python
FROM python:3.9

# Instalar Tor y dependencias necesarias
RUN apt update && apt install -y tor privoxy && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos del proyecto
COPY . .

# Copiar configuración de Tor
COPY torrc /etc/tor/torrc
COPY privoxy_config /etc/privoxy/config

# Exponer el puerto del API
EXPOSE 8080 8118

# Script de inicio
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Comando de inicio
CMD ["/start.sh"]