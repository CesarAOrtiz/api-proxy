from fastapi import FastAPI, Request
import httpx
from stem import Signal
from stem.control import Controller
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import StreamingResponse

app = FastAPI()

# Proxy Privoxy que pasa por Tor
PRIVOXY_PROXY = "http://127.0.0.1:8118"

# ThreadPool para manejar cambios de IP sin bloquear solicitudes
executor = ThreadPoolExecutor(max_workers=3)

# Función para cambiar la IP en cada instancia de Tor


def renew_tor_ip(control_ports):
    for port in control_ports:
        try:
            with Controller.from_port(port=port) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
        except Exception as e:
            print(f"Error al cambiar la IP en Tor ({port}): {e}")


# Lista de puertos de control de Tor para rotación de IPs
TOR_CONTROL_PORTS = [9051, 9053, 9055]

proxy_mounts = {
    "http://": httpx.AsyncHTTPTransport(proxy=PRIVOXY_PROXY),
    "https://": httpx.AsyncHTTPTransport(proxy=PRIVOXY_PROXY),
}

# Configurar cliente HTTPX con `proxy_mounts`
client = httpx.AsyncClient(
    mounts=proxy_mounts,
    follow_redirects=True
)


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(request: Request, full_path: str):
    try:
        # Construir la URL de destino
        target_url = f"http://{full_path}" if not full_path.startswith(
            "http") else full_path

        # Rotar IPs en segundo plano sin bloquear la solicitud
        executor.submit(renew_tor_ip, TOR_CONTROL_PORTS)

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
            timeout=30
        ) as response:

            # Enviar la respuesta como un streaming para mejorar la carga de páginas
            return StreamingResponse(response.aiter_raw(), status_code=response.status_code, headers=dict(response.headers))

    except httpx.RequestError as e:
        return StreamingResponse(iter([f"Error al acceder a {target_url}: {str(e)}".encode()]), status_code=500)


@app.get("/")
async def root():
    return {"message": "Proxy API is running. Use /<your_url> to make requests."}
