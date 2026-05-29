"""
Mapeo de transacciones a las categorías de Finanzas Tomi.

Reglas ordenadas por prioridad: la primera que matchea gana.
Cada regla es (categoría, [keywords en minúsculas]).
"""

CATEGORY_RULES = [
    # ── GASTOS FIJOS ──────────────────────────────────────────────
    (
        "Servicios (luz, gas, internet)",
        ["telecentro", "edesur", "metrogas", "naturgy", "fibertel", "cablevision", "internet"],
    ),
    (
        "Programas (Adobe)",
        ["adobe"],
    ),
    (
        "IA (CLAUDE, MIDJOU)",
        ["claude", "anthropic", "midjourney", "openai", "chatgpt", "claude ai"],
    ),
    (
        "Servicios dig (spotify, nube, yt)",
        ["spotify", "apple.com", "apple.com/bill", "icloud", "netflix", "youtube",
         "google one", "google *google", "google storage", "dropbox", "onedrive"],
    ),
    (
        "Celular - Tuenti",
        ["tuenti", "claro", "personal telco", "movistar"],
    ),
    (
        "Facultad",
        ["escueladavinc", "escuela da vinci", "da vinci", "uba", "uade", "palermo",
         "universidad", "instituto", "colegio"],
    ),
    (
        "Créditos",
        ["plan v", "plan visa", "tna ", "prestamo", "crédito personal", "credito personal",
         "descubierto", "financiacion"],
    ),
    (
        "Psicóloga",
        ["psicolog", "terapeuta", "terapia"],
    ),
    (
        "Vivienda / Alquiler",
        ["alquiler", "inmobiliaria", "propietario"],
    ),

    # ── GASTOS VARIABLES ─────────────────────────────────────────
    (
        "Comida / Supermercado",
        ["coto", "carrefour", "dia ", "jumbo", "walmart", "disco ", "vea ",
         "changomas", "supermercado", "almacen", "verduleria", "verdulería",
         "merpago*coto", "merpago*carrefour", "merpago*jumbo"],
    ),
    (
        "Salidas / Ocio / Rest.",
        ["festival", "teatro", "cine", "bar ", "resto", "restaurant", "venti latam",
         "ticketek", "ticketmaster", "evento", "boliche", "parque", "museo",
         "df festival", "entradas"],
    ),
    (
        "Salud / Farmacia",
        ["farmacia", "farmacity", "drogueria", "droguería", "osde", "swiss medical",
         "medico", "medica", "clinica", "hospital", "laboratorio"],
    ),
    (
        "Ropa / Cuidado personal",
        ["joyeria", "joyería", "zara", "falabella", "adidas", "nike", "h&m",
         "peluqueria", "peluquería", "indumentaria", "ropa", "calzado"],
    ),
    (
        "Transporte fijo (SUBE)",
        ["sube", "subte", "colectivo", "tren ", "cabify", "uber", "rappi envios"],
    ),
    (
        "Comida / Supermercado",
        ["rappi", "pedidosya", "pedidos ya"],
    ),
    (
        "Otros variables",
        ["merpago*mercadolibre", "mercadolibre", "mercado libre"],
    ),
    (
        "Arreglos casa",
        ["ferreteria", "ferrería", "pinturas", "muebles", "cortinas", "homedepo",
         "easy ", "sodimac"],
    ),
    (
        "Tocadiscos",
        ["vinilo", "discos", "musimundo", "el arranque"],
    ),
]


def categorize_transactions(transactions: list[dict]) -> list[dict]:
    """
    Recibe una lista de transacciones con al menos el campo 'description'.
    Agrega el campo 'category' a cada una.
    Las que no matcheen quedan con category=None (se agrupan como "no identificadas").
    """
    for t in transactions:
        t["category"] = _match_category(t.get("description", ""))
    return transactions


def _match_category(description: str) -> str | None:
    desc_lower = description.lower()
    for category, keywords in CATEGORY_RULES:
        if any(kw in desc_lower for kw in keywords):
            return category
    return None
