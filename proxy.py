from fastapi import FastAPI, Request, Response
import httpx
from stem import Signal
from stem.control import Controller
from urllib.parse import urlparse

app = FastAPI()

PRIVOXY_PROXY = "http://127.0.0.1:8118"
TOR_SOCKS_PROXY = "socks5h://127.0.0.1:9050"

client = httpx.AsyncClient(
    proxy=TOR_SOCKS_PROXY,
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


def format_url(full_path: str) -> str:
    """ Asegura que la URL tiene el esquema (http:// o https://) """
    parsed_url = urlparse(full_path)

    if not parsed_url.scheme:
        full_path = "https://" + full_path

    return full_path


@app.get("/")
async def root():
    """ Página de bienvenida cuando el usuario accede a `/` """
    return {"message": "Proxy API running 🚀. Use /proxy/<your_url> to make requests."}


@app.api_route("/proxy/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(request: Request, full_path: str):
    """ Proxy que reenvía peticiones a través de Tor. """
    try:
        target_url = format_url(full_path)

        renew_tor_ip()

        headers = {key: value for key,
                   value in request.headers.items() if key.lower() != "host"}

        body = await request.body() if request.method in ["POST", "PUT", "PATCH"] else None

        async with client.stream(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            params=request.query_params,
            cookies=request.cookies,
            timeout=30
        ) as response:
            print(f"✅ Respuesta recibida con código {response.status_code}")

            # Preparar los headers de la respuesta eliminando los que pueden causar errores
            response_headers = {
                key: value
                for key, value in response.headers.items()
                if key.lower() not in ["content-encoding", "transfer-encoding"]
            }

            # Retornar la respuesta **exactamente como la devuelve el servidor original**
            return Response(
                # 🔥 Contenido sin modificar (JSON, HTML, imágenes, archivos, etc.)
                content=await response.aread(),
                status_code=response.status_code,
                headers=response_headers
            )

    except httpx.RequestError as e:
        print(f"❌ Error en la solicitud a {target_url}: {e}")
        return Response(content=f"Error al acceder a {target_url}: {str(e)}",
                        status_code=500,
                        media_type="text/plain")
