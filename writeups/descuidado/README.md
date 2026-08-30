## Descuidado

El historial puede contener información muy valiosa.

[AppData.zip](/writeups/descuidado/AppData.zip)

## Solución

El desafío nos entrega el contenido de la carpeta AppData de un usuario de Windows, y nos indica que potencialmente, la info que buscamos se encuentra dentro del historial del navegador. Para ello vamos directamente al archivo accediendo a `AppData/Local/Google/Chrome/User Data/Default`, donde nos encontraremos con el archivo `History`.

Podemos abrir el archivo con cualquier editor de texto y buscar algo que nos parezca relevante para encontrar la flag. Particularmente, en la línea 1402 se encuentra el siguiente contenido:

```
https://docs.google.com/spreadsheets/d/1AWa6qn-h_KyaDKEpfqTyC3p_4nNfjH6cipZ8CJNX-8E/edit?gid=0#gid=0All_flags_BukCTF - Hojas de cálculo de Google
```

Documento público que lista la flag del desafío.