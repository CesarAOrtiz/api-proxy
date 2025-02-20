from fastapi import FastAPI, Request
import httpx
from stem import Signal
from stem.control import Controller
from fastapi.responses import StreamingResponse

app = FastAPI()

# Proxy de Privoxy conectado a una única instancia de Tor
PRIVOXY_PROXY = "http://127.0.0.1:8118"

# Cliente HTTPX con Privoxy como proxy
client = httpx.AsyncClient(
    proxy=PRIVOXY_PROXY,
    follow_redirects=True
)


def renew_tor_ip():
    """ Cambia la IP de Tor """
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
    except Exception as e:
        print(f"Error al cambiar la IP en Tor: {e}")


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(request: Request, full_path: str):
    """ Proxy que reenvía peticiones a través de Tor. """
    try:
        # Construir la URL de destino
        target_url = f"http://{full_path}" if not full_path.startswith(
            "http") else full_path

        # Cambiar la IP de Tor antes de cada solicitud
        renew_tor_ip()

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
            # Retornar la respuesta en streaming
            return StreamingResponse(response.aiter_raw(), status_code=response.status_code, headers=dict(response.headers))

    except httpx.RequestError as e:
        return StreamingResponse(iter([f"Error al acceder a {target_url}: {str(e)}".encode()]), status_code=500)


@app.get("/")
async def root():
    """ Mensaje de bienvenida """
    return {"message": "Proxy API running 🚀. Use /<your_url> to make requests."}
