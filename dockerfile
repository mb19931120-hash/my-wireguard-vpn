# انسخ هذا تماماً وحفظه باسم: Dockerfile
FROM linuxserver/wireguard:latest

# إعدادات الخادم
ENV PUID=1000
ENV PGID=1000
ENV TZ=Asia/Riyadh
ENV SERVERURL=auto
ENV SERVERPORT=51820
ENV PEERS=5
ENV PEERDNS=1.1.1.1
ENV INTERNAL_SUBNET=10.13.13.0
ENV ALLOWEDIPS=0.0.0.0/0

# منافذ الخادم
EXPOSE 51820/udp
EXPOSE 51821/tcp

# مجلد التكوينات
VOLUME /config
