FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends openssl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY const.py server1.py server2.py entrypoint.sh ./

# La magia del Genio se forja en cada build: par RSA con exponente publico 3
# (textbook-friendly). Nunca sale del repo, solo vive dentro de la imagen.
RUN mkdir -p /app/keys \
 && openssl genrsa -3 -out /app/keys/pk.key 2048 \
 && openssl rsa -in /app/keys/pk.key -pubout -out /app/keys/pub.pem

RUN useradd --create-home challenge \
 && chmod +x entrypoint.sh \
 && chown -R challenge:challenge /app
USER challenge

EXPOSE 5326 5327
ENTRYPOINT ["./entrypoint.sh"]
