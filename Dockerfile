# Usa Debian como base
FROM debian:latest

# Instalar NGINX y Squid
RUN apt update && apt install -y \
    nginx squid && \
    rm -rf /var/lib/apt/lists/*

# Copiar configuraciones personalizadas
COPY nginx.conf /etc/nginx/nginx.conf
COPY squid.conf /etc/squid/squid.conf

# Exponer el puerto de NGINX
EXPOSE 8080

# Iniciar Squid y NGINX en segundo plano
CMD service squid restart && nginx -g "daemon off;"
