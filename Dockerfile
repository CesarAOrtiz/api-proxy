FROM debian:latest

RUN apt update && apt install -y \
    squid tor privoxy netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

COPY squid.conf /etc/squid/squid.conf
COPY privoxy.config /etc/privoxy/config
COPY torrc /etc/tor/torrc
COPY rotate_ip.sh /rotate_ip.sh

RUN chmod +x /rotate_ip.sh

EXPOSE 3128

CMD service tor restart && service privoxy restart && service squid restart && ./rotate_ip.sh && tail -f /dev/null
