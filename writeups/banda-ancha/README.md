## Banda Ancha

Interceptamos un stream de datos de un grupo malicioso asociado a ciberdelincuencia. Los analistas dijeron que el payload estaba corrupto porque parecía puro ruido de caracteres sin formato ni saltos de línea. ¿Estarán en lo cierto?

[strange_content.txt](/writeups/banda-ancha/source.txt)

## Solución

El contenido del archivo se reordena a medida que cambiamos el ancho del editor de texto. Si lo ajustamos en el tamaño adecuado, los simbolos pasan a formar un QR que al ser escaneado, revela la Flag: `fukers{3s_c0s4_d3_p3r5p3ct1v4}`

> Nota: Esta es la única flag que comienza con `fukers` y no con `bukctf`.
