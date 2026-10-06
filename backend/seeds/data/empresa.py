"""Datos base de la empresa ficticia TransDemo S.R.L.: empresa, ciudades, oficinas, servicios, FAQs y páginas.

Todo es inventado para la demostración: teléfonos (rango 591 70000xxx), direcciones, NIT y textos.
"""

URL_COMPRA = "https://www.transdemo.com/pasajes"
URL_RASTREO = "https://www.transdemo.com/rastreo"

TELEFONO_CENTRAL = "59170000100"
WHATSAPP_CENTRAL = "59170000101"
WHATSAPP_PUERTA_SUCRE = "59170000111"
WHATSAPP_PUERTA_SANTA_CRUZ = "59170000112"

EMPRESA = {
    "id": 1,
    "razon_social": "TransDemo S.R.L.",
    "nombre_comercial": "TransDemo",
    "nit": "1000000019",  # demo
    "ente_regulador": "Autoridad de Telecomunicaciones y Transportes (ATT)",
    "sitio_web": "https://www.transdemo.com",
    "url_compra_pasajes": URL_COMPRA,
    "url_rastreo_carga": URL_RASTREO,
    "facebook_url": None,
    "email_contacto": "contacto@transdemo.com",
    "telefono_central_e164": TELEFONO_CENTRAL,
    "telefono_atencion_cliente_e164": TELEFONO_CENTRAL,
    "whatsapp_central_e164": WHATSAPP_CENTRAL,
    "color_marca": "#B3122E",
    "eslogan": "Viaja y envía por Bolivia: pasajes en línea y encomiendas con seguimiento.",
    "descripcion": (
        "Empresa ficticia de demostración. Simula una operadora boliviana de transporte interdepartamental "
        "de pasajeros en buses de dos pisos (Suite Cama arriba y Leito Cama abajo) y de envío de carga y "
        "encomiendas con seguimiento en línea."
    ),
    "terminos_condiciones": (
        "Texto de demostración. El pasaje es personal e intransferible y debe coincidir con el documento "
        "de identidad del pasajero. Las fechas y horas de partida están sujetas a cambios. Los reembolsos "
        "se rigen por la política publicada en el Centro de Ayuda."
    ),
    "moneda": "BOB",
    "zona_horaria": "America/La_Paz",
}

CIUDADES = [
    {
        "codigo": "SRE",
        "nombre": "Sucre",
        "departamento": "Chuquisaca",
        "es_destino_pasajeros": True,
        "es_destino_carga": True,
        "tiene_puerta_a_puerta": True,
        "whatsapp_puerta_a_puerta_e164": WHATSAPP_PUERTA_SUCRE,
        "alias_busqueda": ["sucre", "sre", "chuquisaca", "ciudad blanca", "capital"],
    },
    {
        "codigo": "CMG",
        "nombre": "Camargo",
        "departamento": "Chuquisaca",
        "es_destino_pasajeros": False,
        "es_destino_carga": True,
        "tiene_puerta_a_puerta": False,
        "whatsapp_puerta_a_puerta_e164": None,
        "alias_busqueda": ["camargo", "cmg"],
    },
    {
        "codigo": "SCZ",
        "nombre": "Santa Cruz",
        "departamento": "Santa Cruz",
        "es_destino_pasajeros": True,
        "es_destino_carga": True,
        "tiene_puerta_a_puerta": True,
        "whatsapp_puerta_a_puerta_e164": WHATSAPP_PUERTA_SANTA_CRUZ,
        "alias_busqueda": ["santa cruz de la sierra", "scz", "santa", "santacruz"],
    },
    {
        "codigo": "TJA",
        "nombre": "Tarija",
        "departamento": "Tarija",
        "es_destino_pasajeros": True,
        "es_destino_carga": True,
        "tiene_puerta_a_puerta": False,
        "whatsapp_puerta_a_puerta_e164": None,
        "alias_busqueda": ["tarija", "tja"],
    },
    {
        "codigo": "PTS",
        "nombre": "Potosí",
        "departamento": "Potosí",
        "es_destino_pasajeros": False,
        "es_destino_carga": True,
        "tiene_puerta_a_puerta": False,
        "whatsapp_puerta_a_puerta_e164": None,
        "alias_busqueda": ["potosi", "pts", "villa imperial"],
    },
    {
        "codigo": "LPZ",
        "nombre": "La Paz",
        "departamento": "La Paz",
        "es_destino_pasajeros": True,
        "es_destino_carga": True,
        "tiene_puerta_a_puerta": False,
        "whatsapp_puerta_a_puerta_e164": None,
        "alias_busqueda": ["la paz", "lpz", "lapaz"],
    },
    {
        "codigo": "EAT",
        "nombre": "El Alto",
        "departamento": "La Paz",
        "es_destino_pasajeros": False,
        "es_destino_carga": True,
        "tiene_puerta_a_puerta": False,
        "whatsapp_puerta_a_puerta_e164": None,
        "alias_busqueda": ["el alto", "eat", "alto"],
    },
]

