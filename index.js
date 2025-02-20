const http = require("http");
const httpProxy = require("http-proxy");
const { SocksProxyAgent } = require("socks-proxy-agent");
const net = require("net");

const TOR_SOCKS_PROXY = "socks5h://127.0.0.1:9050";

const proxy = httpProxy.createProxyServer({
  agent: new SocksProxyAgent(TOR_SOCKS_PROXY), // Redirige tráfico HTTP a SOCKS5
  changeOrigin: true,
});

// Función para cambiar la IP de Tor dinámicamente
function changeTorIP() {
  const socket = net.connect(9051, "127.0.0.1", () => {
    socket.write('AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\nQUIT\r\n');
    socket.end();
    console.log("🔄 IP de Tor cambiada");
  });
}

// Cambia la IP cada 5 minutos automáticamente
setInterval(changeTorIP, 300000);

// Servidor HTTP Proxy
const server = http.createServer((req, res) => {
  console.log(`🔗 Redirigiendo tráfico a través de Tor`);

  proxy.web(req, res, {}, (err) => {
    console.error("❌ Error en el proxy", err);
    res.writeHead(500);
    res.end("Error en el proxy");
  });
});

// Escuchar en el puerto 8080
const PORT = process.env.PORT;
server.listen(PORT, () => {
  console.log(`🚀 Proxy con Tor corriendo en http://localhost:${PORT}`);
});
