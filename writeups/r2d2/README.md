## R2D2
Nuestro portal es increíblemente seguro y privado, ni siquiera **Google** es capaz de encontrarlo.
Estamos tan orgullosos de él, que te permitiremos chale un vistazo: https://secure-login.bukctf.tech/

> Nota: desafío presente en carpeta challenges como `secure-login`.


## Solución
El hecho de que "ni siquiera **Google** es capaz de encontrarlo" es el mayor hint. Si Google no es capaz de encontrar el contenido significa que hay una declaración en el archivo `robots.txt` que restringe el acceso de el buscador. 

Al acceder a dicho archivo, notamos que la ruta `/s3cr3t` está explícitamente bloqueada para los bots de Goole impidiendo su indexación. Sin embargo, nosotros podemos ir a curiosear qué hay en dicha ruta.

La ruta nos indica que dentro de la carpeta `s3cr3t`, existe un archivo `users.csv` que lista los usuarios activos en la plataforma y el hash de la contraseña en `SHA-256`. 

Luego, usamos alguna página como [IO Tools](https://iotools.cloud/tool/sha256-decrypt/) para obtener el valor plano de alguna de las contraseñas e ingresar (recomiendo el segundo usuario).

> Nota 1: Si no sabías lo de `robots`, tranqui, lo importante es que ahora sí sabes.
> Nota 2: Las funciones de hash cumplen con ser unidireccionales, es decir, no existe una inversa conocida. Pudimos obtener la contraseña original por 2 razones: la contraseña usada es muy común (y su hash es conocido), y que no se usó una *sal* criptográfica para aleatorizar el resultado. Si no sabes lo que es esa *sal*, te invito a investigarlo!
