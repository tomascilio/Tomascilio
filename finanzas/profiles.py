"""
Perfiles de configuración por persona.
Cada perfil define el SPREADSHEET_ID y el mapeo de categorías a etiquetas de la hoja Gastos.
"""

PROFILES = {
    "tomi": {
        "spreadsheet_id": "1qrLkvC2oNFz42aeXxAnsE26LdJnNhk5cgqld-XZi82Q",
        "category_map": {
            "Vivienda / Alquiler":               "Vivienda / Alquiler",
            "Servicios (luz, gas, internet)":    "Servicios (luz, gas, internet)",
            "Transporte fijo (SUBE)":            "Transporte fijo (SUBE)",
            "Créditos":                          "Créditos",
            "Psicóloga":                         "Psicologa",
            "Celular - Tuenti":                  "Celular - Tuenti",
            "Facultad":                          "Facultad",
            "Programas (Adobe)":                 "Programas (Adobe)",
            "IA (CLAUDE, MIDJOU)":               "IA (CLAUDE,MIDJOU)",
            "Servicios dig (spotify, nube, yt)": "Servicios dig(spotify,nube,yt)",
            "Comida / Supermercado":             "Comida / Supermercado",
            "Salidas / Ocio / Rest.":            "Salidas / Ocio / Rest.",
            "Arreglos casa":                     "Arreglos casa",
            "Ropa / Cuidado personal":           "Ropa / Cuidado personal",
            "Salud / Farmacia":                  "Salud / Farmacia",
            "Tocadiscos":                        "Tocadiscos",
            "Otros variables":                   "Otros variables",
        },
    },
    "mara": {
        "spreadsheet_id": "1F3mWKU_bTWLA89WYCJExQkSNx35wpTBegJjHnjUKugw",
        "category_map": {
            "Vivienda / Alquiler":               "Vivienda / Alquiler",
            "Servicios (luz, gas, internet)":    "Servicios (luz, gas, internet)",
            "Créditos":                          "Cuotas / Créditos",
            "Psicóloga":                         "Psicologa",
            "Celular - Tuenti":                  "Celular - Claro",
            "Facultad":                          "Facultad",
            "Programas (Adobe)":                 "Programas (capcut)",
            "IA (CLAUDE, MIDJOU)":               "IA (claude,)",
            "Servicios dig (spotify, nube, yt)": "Servicios (spotify,nube,linkedi,netflix)",
            "Comida / Supermercado":             "Comida / Supermercado",
            "Salidas / Ocio / Rest.":            "Salidas / Ocio / Rest.",
            "Ropa / Cuidado personal":           "Ropa / Cuidado personal",
            "Salud / Farmacia":                  "Salud / Farmacia",
            "Otros variables":                   "Otros variables",
            "Transporte fijo (SUBE)":            "Transporte (cabify)",
        },
    },
}

DEFAULT_PROFILE = "tomi"


def get_profile(name: str) -> dict:
    if name not in PROFILES:
        raise ValueError(f"Perfil '{name}' no encontrado. Disponibles: {list(PROFILES.keys())}")
    return PROFILES[name]
