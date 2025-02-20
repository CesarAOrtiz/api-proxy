# Usa Debian como base
FROM debian:latest

# Instalar NGINX, Squid, Tor y Privoxy
RUN apt update && apt install -y \
    nginx squid tor privoxy curl netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Copiar configuraciones personalizadas
COPY squid.conf /etc/squid/squid.conf
COPY privoxy.config /etc/privoxy/config
COPY torrc /etc/tor/torrc
COPY rotate_ip.sh /rotate_ip.sh

# Dar permisos de ejecución al script de rotación
RUN chmod +x /rotate_ip.sh

# Exponer el puerto de Squid
EXPOSE 3128

# Iniciar Squid, Tor, Privoxy y la rotación de IPs
CMD service tor restart && service privoxy restart && service squid restart && ./rotate_ip.sh && tail -f /dev/null
