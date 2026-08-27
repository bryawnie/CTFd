# FaceBuk — CTF de OSINT

Plataforma social ficticia para un desafío de OSINT para principiantes.

> Se filtró la tabla de usuarios de FaceBuk, una famosa red social. Entre los
> registros está la cuenta del fundador, un joven emprendedor que comparte toda
> su vida en su perfil público. En sus mensajes hay pistas de un viaje secreto
> que intentó mantener en secreto. ¿Puedes rastrear a dónde fue y descubrir lo
> que dejó publicado sin darse cuenta?

El desafío tiene dos etapas:

1. **OSINT + cracking.** Con el dump filtrado de la tabla `users` (usuarios +
   hashes sha256), los jugadores averiguan en `/about` quién fundó FaceBuk,
   buscan pistas en su perfil, deducen su contraseña y la crackean.
2. **Investigación de mensajes.** Con esa contraseña inician sesión y acceden a
   `/mensajes`. En sus conversaciones privadas encuentran pistas de un viaje
   secreto: un archivo adjunto sin cifrar con una foto del lugar, y menciones
   del ron que bebieron allá. Usando búsqueda inversa de imágenes o Google Maps,
   identifican el local, encuentran su reseña de 5 estrellas en Google Reviews,
   y recuperan la flag que dejó ahí.

La flag **no vive en la aplicación**: está en una reseña real de Google Reviews
que el organizador debe crear antes del evento.

> **Este README es para quien organiza.** Contiene la solución. No lo entregues
> a los jugadores: a ellos solo se les da la carpeta `handout/`.

## Puesta en marcha

La flag vive **fuera del repositorio**, en una reseña de Google Reviews (ver
abajo). El código no contiene secretos: se genera de forma determinista desde
`content.py` y `messages.py`.

```bash
uv sync                                          # instala dependencias
uv run seed.py                                   # genera social.db + handout/
uv run app.py                                    # sirve en 0.0.0.0:8000  (PORT=9000 uv run app.py para cambiarlo)
```

Los jugadores entran a `http://<IP-DEL-NOTEBOOK>:8000`. Para averiguar la IP en
la wifi:

```bash
ipconfig getifaddr en0
```

El puerto 5000 no sirve en macOS: lo ocupa el receptor AirPlay y responde 403.
Por eso la aplicación usa el 8000.

`seed.py` es idempotente: cada ejecución borra y reconstruye `social.db` y el
dump desde `content.py`, así que la base y los hashes nunca se desincronizan.

## Docker

La imagen está pensada para desplegarse como servicio dentro del stack de CTFd,
detrás del proxy inverso. El contenedor escucha en el **8080**, corre como el
usuario no-root `challenge` y no usa volúmenes.

```bash
docker build -t fake-social .
docker run --rm -p 8080:8080 fake-social
```

`entrypoint.sh` ejecuta `seed.py` en cada arranque si no existe `social.db`, es
decir, en cada contenedor nuevo. El sembrado va en tiempo de ejecución y no de
construcción para mantener el servicio stateless: `seed.py` es determinista
(`random.Random(1337)`) y `app.py` nunca escribe en la base. No hay secretos
que pasar al contenedor.

La imagen instala `zip` y `unzip` (Info-ZIP) con apt porque `seed.py` los invoca
como subprocesos: el módulo `zipfile` no sabe escribir archivos con contraseña.

`handout/` **no** se genera dentro del contenedor ni se sirve por la aplicación.
Lo produce quien organiza con `uv run seed.py` en local y se sube a mano a CTFd.
Su contenido es determinista: `construir_dump()` solo serializa la tabla
`users`.

## Qué se entrega a los jugadores

Solo la carpeta `handout/`:

- `facebuk_users_dump.csv` — fácil de abrir y de programar encima.
- `facebuk_users_dump.sql` — el mismo contenido con pinta de `mysqldump`.

Ambos traen `id, email, username, password_hash`. No incluyen bios, posts ni
nada del contenido de los perfiles: eso solo se obtiene navegando la plataforma.

## Estructura

| Archivo | Rol |
|---|---|
| `content.py` | Todos los usuarios, bios, posts y contraseñas en texto plano. **Acá se edita el desafío.** |
| `schema.sql` | Esquema de `social.db` (`users`, `facts`, `posts`). |
| `seed.py` | Construye la base y el dump. Valida el contenido antes de escribir. |
| `messages.py` | Mensajes privados: pistas del viaje con felipe_dev, y la contraseña del señuelo con juana_rios. |
| `assets/viaje/` | Foto del bar (se empaqueta en `viaje.zip`, sin cifrar). |
| `assets/michi/` | Fotos del gato (se empaquetan en `fotos_michi.zip`, el señuelo cifrado). |
| `app.py` | Rutas Flask: `/`, `/buscar`, `/u/<username>`, `/login`, `/mensajes`, `/descargar/<archivo>`, `/salir`. |
| `templates/`, `static/` | Interfaz. |

La base de datos nunca se expone por la red: solo se llega a ella a través del
HTML que renderiza la aplicación.

El zip se genera en `private/`, **fuera de `static/`**, y `/descargar` solo lo
entrega si hay sesión iniciada y el adjunto pertenece a un hilo de ese usuario.
Nadie puede bajarlo sin haber superado la etapa 1.

## Solución (spoilers)

1. La página **Nosotros** (`http://<ip>:8000/about`, enlazada desde el pie de
   página) dice que el fundador y CEO es **Jaime Armani, @jaimito_ar**. Ese
   username aparece en el dump. Su hash no cae con listas de contraseñas
   comunes, así que hay que investigar el perfil.

