# Servidor 2 (puerto 5327): EL GUARDIAN que verifica el sello del Genio.
# Recibe {message, signature}, verifica signature^e mod n == message.
# Si es valido Y el mensaje es el deseo prohibido -> entrega la flag.
import os
import socket
import threading
import random
import json
from cryptography.hazmat.primitives import serialization
from const import *

flag = os.environ["GEENIE_FLAG"]
pk = serialization.load_pem_public_key(os.environ["GEENIE_PUBLIC_KEY"].encode())
e = pk.public_numbers().e
n = pk.public_numbers().n


def handle(c):
    c.sendall(b"Muestrame un deseo firmado por el Genio (tal cual lo recibiste) y lo cumplire.\n\n")
    try:
        received = json.loads(c.recv(4096).decode().strip())
        message_to_int = int.from_bytes(bytes.fromhex(received.get("message", "")), byteorder='big')
        signature = received.get("signature", "")
        computed = pow(signature, e, n)
        if message_to_int == computed:
            if received.get("message") == FORBIDDEN_QUESTION.encode().hex():
                c.sendall(b"Imposible... el sello es autentico.\n\n\nLa flag es: " + flag.encode() + b"\n\n")
            else:
                c.sendall(random.choice(PREDICTIONS).encode() + b"\n\n")
        else:
            c.sendall(b"Sello invalido! Ese deseo no lo firmo el Genio.\n\n")
    except Exception as exception:
        print(exception)
        c.sendall(b"No entendi.\n")
    c.sendall(b"Adios!\n\n")
    c.close()


if __name__ == "__main__":
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", 5327))
        s.listen()

        while True:
            c, _ = s.accept()
            # Send each "client_soc" connection as a parameter to a thread.
            threading.Thread(target=handle, args=(c,), daemon=True).start()
    except KeyboardInterrupt:
        print("Closing socket...")
        s.close()
