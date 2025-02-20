# Imagen base con Python
FROM debian:latest

# Instalar Tor y dependencias necesarias
RUN apt update && apt install -y tor privoxy && rm -rf /var/lib/apt/lists/*

# Copiar configuración de Tor
COPY torrc /etc/tor/torrc
COPY privoxy_config /etc/privoxy/config

# Exponer el puerto del API
EXPOSE 8118

# Iniciar Tor y Privoxy
CMD tor & privoxy --no-daemon /etc/privoxy/config