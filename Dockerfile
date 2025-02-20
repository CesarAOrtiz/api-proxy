# Imagen base con Node.js y Tor
FROM debian:latest

# Instalar dependencias necesarias
RUN apt update && apt install -y \
    nodejs npm tor netcat curl && \
    rm -rf /var/lib/apt/lists/*

# Copiar archivos de configuración de Tor
COPY torrc /etc/tor/torrc

# Instalar dependencias de Node.js
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install

# Copiar el código del servidor proxy
COPY index.js ./

# Exponer el puerto del proxy
EXPOSE 8080

# Iniciar Tor y luego el proxy en Node.js
CMD tor & node index.js