# (ciudad, codigo, nombre, tipo, direccion, referencia, telefono, whatsapp, url_mapa, principal, lat, lon)
# Direcciones y teléfonos ficticios; sin enlace de mapa ni coordenadas.
OFICINAS = [
    (
        "SRE",
        "SRE-BOL",
        "Boletería Sucre",
        "boleteria",
        "Av. Los Álamos 100",
        "Terminal de buses, módulo A-12",
        "59170000120",
        None,
        None,
        True,
        None,
        None,
    ),
    (
        "SRE",
        "SRE-BOD",
        "Bodega Sucre",
        "bodega_carga",
        "Av. Los Álamos 120",
        "A media cuadra de la boletería",
        WHATSAPP_PUERTA_SUCRE,
        WHATSAPP_PUERTA_SUCRE,
        None,
        False,
        None,
        None,
    ),
    (
        "CMG",
        "CMG-BOL",
        "Boletería Camargo",
        "boleteria",
        "Calle Central 45",
        "Terminal de buses de Camargo",
        "59170000130",
        None,
        None,
        True,
        None,
        None,
    ),
    (
        "CMG",
        "CMG-BOD",
        "Bodega Camargo",
        "bodega_carga",
        "Calle Central 45",
        "Terminal de buses de Camargo",
        "59170000130",
        None,
        None,
        False,
        None,
        None,
    ),
    (
        "SCZ",
        "SCZ-BOL",
        "Boletería Santa Cruz",
        "boleteria",
        "Av. Los Tajibos 300",
        "Terminal de buses, módulo B-07",
        "59170000140",
        None,
        None,
        True,
        None,
        None,
    ),
    (
        "SCZ",
        "SCZ-BOD1",
        "Bodega Santa Cruz 1",
        "bodega_carga",
        "Av. Los Tajibos 320",
        None,
        "59170000141",
        None,
        None,
        False,
        None,
        None,
    ),
    (
        "SCZ",
        "SCZ-BOD2",
        "Bodega Santa Cruz 2",
        "bodega_carga",
        "Calle Las Palmeras 58, entre calles 3 y 4",
        None,
        WHATSAPP_PUERTA_SANTA_CRUZ,
        WHATSAPP_PUERTA_SANTA_CRUZ,
        None,
        False,
        None,
        None,
    ),
    (
        "TJA",
        "TJA-BOL",
        "Boletería Tarija",
        "boleteria",
        "Av. Los Sauces 210",
        "Terminal de buses, módulo C-03",
        "59170000150",
        None,
        None,
        True,
        None,
        None,
    ),
    (
        "TJA",
        "TJA-BOD",
        "Bodega Tarija",
        "bodega_carga",
        "Av. Los Sauces 230",
        None,
        "59170000150",
        None,
        None,
        False,
        None,
        None,
    ),
    (
        "PTS",
        "PTS-BOD",
        "Bodega Potosí",
        "bodega_carga",
        "Av. Las Minas 75",
        None,
        "59170000160",
        None,
        None,
        True,
        None,
        None,
    ),
    (
        "LPZ",
        "LPZ-BOL",
        "Boletería La Paz",
        "boleteria",
        "Av. Los Andes 980",
        "Terminal de buses, módulo D-21",
        "59170000170",
        None,
        None,
        True,
        None,
        None,
    ),
    (
        "LPZ",
        "LPZ-BOD",
        "Bodega La Paz",
        "bodega_carga",
        "Av. Los Andes 1010",
        None,
        "59170000171",
        None,
        None,
        False,
        None,
        None,
    ),
    (
        "EAT",
        "EAT-BOL",
        "Boletería El Alto",
        "boleteria",
        "Av. Las Flores 400",
        None,
        "59170000180",
        None,
        None,
        True,
        None,
        None,
    ),
    (
        "EAT",
        "EAT-BOD",
        "Bodega El Alto",
        "bodega_carga",
        "Av. Las Flores 420",
        None,
        "59170000181",
        None,
        None,
        False,
        None,
        None,
    ),
]

