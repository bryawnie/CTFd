# El Genio Multiplicador

El Genio concede cualquier deseo estampándolo con su **sello mágico** (una firma
RSA). Presume que "el destino ya está escrito" y que jamás sabrás la flag: por
eso se niega a firmar el deseo `quiero la flag`.

- **Puerto 5326 — el Genio.** Le envías tu deseo en hexadecimal y te devuelve un
  JSON con el deseo y su sello.
- **Puerto 5327 — el Guardián.** Le envías ese JSON, revisa el sello y, si es
  auténtico, cumple el deseo.

## Pasos para levantarlo

1. Crea el archivo `.env` a partir del ejemplo:

   ```bash
   cp .env.example .env
   ```

2. Rellena `GEENIE_FLAG` con la flag que quieras.

3. Construye y levanta:

   ```bash
   docker build -t geenie .
   docker run --rm --env-file .env -p 5326:5326 -p 5327:5327 geenie
   ```

El par de claves RSA se genera solo durante el `docker build` (ver `Dockerfile`),
así que no hay nada más que configurar. Cada build produce un par nuevo.

## Probar

```bash
echo -n "hola genio" | xxd -p | nc localhost 5326
```
