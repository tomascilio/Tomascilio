"""
Crea la hoja "Detalle Mayo 2026" en Finanzas Tomi con todas las
transacciones compartidas (Excel VISA, AMEX y screenshots de MP).
Correr: python3 crear_detalle.py
"""

import sys
sys.path.insert(0, '.')
from sheets_updater import _get_credentials, SPREADSHEET_ID, _get_or_create_worksheet
import gspread

SHEET_NAME = "Detalle Mayo 2026"

# ── Todas las transacciones ────────────────────────────────────────────────
# [Fecha, Descripción, Cuotas, Monto $, Monto USD, Categoría, Tarjeta, Fuente]
TRANSACTIONS = [
    # VISA 3416
    ["03/09/2025", "Merpago*escueladavinc",    "9 de 12", "$14.025,00",    "",          "Facultad",                         "Visa 3416",  "Excel"],
    ["02/12/2025", "Merpago*byp",               "6 de 9",  "$10.000,00",    "",          "⚠ No identificada",                "Visa 3416",  "Excel"],
    ["04/12/2025", "Merpago*escueladavinc",    "6 de 12", "$3.250,00",     "",          "Facultad",                         "Visa 3416",  "Excel"],
    ["26/12/2025", "Merpago*neixer",            "5 de 6",  "$9.994,87",     "",          "⚠ No identificada",                "Visa 3416",  "Excel"],
    ["26/12/2025", "Merpago*joyeriaororub",    "5 de 9",  "$15.466,22",    "",          "Ropa / Cuidado personal",          "Visa 3416",  "Excel"],
    ["09/02/2026", "Plan v (tna 48,00)",        "4 de 15", "$254.833,96",   "",          "Créditos",                         "Visa 3416",  "Excel"],
    ["01/05/2026", "Spotify",                   "",        "",              "US$1,31",   "Servicios dig (spotify, nube, yt)","Visa 3416",  "Excel"],
    ["02/05/2026", "Apple.com/bill",            "",        "",              "US$4,99",   "Servicios dig (spotify, nube, yt)","Visa 3416",  "Excel"],
    ["08/05/2026", "Apple.com/bill",            "",        "",              "US$2,99",   "Servicios dig (spotify, nube, yt)","Visa 3416",  "Excel"],
    ["20/05/2026", "Adobe.com",                 "",        "",              "US$25,07",  "Programas (Adobe)",                "Visa 3416",  "Excel"],
    ["20/05/2026", "Google *google",            "",        "",              "US$9,99",   "Servicios dig (spotify, nube, yt)","Visa 3416",  "Excel"],

    # AMEX 7928
    ["19/02/2026", "970781*df festival",        "4 de 6",  "$32.500,00",    "",          "Salidas / Ocio / Rest.",            "AMEX 7928",  "Excel"],
    ["04/03/2026", "Merpago*mercadolibre",      "3 de 3",  "$26.099,66",    "",          "Otros variables",                  "AMEX 7928",  "Excel"],
    ["26/05/2026", "Telecentro s.a.",           "",        "$67.242,48",    "",          "Servicios (luz, gas, internet)",   "AMEX 7928",  "Excel"],

    # Mercado Pago Mastercard (screenshots)
    ["27/05/2026", "Mercado Libre",             "",        "$43.990,00",    "",          "Otros variables",                  "MP Mastercard", "Screenshot"],
    ["22/05/2026", "Mercado Libre",             "",        "$22.822,49",    "",          "Otros variables",                  "MP Mastercard", "Screenshot"],
    ["18/05/2026", "Claude Ai",                 "",        "",              "US$20,00",  "IA (CLAUDE,MIDJOU)",               "MP Mastercard", "Screenshot"],
    ["18/05/2026", "Escuela Da Vinci",          "",        "$333.187,00",   "",          "Facultad",                         "MP Mastercard", "Screenshot"],
    ["15/05/2026", "Coto",                      "",        "$334.963,59",   "",          "Comida / Supermercado",            "MP Mastercard", "Screenshot"],
    ["14/05/2026", "Venti Latam",               "",        "$80.500,00",    "",          "Salidas / Ocio / Rest.",            "MP Mastercard", "Screenshot"],
    ["09/05/2026", "Midjourney Inc.",           "",        "",              "US$10,00",  "IA (CLAUDE,MIDJOU)",               "MP Mastercard", "Screenshot"],
    ["09/05/2026", "Tuenti",                    "",        "$16.650,00",    "",          "Celular - Tuenti",                 "MP Mastercard", "Screenshot"],
]

HEADER = ["Fecha", "Descripción", "Cuotas", "Monto $", "Monto USD", "Categoría", "Tarjeta", "Fuente"]

COLOR_HEADER    = {"red": 0.18, "green": 0.18, "blue": 0.18}
COLOR_WHITE     = {"red": 1.0,  "green": 1.0,  "blue": 1.0}
COLOR_UNKNOWN   = {"red": 1.0,  "green": 0.95, "blue": 0.90}
COLOR_VISA      = {"red": 0.90, "green": 0.95, "blue": 1.0}
COLOR_AMEX      = {"red": 0.95, "green": 1.0,  "blue": 0.92}
COLOR_MP        = {"red": 1.0,  "green": 0.98, "blue": 0.88}


def main():
    creds = _get_credentials()
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    ws = _get_or_create_worksheet(spreadsheet, SHEET_NAME)

    # Título
    rows = [
        [f"Detalle de gastos — Mayo 2026", "", "", "", "", "", "", ""],
        [""],
        HEADER,
    ]

    for t in TRANSACTIONS:
        rows.append(t)

    ws.update("A1", rows, value_input_option="USER_ENTERED")

    # Formato título
    ws.format("A1", {
        "backgroundColor": COLOR_HEADER,
        "textFormat": {"foregroundColor": COLOR_WHITE, "bold": True, "fontSize": 13},
    })

    # Formato encabezado
    ws.format("A3:H3", {
        "backgroundColor": {"red": 0.26, "green": 0.26, "blue": 0.26},
        "textFormat": {"foregroundColor": COLOR_WHITE, "bold": True},
    })

    # Formato filas por tarjeta y no identificadas
    for i, t in enumerate(TRANSACTIONS):
        row_num = i + 4  # filas 4 en adelante
        tarjeta = t[6]
        categoria = t[5]
        if "No identificada" in categoria:
            color = COLOR_UNKNOWN
        elif "Visa" in tarjeta:
            color = COLOR_VISA
        elif "AMEX" in tarjeta:
            color = COLOR_AMEX
        else:
            color = COLOR_MP
        try:
            ws.format(f"A{row_num}:H{row_num}", {"backgroundColor": color})
        except Exception:
            pass

    # Ajustar anchos
    try:
        sheet_id = ws.id
        requests = [{"updateDimensionProperties": {"range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i+1}, "properties": {"pixelSize": w}, "fields": "pixelSize"}}
                    for i, w in enumerate([100, 260, 80, 110, 90, 230, 130, 100])]
        spreadsheet.batch_update({"requests": requests})
    except Exception:
        pass

    print(f"✓ Hoja '{SHEET_NAME}' creada con {len(TRANSACTIONS)} transacciones.")


if __name__ == "__main__":
    main()