HORARIO_BOLETERIA = ("07:00", "20:00", range(1, 8))  # lunes a domingo
HORARIO_BODEGA = ("08:00", "18:00", range(1, 7))  # lunes a sábado

TIPOS_ASIENTO = [
    {
        "codigo": "SUITE_CAMA",
        "nombre": "Suite Cama",
        "planta": "alta",
        "inclinacion_grados": 180,
        "orden": 1,
        "descripcion": "Planta alta. Asientos que se reclinan hasta 180°, con TV individual.",
    },
    {
        "codigo": "LEITO_CAMA",
        "nombre": "Leito Cama",
        "planta": "baja",
        "inclinacion_grados": 160,
        "orden": 2,
        "descripcion": "Planta baja. Asientos que se reclinan hasta 160°, con TV en cabina.",
    },
]

COMODIDADES = [
    ("asientos_reclinables", "Asientos reclinables", "seat"),
    ("cargadores_usb", "Cargadores USB", "usb"),
    ("calefaccion", "Calefacción", "heat"),
    ("bano_unisex", "Baño unisex", "wc"),
    ("tv_individual", "TV individual", "tv"),
    ("tv_cabina", "TV en cabina", "tv"),
    ("aire_acondicionado", "Aire acondicionado", "snowflake"),
]

COMODIDADES_POR_TIPO = {
    "SUITE_CAMA": [
        "asientos_reclinables",
        "cargadores_usb",
        "calefaccion",
        "bano_unisex",
        "tv_individual",
        "aire_acondicionado",
    ],
    "LEITO_CAMA": [
        "asientos_reclinables",
        "cargadores_usb",
        "calefaccion",
        "bano_unisex",
        "tv_cabina",
        "aire_acondicionado",
    ],
}

# (codigo, origen, destino, km, minutos)
RUTAS = [
    ("SRE-SCZ", "SRE", "SCZ", 661, 840),
    ("SCZ-SRE", "SCZ", "SRE", 661, 840),
    ("SRE-TJA", "SRE", "TJA", 469, 660),
    ("TJA-SRE", "TJA", "SRE", 469, 660),
    ("SRE-LPZ", "SRE", "LPZ", 555, 720),
    ("LPZ-SRE", "LPZ", "SRE", 555, 720),
]

# (tipo, nombre, %, solo_boleteria, edad_min, edad_max, requisito, es_demo)
POLITICAS = [
    ("adulto", "Adulto", 0, False, 12, None, "Documento de identidad que coincida con el pasaje", False),
    (
        "menor",
        "Menor de edad (3 a 11 años)",
        50,
        True,
        3,
        11,
        "Permiso de Viaje de la Defensoría de la Niñez y Adolescencia",
        False,
    ),
    ("adulto_mayor", "Adulto mayor (60 años o más)", 20, True, 60, None, "Cédula de identidad", False),
    ("persona_con_discapacidad", "Persona con discapacidad", 50, True, None, None, "Carnet de discapacidad", True),
    ("embarazada", "Embarazada", 0, False, None, None, "Hasta 30 semanas de gestación", False),
]

