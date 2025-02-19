#!/bin/bash
# Iniciar Tor en segundo plano
tor &

# Esperar a que Tor esté listo
sleep 10

# Iniciar FastAPI usando el puerto proporcionado por Railway
uvicorn proxy:app --host 0.0.0.0 --port ${PORT:-8080}