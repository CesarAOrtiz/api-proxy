const http = require("http");
const httpProxy = require("http-proxy");
const net = require("net");

const TOR_PROXY = { host: "127.0.0.1", port: 9050 }; // Puerto de Tor en Docker

const proxyServer = httpProxy.createProxyServer({});

function changeTorIP() {
  const socket = net.connect(9051, "127.0.0.1", () => {
    socket.write('AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\nQUIT\r\n');
    socket.end();
  });
  console.log("🔄 IP de Tor cambiada");
}

// Cambia la IP cada 5 minutos
setInterval(changeTorIP, 300000);

const server = http.createServer((req, res) => {
  console.log(`🔗 Redirigiendo tráfico a través de Tor`);

  proxyServer.web(
    req,
    res,
    {
      target: `socks5://${TOR_PROXY.host}:${TOR_PROXY.port}`,
      changeOrigin: true,
    },
    (err) => {
      console.error("❌ Error en el proxy", err);
      res.writeHead(500);
      res.end("Error en el proxy");
    }
  );
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
  console.log(`🚀 Proxy con Tor corriendo en http://localhost:${PORT}`);
});