FAQ_CATEGORIAS = [
    ("pasajeros", "Pasajeros", 1),
    ("pasajes_y_pagos", "Pasajes y pagos", 2),
    ("equipaje", "Equipaje", 3),
    ("viaje", "Viaje", 4),
    ("carga", "Carga y encomiendas", 5),
]

# (categoria, slug, pregunta, respuesta, respuesta corta para voz, palabras clave)
FAQS = [
    (
        "pasajeros",
        "viaje-de-menores",
        "Viaje de menores",
        "Todo menor de edad necesita el Permiso de Viaje emitido por la Defensoría de la Niñez y Adolescencia; "
        "sin él no puede subir al bus, así que conviene tramitarlo con tiempo.\n\n"
        "Los niños de 3 a 11 años pagan la mitad de la tarifa máxima referencial. Ese pasaje se compra solo en "
        "boletería, mostrando el Permiso de Viaje.",
        "Los menores necesitan el Permiso de Viaje de la Defensoría de la Niñez. De 3 a 11 años pagan la mitad, "
        "y ese pasaje se compra solo en boletería.",
        ["menor", "menores", "niño", "niña", "hijo", "permiso de viaje", "defensoria", "descuento"],
    ),
    (
        "pasajeros",
        "embarazadas",
        "Embarazadas",
        "Por seguridad, aceptamos pasajeras embarazadas hasta las 30 semanas de gestación.",
        "Las embarazadas pueden viajar hasta las 30 semanas de gestación.",
        ["embarazada", "embarazo", "gestacion", "semanas"],
    ),
    (
        "pasajeros",
        "adultos-mayores",
        "Adultos mayores",
        "Las personas de 60 años o más tienen el descuento de ley del 20% sobre la tarifa máxima referencial. "
        "Este pasaje con descuento se compra en boletería, presentando la cédula de identidad.",
        "Las personas de 60 años o más tienen 20% de descuento de ley, comprando en boletería.",
        ["adulto mayor", "tercera edad", "jubilado", "descuento", "60 años"],
    ),
    (
        "pasajeros",
        "mascotas",
        "Mascotas",
        "No transportamos mascotas, ni en cabina ni en bodega. Solo los perros guía (lazarillos) pueden viajar, "
        "siempre junto a su dueño.",
        "No se permiten mascotas, ni en cabina ni en bodega. La única excepción son los perros lazarillos.",
        ["mascota", "perro", "gato", "animal", "lazarillo"],
    ),
    (
        "pasajes_y_pagos",
        "facturas-y-boletos",
        "Facturas y boletos",
        "El pasaje electrónico vale también como factura.\n\nAl terminar la compra lo recibes en PDF en tu "
        "correo, y puedes descargarlo o imprimirlo cuando quieras.",
        "Tu pasaje electrónico es también tu factura. Te llega en PDF a tu correo.",
        ["factura", "nit", "boleto", "e-ticket", "pdf", "correo"],
    ),
    (
        "pasajes_y_pagos",
        "comprar-boletos-en-linea",
        "¿Puedo comprar boletos en línea?",
        f"Sí. Elige tu viaje, tus asientos y paga en línea desde {URL_COMPRA}.",
        "Sí, puedes comprar en línea en transdemo punto com.",
        ["comprar", "online", "en linea", "internet", "web", "pagina"],
    ),
    (
        "pasajes_y_pagos",
        "medios-de-pago",
        "¿Con qué medios de pago puedo comprar boletos?",
        "Aceptamos:\n\n- Pago con código QR de bancos bolivianos.\n- Tarjetas de débito o crédito Visa y "
        "Mastercard, nacionales o del exterior.\n- Tigo Money.",
        "Puedes pagar con QR de bancos bolivianos, tarjeta Visa o Mastercard, o Tigo Money.",
        ["pago", "pagar", "qr", "tarjeta", "visa", "mastercard", "tigo money", "debito", "credito"],
    ),
    (
        "pasajes_y_pagos",
        "pasajes-electronicos",
        "Sobre pasajes electrónicos",
        "Al abordar puedes mostrar el pasaje impreso o en la pantalla de tu celular.\n\nLos datos del pasaje "
        "deben coincidir con el documento de identidad del pasajero.",
        "Puedes mostrar el pasaje impreso o en tu celular. Debe coincidir con tu documento de identidad.",
        ["pasaje electronico", "imprimir", "celular", "abordar", "documento"],
    ),
    (
        "pasajes_y_pagos",
        "reajuste-de-precios",
        "Reajuste de precios",
        "El precio queda fijo desde el momento de la compra, aunque la tarifa cambie después.",
        "Una vez que compras el boleto, el precio ya no cambia.",
        ["precio", "tarifa", "reajuste", "aumento", "cambio"],
    ),
    (
        "pasajes_y_pagos",
        "reembolsos",
        "Reembolsos",
        "Si no vas a usar tu pasaje, te devolvemos el 85% de lo pagado. El 15% restante cubre los costos de "
        "emisión y facturación.\n\nEl reembolso se pide como mínimo 2 horas antes de la salida indicada en el "
        "pasaje; después de ese plazo, o una vez salido el bus, ya no hay devolución.\n\nSi compraste en "
        "boletería, pídelo en cualquier boletería. Si compraste en línea, llama a Atención al Cliente al "
        "+591 70000100. El dinero llega en un plazo de hasta 7 días hábiles.",
        "Te devolvemos el 85% si lo pides al menos 2 horas antes de la salida, llamando al 7 0 0 0 0 1 0 0. "
        "Después ya no hay devolución. El reembolso tarda hasta 7 días hábiles.",
        ["reembolso", "devolucion", "devolver", "devuelvan", "dinero", "cancelar", "anular", "85"],
    ),
    (
        "equipaje",
        "politica-de-equipajes",
        "Política de equipajes",
        "Cada pasajero puede llevar hasta 20 kg en la bodega del bus y hasta 5 kg de equipaje de mano.\n\n"
        "El peso adicional se cobra por kilo, con una tarifa que depende de la ruta.",
        "Cada pasajero lleva 20 kilos en bodega y 5 de mano. El exceso se cobra por kilo según la ruta.",
        ["equipaje", "maleta", "kilos", "kg", "exceso", "bodega", "mano", "buzon"],
    ),
    (
        "viaje",
        "hora-de-salida-demoras-y-cancelaciones",
        "Hora de salida, demoras y cancelaciones",
        "Los horarios pueden ajustarse por motivos operativos.\n\nSi cancelamos un viaje por causas propias "
        "de la empresa, te devolvemos el 100% del pasaje de inmediato.\n\nNo respondemos por retrasos "
        "causados por factores externos, como el estado de las carreteras, bloqueos o el clima.",
        "Si la empresa cancela el viaje, te devolvemos el 100% de inmediato. Los horarios pueden cambiar por "
        "condiciones del camino o del clima.",
        ["horario", "salida", "demora", "retraso", "cancelacion", "atraso", "bloqueo"],
    ),
    (
        "carga",
        "rastrear-mi-carga",
        "Quiero rastrear mi carga",
        f"Ingresa el número de guía de 8 dígitos en {URL_RASTREO} y verás en qué etapa está tu envío.",
        "Puedes rastrear tu carga con el número de guía de 8 dígitos.",
        ["rastrear", "rastreo", "encomienda", "carga", "guia", "tracking", "paquete"],
    ),
]

