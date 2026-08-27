"""
Datos de seed para el CTF beginner de FaceBuk.
Base de datos de mensajes privados entre usuarios.
"""

CONVERSACIONES = {
    "jaimito_ar": [
        {
            "peer": "camila_lawyer",
            "mensajes": [
                ("in", "Jaime, ya revisé los términos de servicio que me mandaste", "2024-03-10 14:22", None),
                ("in", "Está casi todo bien, solo hay que ajustar la cláusula de datos", "2024-03-10 14:23", None),
                ("out", "Perfecto. ¿Alcanzamos a dejarlo listo esta semana?", "2024-03-10 14:24", None),
                ("in", "Sí, te mando la versión corregida el jueves", "2024-03-10 14:25", None),
                ("out", "Gracias Camila, me sacas un peso de encima", "2024-03-10 14:26", None),
                ("in", "Para eso estamos. Cualquier cosa me escribes", "2024-03-10 14:27", None),
            ],
        },
        {
            "peer": "felipe_dev",
            "mensajes": [
                ("in", "Oye, ¿al final subiste las fotos a algún lado?", "2024-03-10 14:20", None),
                ("out", "No, ni loco. Las tengo acá no más", "2024-03-10 14:21", None),
                ("out", "Te las paso mejor, por si acaso", "2024-03-10 14:22", "viaje.zip"),
                ("in", "Ya, guardadas", "2024-03-10 14:23", None),
                ("in", "Todavía no caigo que estuvimos allá", "2024-03-10 14:24", None),
                ("out", "Las Caimán son otro nivel", "2024-03-10 14:25", None),
                ("in", "Oye, ¿cómo se llamaba el barcito ese de la costa oeste?", "2024-03-10 14:26", None),
                ("out", "¿El Tuki? ¿Taki? Algo así era", "2024-03-10 14:27", None),
                ("in", "No me acuerdo, pero el ron de ese lugar no se me olvida más", "2024-03-10 14:28", None),
                ("out", "El ron. EL RON. No he tomado nada igual desde entonces", "2024-03-10 14:29", None),
                ("in", "El Nico quedó tan contento que les dejó cinco estrellas y todo", "2024-03-10 14:30", None),
                ("out", "Se lo merecían. Ojalá volver antes de fin de año", "2024-03-10 14:31", None),
                ("in", "Eso sí, ni una palabra de esto a nadie de la oficina", "2024-03-10 14:32", None),
                ("out", "Tranquilo. Esto no existió", "2024-03-10 14:33", None),
            ],
        },
        {
            "peer": "juana_rios",
            "mensajes": [
                ("in", "Manda foto de Michi, ¡la extraño!", "2024-02-28 16:12", None),
                ("out", "Jajaja está dormida en su lugar favorito", "2024-02-28 16:13", None),
                ("out", "Te mando el pack completo, pero ojo que va con clave", "2024-02-28 16:14", None),
                ("out", "La clave es michi-la-reina, obvio", "2024-02-28 16:15", None),
                ("out", "Ahí va. No lo andes mostrando por ahí jajaja", "2024-02-28 16:16", "fotos_michi.zip"),
                ("in", "¡Muero! Está tan gorda y tan digna a la vez", "2024-02-28 16:17", None),
                ("in", "¿Cómo sigue en el tema del comportamiento?", "2024-02-28 16:18", None),
                ("out", "Mucho mejor. Tu consejo funcionó", "2024-02-28 16:19", None),
                ("in", "Te lo dije. Los gatos responden bien al refuerzo positivo", "2024-02-28 16:20", None),
                ("out", "Eres la mejor psicóloga de gatos jajaja", "2024-02-28 16:21", None),
                ("in", "Jajaja, bueno, también estudié eso en la carrera", "2024-02-28 16:22", None),
            ],
        },
    ],
    "diego_photo": [
        {
            "peer": "estela_travel",
            "mensajes": [
                ("in", "Oye, vi tus fotos del sur. Están brutales", "2024-03-12 10:05", None),
                ("out", "Gracias! Fue increíble. La luz en Patagonia es otra cosa", "2024-03-12 10:06", None),
                ("in", "Ando pensando en una expedición. Me asesorías?", "2024-03-12 10:07", None),
                ("out", "Claro, cuéntame adónde quieres ir", "2024-03-12 10:08", None),
                ("in", "Torres del Paine. Es un sueño", "2024-03-12 10:09", None),
                ("out", "Uyyy, eso es hermoso. Yo también quiero ir", "2024-03-12 10:10", None),
            ],
        },
    ],
    "carlos_h": [
        {
            "peer": "mateo_gamer",
            "mensajes": [
                ("in", "Hermano, viste que sale Valorant Act nuevo?", "2024-03-09 20:30", None),
                ("out", "Sí! Estoy ansioso. Hay nuevas armas", "2024-03-09 20:31", None),
                ("in", "Vamos a rankear juntos entonces", "2024-03-09 20:32", None),
                ("in", "Necesito subir de Platino", "2024-03-09 20:33", None),
                ("out", "Dale, este fin de semana. Traes tu A-game", "2024-03-09 20:34", None),
                ("in", "Obvio. Vamos a llegar a Diamante", "2024-03-09 20:35", None),
            ],
        },
    ],
    "sofia_pastry": [
        {
            "peer": "jessica_cook",
            "mensajes": [
                ("in", "Sofía, probé tu pan de masa madre. Está fuera de serie", "2024-03-07 15:20", None),
                ("out", "¡Qué alegría! Es la receta de mi abuela", "2024-03-07 15:21", None),
                ("in", "Me encantaría saber cómo lo haces", "2024-03-07 15:22", None),
                ("out", "Claro, algún día te enseño. Es cuestión de paciencia", "2024-03-07 15:23", None),
                ("in", "Voy a intentar hacer algunos postres con tu pan", "2024-03-07 15:24", None),
                ("out", "Perfecto, avísame cómo resulta. Confío en tus habilidades", "2024-03-07 15:25", None),
                ("in", "Esta semana te mando fotos de cómo queda", "2024-03-07 15:26", None),
            ],
        },
    ],
    "pablo_music": [
        {
            "peer": "monica_dance",
            "mensajes": [
                ("in", "Pablo, necesito una canción para mi coreografía nueva", "2024-03-11 11:40", None),
                ("out", "Claro! Qué estilo buscas?", "2024-03-11 11:41", None),
                ("in", "Algo contemporáneo, melancólico", "2024-03-11 11:42", None),
                ("out", "Dale, me inspiro y te envío algo pronto", "2024-03-11 11:43", None),
                ("in", "Eres el mejor. Te espero", "2024-03-11 11:44", None),
                ("out", "Vamos a hacer algo bonito juntos", "2024-03-11 11:45", None),
            ],
        },
    ],
    "estela_travel": [
        {
            "peer": "luis_mechanic",
            "mensajes": [
                ("in", "Luis, necesito arreglar la camioneta para el viaje", "2024-03-06 09:15", None),
                ("out", "Claro, pásate por el taller cuando quieras", "2024-03-06 09:16", None),
                ("in", "Cuándo es el mejor momento para ir?", "2024-03-06 09:17", None),
                ("out", "Lunes o martes. Ahora ando más tranquilo", "2024-03-06 09:18", None),
                ("in", "Dale, paso el lunes a las 3", "2024-03-06 09:19", None),
                ("out", "Perfecto. Te espero", "2024-03-06 09:20", None),
                ("in", "Gracias por siempre estar listo", "2024-03-06 09:21", None),
            ],
        },
    ],
    "jessica_cook": [
        {
            "peer": "lupita_92",
            "mensajes": [
                ("in", "Jessica, viste que abrieron esa tienda de insumos gourmet?", "2024-03-13 17:50", None),
                ("out", "No! Adónde es?", "2024-03-13 17:51", None),
                ("in", "En Providencia, cerca de tu oficina", "2024-03-13 17:52", None),
                ("out", "Genial, voy a pasar. Ando buscando harinas especiales", "2024-03-13 17:53", None),
                ("in", "Yo también. Vamos juntas un día?", "2024-03-13 17:54", None),
                ("out", "Dale, perfecto. Te aviso cuando pueda", "2024-03-13 17:55", None),
            ],
        },
    ],
    "mariasg": [
        {
            "peer": "catalina_vet",
            "mensajes": [
                ("in", "María, necesitaba tu consejo sobre un tema legal", "2024-03-05 13:25", None),
                ("out", "Claro, cuéntame", "2024-03-05 13:26", None),
                ("in", "Es sobre un contrato de compraventa de una propiedad", "2024-03-05 13:27", None),
                ("out", "Oof, eso es complicado. Mejor conversamos en persona", "2024-03-05 13:28", None),
                ("in", "Tienes razón. Te paso mi número de office", "2024-03-05 13:29", None),
                ("out", "Dale, nos vemos esta semana", "2024-03-05 13:30", None),
            ],
        },
    ],
    "ramon_barista": [
        {
            "peer": "alejandro_book",
            "mensajes": [
                ("in", "Ramón, el café que hiciste ayer fue perfección", "2024-03-14 08:45", None),
                ("out", "Gracias! Es el Etiopía Yirgacheffe que recién llegó", "2024-03-14 08:46", None),
                ("in", "Se nota la calidad en cada sorbo", "2024-03-14 08:47", None),
                ("out", "Eso es lo que busco. Cada café es una experiencia", "2024-03-14 08:48", None),
                ("in", "Voy todos los días a disfrutar de tu obra maestra", "2024-03-14 08:49", None),
            ],
        },
    ],
}
