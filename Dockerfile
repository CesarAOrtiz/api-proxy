# Usa Debian como base
FROM debian:latest

# Instalar Squid, Tor, Privoxy, netcat y jq para JSON
RUN apt update && apt install -y \
    squid tor privoxy netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Copiar configuraciones personalizadas
COPY squid.conf /etc/squid/squid.conf
COPY privoxy.config /etc/privoxy/config
COPY torrc /etc/tor/torrc

# Exponer el puerto del proxy Squid
EXPOSE 3128

# Iniciar Tor, Privoxy y Squid, luego mantener el contenedor en ejecución
CMD service tor restart && \
    while ! nc -z 127.0.0.1 9050; do echo "⏳ Esperando Tor..."; sleep 2; done && \
    service privoxy restart && \
    service squid restart && \
    squid -N