# (slug, titulo, descripcion, contenido markdown, url de origen)
PAGINAS = [
    (
        "inicio",
        "TransDemo | Pasajes de bus, carga y encomiendas",
        "Pasajes de bus en línea y encomiendas con seguimiento.",
        "# TransDemo\n\nViaja y envía por Bolivia: compra tus pasajes en línea y sigue tus encomiendas.\n\n"
        "- **Pasajes**: Sucre ↔ Santa Cruz, Tarija y La Paz.\n- **Buses** de dos pisos Suite Cama y Leito Cama."
        "\n- **Carga y encomiendas** a 7 ciudades, con puerta a puerta en Sucre y Santa Cruz.\n\n"
        "_TransDemo es una empresa ficticia creada para esta demostración._",
        None,
    ),
    (
        "pasajes",
        "Pasajes de bus",
        "Compra tus pasajes sin hacer fila.",
        "# Pasajes de bus\n\nElige tu viaje y tus asientos desde el celular, sin hacer fila. Paga con **QR, "
        f"tarjeta de débito o crédito, o Tigo Money**.\n\n[Comprar pasajes]({URL_COMPRA})",
        None,
    ),
    (
        "rutas",
        "Rutas e itinerarios",
        "Rutas de pasajeros y destinos de carga.",
        "# Rutas e itinerarios\n\n| Ruta | Distancia | Duración | Servicio |\n|---|---|---|---|\n"
        "| Sucre ↔ Santa Cruz | 661 km | 14 h | Suite Cama - Leito Cama |\n"
        "| Sucre ↔ Tarija | 469 km | 11 h | Suite Cama - Leito Cama |\n"
        "| Sucre ↔ La Paz | 555 km | 12 h | Suite Cama - Leito Cama |\n\n"
        "**Destinos de carga:** Sucre, Camargo, Santa Cruz, Tarija, La Paz, El Alto y Potosí.",
        None,
    ),
    (
        "buses",
        "Nuestros buses",
        "Buses de dos pisos Suite Cama y Leito Cama.",
        "# Nuestros buses\n\n## Suite Cama, piso superior\nAsientos que se reclinan hasta 180°, pantalla "
        "individual, cargador USB, calefacción, aire acondicionado y baño.\n\n## Leito Cama, piso inferior\n"
        "Asientos que se reclinan hasta 160°, pantalla compartida, cargador USB, calefacción, aire "
        "acondicionado y baño.",
        None,
    ),
    (
        "oficinas",
        "Boleterías y bodegas",
        "Direcciones de oficinas y bodegas.",
        "# Boleterías y bodegas\n\nBoleterías abiertas de 07:00 a 20:00 y bodegas de 08:00 a 18:00 en "
        "Sucre, Camargo, Santa Cruz, Tarija, Potosí, La Paz y El Alto. Consulta el detalle en "
        "`GET /api/v1/oficinas`.",
        None,
    ),
    (
        "carga",
        "Carga y encomienda",
        "Envíos nacionales con seguimiento en línea.",
        "# Carga y encomienda\n\n## Sobres y paquetes (hasta 30 kg)\nEnvíos a todo el país. Pagas al enviar o "
        "al recibir. Cuentas para empresas.\n\n## Carga (más de 30 kg)\nEnvíos grandes y mudanzas, con "
        "seguimiento GPS.\n\n## Puerta a puerta (desde 1 kg)\nPasamos a recoger tu envío a la dirección que "
        "nos indiques y lo dejamos en la puerta de quien lo recibe. Disponible en Sucre y Santa Cruz.\n\n"
        "- Entregas: lunes a viernes, de 08:00 a 12:00.\n- Recojos: lunes a viernes, de 14:00 a 17:00.\n"
        "- WhatsApp Sucre: +591 70000111 · Santa Cruz: +591 70000112.\n\n"
        "Guía electrónica y seguimiento en tiempo real.",
        None,
    ),
    (
        "ayuda",
        "Centro de ayuda",
        "Preguntas frecuentes.",
        "# Preguntas frecuentes\n\nConsulta las respuestas en `GET /api/v1/faqs`. WhatsApp: +591 70000101.",
        None,
    ),
    (
        "terminos",
        "Términos y condiciones",
        "Términos y condiciones del servicio.",
        "# Términos y condiciones\n\n" + EMPRESA["terminos_condiciones"],
        None,
    ),
]