2. En `http://<ip>:8000/u/jaimito_ar` se encuentran dos datos:
   - una gata llamada **Michi**, mencionada en sus posts y en sus detalles;
   - un post fechado en 2024 donde cuenta que cumplió 21 años, junto al dato de
     que su cumpleaños es el 14 de marzo → nació en **2003**.

3. Combinando ambos se llega a `Michi2003`, cuyo sha256 coincide con el hash del
   dump.

4. Iniciar sesión en `/login` como `jaimito_ar` / `Michi2003` redirige a
   `/mensajes`. No hay flag acá, pero hay pistas.

5. En el buzón, el hilo con **felipe_dev** revela un viaje secreto a las Islas
   Caimán. Mencionan un bar de la costa oeste cuyo nombre no recuerdan bien
   ("¿El Tuki? ¿Taki?") y no paran de hablar del ron. Ahí va el adjunto
   `viaje.zip`, sin contraseña.

6. Se descarga y abre `viaje.zip`:
   ```bash
   unzip viaje.zip
   ```
   Contiene `bar-islas-caimanes.jpg`: la terraza del bar frente al mar, con
   George Town de fondo.

7. Usando **búsqueda inversa de imágenes** en Google Images o **búsqueda en
   Google Maps** ("tiki bar west side Grand Cayman"), los jugadores identifican
   el lugar: **Grand Tiki - Bar & Grill**, 93 S Church St, George Town, Islas
   Caimán. Sitio: grandtikibar.ky

8. En las reseñas de Google de ese local, buscan una de 5 estrellas de alguien
   llamado "Nico" o "Nicolás", que destaca el ron. **La última línea de esa reseña es la flag**:
   `bukctf{0v3rsh4ring_is_a_s3curity_r1sk}`

**El tema del desafío:** el fundador intentó mantener el viaje en secreto, pero
lo que publicó de más lo delata dos veces. Primero en su perfil, donde el nombre
de su gata y su fecha de nacimiento son su contraseña. Después en una reseña
pública, donde deja el rastro que lo termina de hundir.

**Nota sobre el señuelo:** El hilo con **juana_rios** contiene otro adjunto,
`fotos_michi.zip`, cifrado con contraseña `michi-la-reina` (visible en el
mismo chat). Al abrirlo, solo hay fotos del gato. Es un callejón sin salida por
diseño, para que los jugadores lean con atención cuál es el camino correcto.

Hay tres cuentas con contraseñas triviales (`123456`, `password`, `qwerty`) para
que quienes recién empiezan confirmen que su herramienta de cracking funciona.
Iniciar sesión con ellas funciona, pero no dan acceso a ninguna pista.

## Advertencias importantes

**⚠️ Requiere internet.** A diferencia de versiones anteriores, este desafío
necesita que los jugadores accedan a Google Maps y Google Reviews. Verifica
que la wifi del evento tenga acceso a internet y que sea estable.

**⚠️ La flag está fuera de tu control.** Vive en una reseña real de Google
Reviews. Google puede moderar o eliminar la reseña, y el negocio podría cerrar.
**Verifica que la reseña siga en vivo poco antes del evento y durante el mismo.**
Si desaparece, el desafío se vuelve imposible sin aviso.

## Crear / Restaurar la flag

El organizador debe crear una reseña de 5 estrellas en Google para el local
**Grand Tiki - Bar & Grill** (93 S Church St, George Town, Islas Caimán;
[grandtikibar.ky](https://grandtikibar.ky)).

- **Cuenta:** cualquiera, pero mostrar como "Nico" o "Nicolás" (para que los
  jugadores lo identifiquen con el personaje del mensaje).
- **Calificación:** 5 estrellas.
- **Texto:** exactamente este (o muy parecido):

  ```
  Fuimos con un amigo un viernes por la tarde y terminamos quedándonos hasta
  tarde. En general, los tragos muy buenos, pero el ron fue lo mejor. La
  atención fue impecable y muy atentos. Volveré sí o sí.
  bukctf{0v3rsh4ring_is_a_s3curity_r1sk}
  ```

La flag está en la última línea. Si necesitas cambiar la flag, actualiza
**ambas**: la reseña de Google y también este README (y la solución que
compartes internamente, si la tienes).

## Ajustar el desafío

Los perfiles viven en `content.py` y los mensajes privados en `messages.py`.
Las contraseñas de los adjuntos son constantes al inicio de `seed.py`
(`SENUELO_PASSWORD`, etc.) y están hardcodeadas a propósito: no son secretos,
son pasos intermedios que se encuentran explícitamente en `messages.py`.

Si cambias algo en los mensajes o en los adjuntos, `seed.py` valida eso antes
de escribir nada y falla a propósito si:

- el usuario objetivo (`jaimito_ar`) desaparece o le cambia la contraseña
  (`Michi2003`);
- hay contraseñas o usernames duplicados;
- la clave del señuelo (`michi-la-reina`) no aparece exactamente una vez en
  el buzón de Jaimito;
- no hay exactamente dos adjuntos en el buzón de Jaimito (la foto del viaje y el
  señuelo);
- algún mensaje privado filtra la contraseña de la etapa 1 (`Michi2003`);
- la foto del viaje (`viaje.zip`) no se abre sin contraseña;
- el señuelo (`fotos_michi.zip`) no se abre con su contraseña, o se abre con
  una incorrecta.

**La flag no se valida aquí:** vive fuera, en Google Reviews. No cambies
ningún nombre, ubicación, o nombre del local sin actualizar también la reseña.

Después de cualquier cambio: `uv run seed.py`.
