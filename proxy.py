from fastapi import FastAPI, Request
import httpx
import random
from stem import Signal
from stem.control import Controller
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import StreamingResponse

app = FastAPI()

# Lista de proxies: 3 instancias de Tor (SOCKS5) + Privoxy (HTTP/HTTPS)
TOR_PROXIES = [
    {"socks": "socks5h://127.0.0.1:9050", "control": 9051},
    {"socks": "socks5h://127.0.0.1:9052", "control": 9053},
    {"socks": "socks5h://127.0.0.1:9054", "control": 9055},
    {"http": "http://127.0.0.1:8118",
        "https": "http://127.0.0.1:8118", "control": None},  # Privoxy
]

# ThreadPool para manejar cambios de IP sin bloquear solicitudes
executor = ThreadPoolExecutor(max_workers=len(TOR_PROXIES))

# Cliente HTTPX asíncrono con soporte para proxies
client = httpx.AsyncClient(follow_redirects=True)

# Función para cambiar la IP en una instancia específica de Tor


def renew_tor_ip(control_port):
    if control_port:
        try:
            with Controller.from_port(port=control_port) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
        except Exception as e:
            print(f"Error al cambiar la IP en Tor ({control_port}): {e}")


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(request: Request, full_path: str):
    try:
        # Construir la URL de destino
        target_url = f"http://{full_path}" if not full_path.startswith(
            "http") else full_path

        # Seleccionar aleatoriamente una instancia de Tor o Privoxy
        proxy_instance = random.choice(TOR_PROXIES)
        proxy_url = proxy_instance.get("socks") or proxy_instance.get("http")
        control_port = proxy_instance.get("control")

        # Renovar la IP en la instancia seleccionada sin bloquear la solicitud
        if control_port:
            executor.submit(renew_tor_ip, control_port)

        # Configurar el proxy en HTTPX
        proxies = {"all://": proxy_url}

        # Copiar headers originales del cliente
        headers = dict(request.headers)
        headers["Host"] = target_url.replace(
            "https://", "").replace("http://", "").split("/")[0]

        # Capturar el body de la solicitud
        body = await request.body()

        # Hacer la solicitud al servidor de destino con HTTPX
        async with client.stream(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body if request.method in [
                "POST", "PUT", "PATCH"] else None,
            params=request.query_params,
            cookies=request.cookies,
            proxies=proxies,
            timeout=30
        ) as response:

            # Enviar la respuesta como un streaming para mejorar la carga de páginas
            return StreamingResponse(response.aiter_raw(), status_code=response.status_code, headers=dict(response.headers))

    except httpx.RequestError as e:
        return StreamingResponse(iter([f"Error al acceder a {target_url}: {str(e)}".encode()]), status_code=500)


@app.get("/")
async def root():
    return {"message": "Proxy API is running. Use /<your_url> to make requests."}
