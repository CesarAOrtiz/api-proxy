from fastapi import FastAPI, Response, Query
import requests
import random
import time
from stem import Signal
from stem.control import Controller
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

# Lista de instancias de Tor con diferentes puertos
TOR_PROXIES = [
    {"socks": "socks5h://127.0.0.1:9050", "control": 9051},
    {"socks": "socks5h://127.0.0.1:9052", "control": 9053},
    {"socks": "socks5h://127.0.0.1:9054", "control": 9055},
]

# ThreadPool para manejar cambios de IP sin bloquear solicitudes
executor = ThreadPoolExecutor(max_workers=len(TOR_PROXIES))

# Función para cambiar la IP sin bloquear otras solicitudes
def renew_tor_ip(control_port):
    with Controller.from_port(port=control_port) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        time.sleep(3)  # Esperar para que la nueva IP se aplique

@app.get("/proxy")
async def proxy(url: str = Query(..., title="URL objetivo", description="La URL a la que se hará la solicitud")):
    try:
        # Seleccionar una instancia de Tor aleatoriamente
        tor_instance = random.choice(TOR_PROXIES)
        proxy_url = tor_instance["socks"]
        control_port = tor_instance["control"]

        # Renovar la IP en segundo plano
        executor.submit(renew_tor_ip, control_port)

        # Configurar el proxy SOCKS5 de Tor
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }

        # Hacer la solicitud con la nueva IP
        response = requests.get(url, proxies=proxies, timeout=10)

        # Crear una respuesta idéntica a la del servidor de origen
        return Response(content=response.content, status_code=response.status_code, headers=dict(response.headers))

    except requests.exceptions.RequestException as e:
        return Response(content=f"Error al acceder a {url}: {str(e)}", status_code=500)

@app.get("/")
async def root():
    return {"message": "Proxy API is running. Use /proxy?url=<your_url> to make requests."}
