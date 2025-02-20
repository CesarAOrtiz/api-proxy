#!/bin/bash

while true; do
    echo -e 'AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\nQUIT\r\n' | nc 127.0.0.1 9051
    echo "🔄 IP de Tor cambiada"
    sleep 10
done
