# proxy-server

# 🔥 Proxy HTTP con Rotación de IPs usando Squid + Privoxy + Tor

Este proyecto es un **proxy HTTP** basado en **Squid, Privoxy y Tor**, diseñado para ofrecer **anonimato** y **rotación automática de IPs**.

🚀 **Características Principales:**

- 🔄 **Cambio automático de IPs** usando Tor (sin necesidad de scripts manuales).
- 🌍 **Accede a contenido restringido** con IPs rotativas de la red Tor.
- 🔐 **Privacidad y anonimato** para tus solicitudes HTTP.

---

## **📌 1️⃣ Flujo de las Solicitudes**

El tráfico sigue este flujo:

Cliente → Squid (3128) → Privoxy (8118) → Tor (9050) → Internet

📌 **Qué hace cada servicio:**

- **Squid (3128):** Proxy HTTP que maneja las solicitudes entrantes.
- **Privoxy (8118):** Convierte las solicitudes HTTP a SOCKS5 para Tor.
- **Tor (9050):** Red de anonimato que cambia la IP de salida.
