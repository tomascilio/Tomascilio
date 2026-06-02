"""
Crea la hoja "Detalle Mayo 2026" en Finanzas Mara con todas las
transacciones de Mastercard Black y Visa Signature (BBVA).
Correr: python3 crear_detalle_mara.py
"""

import sys
sys.path.insert(0, '.')
from sheets_updater import _get_credentials, _get_or_create_worksheet, _to_float
import gspread
from collections import defaultdict

SPREADSHEET_ID = "1F3mWKU_bTWLA89WYCJExQkSNx35wpTBegJjHnjUKugw"
SHEET_NAME = "Detalle Mayo 2026"

# [Fecha, Descripción, Cuotas, Monto $, Monto USD, Categoría, Tarjeta, Fuente]
TRANSACTIONS = [
    # MASTERCARD BLACK
    ["15/05/2026", "Merpago*Rappi",              "",        "$54.256,00",   "",         "Rappi",                             "Mastercard Black", "PDF"],
    ["18/05/2026", "Merpago*Cabify",             "",        "$10.130,63",   "",         "Transporte (cabify)",               "Mastercard Black", "PDF"],
    ["18/05/2026", "Merpago*Cabify",             "",        "$7.707,43",    "",         "Transporte (cabify)",               "Mastercard Black", "PDF"],
    ["24/05/2026", "Merpago*Rappi",              "",        "$30.190,00",   "",         "Rappi",                             "Mastercard Black", "PDF"],

    # VISA SIGNATURE — cuotas anteriores (ropa)
    ["28/07/2025", "Merpago*Randers",            "10 de 12","$45.806,58",   "",         "Ropa / Cuidado personal",           "Visa Signature",   "PDF"],
    ["07/11/2025", "Distribuidores Indep",        "7 de 18", "$40.111,11",   "",         "Otros variables",                   "Visa Signature",   "PDF"],
    ["14/12/2025", "Merpago*Natura",             "6 de 6",  "$21.261,66",   "",         "Ropa / Cuidado personal",           "Visa Signature",   "PDF"],
    ["24/12/2025", "Nike Arcos",                 "6 de 6",  "$12.166,50",   "",         "Ropa / Cuidado personal",           "Visa Signature",   "PDF"],
    ["24/12/2025", "Juleriaque",                 "6 de 6",  "$11.115,00",   "",         "Ropa / Cuidado personal",           "Visa Signature",   "PDF"],
    ["24/12/2025", "Merpago*Billabong",          "5 de 6",  "$33.332,66",   "",         "Ropa / Cuidado personal",           "Visa Signature",   "PDF"],
    ["27/12/2025", "Australian Gold",            "6 de 6",  "$46.116,66",   "",         "Ropa / Cuidado personal",           "Visa Signature",   "PDF"],
    ["08/01/2026", "Quiksilver",                 "5 de 6",  "$14.999,83",   "",         "Ropa / Cuidado personal",           "Visa Signature",   "PDF"],

    # VISA SIGNATURE — consumos Mayo 2026
    ["02/05/2026", "Merpago*Meli",              "",        "$8.990,00",    "",         "Otros variables",                   "Visa Signature",   "PDF"],
    ["04/05/2026", "3M3A SRL",                  "",        "$51.500,00",   "",         "Otros variables",                   "Visa Signature",   "PDF"],
    ["11/05/2026", "PedidosYa Rapanui",          "",        "$8.189,00",    "",         "Rappi",                             "Visa Signature",   "PDF"],
    ["11/05/2026", "PedidosYa Propina",          "",        "$600,00",      "",         "Rappi",                             "Visa Signature",   "PDF"],
    ["13/05/2026", "Apple.com/bill",             "",        "",             "US$11,19", "Servicios dig (spotify, nube, yt)", "Visa Signature",   "PDF"],
    ["15/05/2026", "Hertz Argentina",            "",        "$180.925,00",  "",         "Salidas / Ocio / Rest.",            "Visa Signature",   "PDF"],
    ["16/05/2026", "Merpago*Simonewegefeld",     "",        "$71.280,00",   "",         "Otros variables",                   "Visa Signature",   "PDF"],
    ["16/05/2026", "Mubi.com",                   "",        "",             "US$59,93", "Servicios dig (spotify, nube, yt)", "Visa Signature",   "PDF"],
    ["17/05/2026", "PedidosYa Mostaza",          "",        "$42.829,00",   "",         "Rappi",                             "Visa Signature",   "PDF"],
    ["17/05/2026", "PedidosYa Mostaza (dev.)",   "",        "-$13.479,89",  "",         "Rappi",                             "Visa Signature",   "PDF"],
    ["18/05/2026", "Merpago*Meryreservas",       "",        "$30.000,00",   "",         "Otros variables",                   "Visa Signature",   "PDF"],
    ["18/05/2026", "PedidosYa Propina",          "",        "$750,00",      "",         "Rappi",                             "Visa Signature",   "PDF"],
    ["19/05/2026", "Apple.com/bill",             "",        "",             "US$6,99",  "Servicios dig (spotify, nube, yt)", "Visa Signature",   "PDF"],
    ["21/05/2026", "Claude.ai",                  "",        "",             "US$20,00", "IA (CLAUDE,MIDJOU)",                "Visa Signature",   "PDF"],
    ["22/05/2026", "Merpago*CCA",                "",        "$19.635,00",   "",         "Otros variables",                   "Visa Signature",   "PDF"],
    ["24/05/2026", "Merpago*ValentinRamall",     "",        "$320.970,00",  "",         "Otros variables",                   "Visa Signature",   "PDF"],
    ["25/05/2026", "LinkedIn",                   "",        "",             "US$2,61",  "Servicios dig (spotify, nube, yt)", "Visa Signature",   "PDF"],
    ["26/05/2026", "Capricho Animal",            "1 de 3",  "$29.326,68",   "",         "Perros",                            "Visa Signature",   "PDF"],
    ["26/05/2026", "Apple.com/bill",             "",        "",             "US$9,99",  "Servicios dig (spotify, nube, yt)", "Visa Signature",   "PDF"],
    ["27/05/2026", "Merpago*BigBox",             "",        "$27.000,00",   "",         "Otros variables",                   "Visa Signature",   "PDF"],
]

