FROM node:14

# Instalar Tor
RUN apt-get update && apt-get install -y tor

# Copiar los archivos de la aplicación
COPY . /app
WORKDIR /app

# Instalar dependencias de Node.js
RUN npm install

# Exponer el puerto
EXPOSE 3000

# Iniciar Tor y luego la aplicación
CMD tor & sleep 10 && node index.js