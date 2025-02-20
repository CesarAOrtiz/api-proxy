const http = require("http");
const httpProxy = require("http-proxy");
const tr = require("tor-request");

// Crear un proxy HTTP
const proxy = httpProxy.createProxyServer({});

// Configurar el servidor HTTP
const server = http.createServer((req, res) => {
  // Extraer la URL de la solicitud
  const targetUrl = req.url.slice(1); // Elimina la barra inicial (/) de la URL

  if (!targetUrl) {
    res.statusCode = 400;
    return res.end("Por favor, proporciona una URL válida.");
  }

  // Enrutar la solicitud a través de Tor
  tr.request(targetUrl, (err, torRes, body) => {
    if (err) {
      res.statusCode = 500;
      return res.end(
        `Error al realizar la solicitud a través de Tor: ${err.message}`
      );
    }

    // Enviar la respuesta al cliente
    res.statusCode = torRes.statusCode;
    res.setHeader("Content-Type", torRes.headers["content-type"]);
    res.end(body);
  });
});

// Iniciar el servidor en el puerto 3000
server.listen(3000, () => {
  console.log("Proxy server con Tor corriendo en http://localhost:3000");
});
