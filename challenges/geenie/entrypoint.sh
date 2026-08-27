#!/bin/bash
set -e

# Las claves se generan en build time (ver Dockerfile). Los servidores las
# leen por entorno, asi que las cargamos desde los PEM de la imagen.
export GEENIE_PRIVATE_KEY="$(cat /app/keys/pk.key)"
export GEENIE_PUBLIC_KEY="$(cat /app/keys/pub.pem)"

# El Genio (5326) y el Guardian (5327) comparten el mismo par de claves, asi que
# viven en el mismo contenedor. Si cualquiera de los dos muere, el contenedor
# muere tambien y docker lo reinicia (restart: always).
python server1.py &
python server2.py &

wait -n
exit $?