HEADER = ["Fecha", "Descripción", "Cuotas", "Monto $", "Monto USD", "Categoría", "Tarjeta", "Fuente"]

COLOR_HEADER  = {"red": 0.18, "green": 0.18, "blue": 0.18}
COLOR_WHITE   = {"red": 1.0,  "green": 1.0,  "blue": 1.0}
COLOR_MC      = {"red": 0.95, "green": 1.0,  "blue": 0.92}   # verde claro → Mastercard
COLOR_VISA    = {"red": 0.90, "green": 0.95, "blue": 1.0}    # azul claro → Visa


def _parse_ars(val):
    if not val:
        return 0.0
    return _to_float(val.replace("$", "").replace(".", "").replace(",", "."))


def _parse_usd(val):
    if not val:
        return 0.0
    return _to_float(val.replace("US$", "").replace(",", "."))


def main():
    creds = _get_credentials()
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    ws = _get_or_create_worksheet(spreadsheet, SHEET_NAME)

    # Leer tipo de cambio desde Gastos!F2
    usd_rate = 0.0
    try:
        gastos_ws = spreadsheet.worksheet("Gastos")
        f2 = gastos_ws.acell("F2").value
        if f2:
            usd_rate = _to_float(str(f2))
            print(f"  → Tipo de cambio (Gastos!F2): ${usd_rate:,.2f}")
    except Exception as e:
        print(f"  ⚠ No se pudo leer F2: {e}")

    rows = [
        ["Detalle de gastos — Mayo 2026 (Mara)", "", "", "", "", "", "", ""],
        [""],
        HEADER,
    ]
    for t in TRANSACTIONS:
        rows.append(t)

    # Totales por tarjeta
    totals_ars = defaultdict(float)
    totals_usd = defaultdict(float)
    for t in TRANSACTIONS:
        card = t[6]
        totals_ars[card] += _parse_ars(t[3])
        totals_usd[card] += _parse_usd(t[4])

    rows.append([""])
    summary_header_row = len(rows) + 1
    rows.append(["Resumen por tarjeta", "", "", "Total $", "Total USD", "", "", ""])

    card_order = ["Mastercard Black", "Visa Signature"]
    for card in card_order:
        ars = totals_ars.get(card, 0)
        usd = totals_usd.get(card, 0)
        ars_str = f"${ars:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if ars else ""
        usd_str = f"US${usd:,.2f}" if usd else ""
        rows.append([card, "", "", ars_str, usd_str, "", "", ""])

    # Total general
    total_ars = sum(totals_ars.values())
    total_usd = sum(totals_usd.values())
    total_combinado = total_ars + (total_usd * usd_rate if usd_rate else 0)
    usd_nota = f" (US${total_usd:,.2f} × ${usd_rate:,.0f})" if usd_rate and total_usd else ""
    total_str = f"${total_combinado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    rows.append([""])
    grand_total_row = len(rows) + 1
    rows.append([f"TOTAL GENERAL{usd_nota}", "", "", total_str, "", "", "", ""])

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

    # Formato filas por tarjeta
    for i, t in enumerate(TRANSACTIONS):
        row_num = i + 4
        color = COLOR_MC if "Mastercard" in t[6] else COLOR_VISA
        try:
            ws.format(f"A{row_num}:H{row_num}", {"backgroundColor": color})
        except Exception:
            pass

    # Formato resumen
    try:
        ws.format(f"A{summary_header_row}:H{summary_header_row}", {
            "backgroundColor": {"red": 0.20, "green": 0.45, "blue": 0.65},
            "textFormat": {"foregroundColor": COLOR_WHITE, "bold": True},
        })
        for j, card in enumerate(card_order):
            r = summary_header_row + 1 + j
            color = COLOR_MC if "Mastercard" in card else COLOR_VISA
            ws.format(f"A{r}:H{r}", {"backgroundColor": color})
        ws.format(f"A{grand_total_row}:H{grand_total_row}", {
            "backgroundColor": {"red": 0.12, "green": 0.53, "blue": 0.30},
            "textFormat": {"foregroundColor": COLOR_WHITE, "bold": True, "fontSize": 11},
        })
    except Exception:
        pass

    # Ajustar anchos
    try:
        sheet_id = ws.id
        requests = [{"updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i+1},
            "properties": {"pixelSize": w}, "fields": "pixelSize"}}
            for i, w in enumerate([100, 260, 80, 110, 90, 230, 140, 90])]
        spreadsheet.batch_update({"requests": requests})
    except Exception:
        pass

    print(f"✓ Hoja '{SHEET_NAME}' creada en Finanzas Mara con {len(TRANSACTIONS)} transacciones.")
    if usd_rate:
        print(f"  Total general: {total_str}")


if __name__ == "__main__":
    main()
