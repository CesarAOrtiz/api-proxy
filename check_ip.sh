#!/bin/bash

echo "🔍 Iniciando validación de IPs de Tor..."
while true; do
    IP=$(curl --socks5-hostname 127.0.0.1:9050 -s https://check.torproject.org/api/ip)
    echo "🌐 Nueva IP de Tor: $IP"
    sleep 10
done
