"""
Escribe los resultados del parser en el Google Sheet "Finanzas Tomi".

Crea (o reemplaza) una hoja llamada "Consumos [Mes Año]" con:
  - Tabla de transacciones categorizadas (ordenadas por categoría)
  - Sección "Transacciones no identificadas" con la info completa
  - Resumen agrupado por categoría al final

Autenticación:
  - Usa el archivo credentials.json (OAuth Desktop) que generás desde Google Cloud Console.
  - La primera vez abre el browser para dar permiso; después cachea el token en token.json.
  - Ver README.md para el paso a paso.
"""

import os
from collections import defaultdict
from pathlib import Path

import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# ID del Google Sheet "Finanzas Tomi"
SPREADSHEET_ID = "1qrLkvC2oNFz42aeXxAnsE26LdJnNhk5cgqld-XZi82Q"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

# Carpeta donde buscar credentials.json y guardar token.json
_CREDS_DIR = Path(__file__).parent

# ── Estilos (colores en formato HEX para gspread) ──────────────────────────
_COLOR_HEADER = {"red": 0.18, "green": 0.18, "blue": 0.18}          # gris oscuro
_COLOR_HEADER_TEXT = {"red": 1.0, "green": 1.0, "blue": 1.0}         # blanco
_COLOR_SUMMARY_BG = {"red": 0.95, "green": 0.97, "blue": 1.0}        # azul muy claro
_COLOR_UNKNOWN_BG = {"red": 1.0, "green": 0.95, "blue": 0.90}        # naranja muy claro
_COLOR_TOTAL_BG = {"red": 0.20, "green": 0.60, "blue": 0.40}         # verde
_COLOR_TOTAL_TEXT = {"red": 1.0, "green": 1.0, "blue": 1.0}


# ── Autenticación ─────────────────────────────────────────────────────────

def _get_credentials() -> Credentials:
    token_path = _CREDS_DIR / "token.json"
    creds_path = _CREDS_DIR / "credentials.json"

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                raise FileNotFoundError(
                    f"No se encontró {creds_path}\n"
                    "Seguí los pasos en README.md para crear las credenciales OAuth."
                )
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return creds


# ── Función principal ──────────────────────────────────────────────────────

def update_google_sheet(summary: dict) -> None:
    """
    Toma el resumen procesado de una tarjeta y:
    1. Crea/actualiza la hoja "Consumos [Mes Año]" con el detalle completo
    2. Carga los totales por categoría en la hoja "Gastos" del mes correspondiente
    """
    creds = _get_credentials()
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    # 1. Hoja de detalle de consumos
    sheet_name = _build_sheet_name(summary)
    worksheet = _get_or_create_worksheet(spreadsheet, sheet_name)
    rows, formats = _build_sheet_data(summary)
    _write_sheet(worksheet, rows, formats, summary)
    print(f"  → Hoja '{sheet_name}' actualizada en Finanzas Tomi")

    # 2. Cargar totales en la hoja Gastos
    gastos_sheet = _find_gastos_sheet(spreadsheet, summary.get("closing_date", ""))
    if gastos_sheet:
        _update_gastos_sheet(gastos_sheet, summary["transactions"])
        print(f"  → Totales cargados en hoja '{gastos_sheet.title}'")


# ── Mapeo categorías del script → etiquetas exactas en la hoja Gastos ────
_CATEGORY_TO_SHEET_LABEL = {
    "Vivienda / Alquiler":              "Vivienda / Alquiler",
    "Servicios (luz, gas, internet)":   "Servicios (luz, gas, internet)",
    "Transporte fijo (SUBE)":           "Transporte fijo (SUBE)",
    "Créditos":                         "Créditos",
    "Psicóloga":                        "Psicologa",
    "Celular - Tuenti":                 "Celular - Tuenti",
    "Facultad":                         "Facultad",
    "Programas (Adobe)":                "Programas (Adobe)",
    "IA (CLAUDE, MIDJOU)":              "IA (CLAUDE,MIDJOU)",
    "Servicios dig (spotify, nube, yt)":"Servicios dig(spotify,nube,yt)",
    "Comida / Supermercado":            "Comida / Supermercado",
    "Salidas / Ocio / Rest.":           "Salidas / Ocio / Rest.",
    "Arreglos casa":                    "Arreglos casa",
    "Ropa / Cuidado personal":          "Ropa / Cuidado personal",
    "Salud / Farmacia":                 "Salud / Farmacia",
    "Tocadiscos":                       "Tocadiscos",
    "Otros variables":                  "Otros variables",
}


def _find_gastos_sheet(spreadsheet, closing_date: str):
    """Siempre carga en la hoja 'Gastos' (el mes activo)."""
    all_sheets = {ws.title: ws for ws in spreadsheet.worksheets()}
    return all_sheets.get("Gastos")


def _update_gastos_sheet(worksheet, transactions: list) -> None:
    """
    Suma los montos por categoría y los escribe en las celdas correspondientes
    de la hoja Gastos. Solo actualiza las celdas que tienen una categoría mapeada.
    Suma al valor existente para no pisar datos ya cargados.
    """
    # Calcular totales por categoría (solo $ARS)
    totals = defaultdict(float)
    for t in transactions:
        cat = t.get("category")
        if cat and t.get("amount_ars"):
            totals[cat] += _to_float(t["amount_ars"])

    if not totals:
        return

    # Leer todas las celdas de la hoja para encontrar las filas
    all_values = worksheet.get_all_values()

    # Construir índice: texto normalizado → (fila, col_monto) 1-indexed
    # Busca el label en las primeras 3 columnas para cubrir distintos layouts
    label_to_row = {}   # norm_label → (row_num, amount_col)
    for i, row in enumerate(all_values):
        for col_idx, cell in enumerate(row[:3]):
            if cell and cell.strip():
                norm = _normalize(cell)
                if norm not in label_to_row:
                    # la columna del monto es la siguiente
                    amount_col = col_idx + 2  # 1-indexed, siguiente columna
                    label_to_row[norm] = (i + 1, amount_col)

    # Preparar actualizaciones
    updates = []
    for cat, amount in totals.items():
        sheet_label = _CATEGORY_TO_SHEET_LABEL.get(cat)
        if not sheet_label:
            continue

        # Búsqueda exacta normalizada
        match = label_to_row.get(_normalize(sheet_label))

        # Búsqueda parcial como fallback
        if not match:
            normalized_label = _normalize(sheet_label)
            for norm_key, val in label_to_row.items():
                if normalized_label in norm_key or norm_key in normalized_label:
                    match = val
                    break

        if not match:
            print(f"    ⚠ No se encontró la fila para '{sheet_label}' en Gastos")
            continue

        row_num, amount_col = match

        updates.append({
            "range": gspread.utils.rowcol_to_a1(row_num, amount_col),
            "values": [[amount]],
        })
        print(f"    → {sheet_label}: ${amount:,.2f}")

    if updates:
        worksheet.batch_update(updates, value_input_option="USER_ENTERED")


# ── Nombre de la hoja ──────────────────────────────────────────────────────

_MONTH_NAMES = {
    "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
    "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
    "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre",
}


def _build_sheet_name(summary: dict) -> str:
    closing = summary.get("closing_date", "")
    if len(closing) == 7:  # YYYY-MM
        year, month = closing.split("-")
        month_name = _MONTH_NAMES.get(month, month)
        return f"Consumos {month_name} {year}"
    return f"Consumos {summary['card_type']} {summary['card_last4']}"


# ── Crear o limpiar hoja ───────────────────────────────────────────────────

def _get_or_create_worksheet(spreadsheet, name: str):
    try:
        ws = spreadsheet.worksheet(name)
        ws.clear()
        return ws
    except gspread.exceptions.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=name, rows=500, cols=8)


# ── Construir datos ────────────────────────────────────────────────────────

def _build_sheet_data(summary: dict) -> tuple[list[list], list[dict]]:
    """
    Devuelve (filas, lista_de_formatos).
    Cada formato es {"range": "A1:H1", "format": {...}}.
    """
    transactions = summary["transactions"]
    card_label = f"{summary['bank']} · {summary['card_type']} terminada en {summary['card_last4']}"
    closing = summary.get("closing_date", "")

    identified = [t for t in transactions if t.get("category")]
    unidentified = [t for t in transactions if not t.get("category")]

    rows = []
    formats = []

    def _row():
        return len(rows) + 1  # fila actual (1-indexed)

    # ── Título ────────────────────────────────────────────────────
    rows.append([f"Consumos {card_label}", "", "", "", "", "", "", ""])
    formats.append({
        "range": f"A{_row()-1}",
        "format": {
            "backgroundColor": _COLOR_HEADER,
            "textFormat": {"foregroundColor": _COLOR_HEADER_TEXT, "bold": True, "fontSize": 12},
        },
    })

    rows.append([f"Cierre: {closing}", "", "", "", "", "", "", ""])
    rows.append([""])  # espacio

    # ── Encabezado de transacciones ───────────────────────────────
    header_row = _row()
    rows.append(["Fecha", "Descripción", "Cuotas", "Monto $", "Monto USD", "Categoría", "Tarjeta", "Archivo"])
    formats.append({
        "range": f"A{header_row}:H{header_row}",
        "format": {
            "backgroundColor": {"red": 0.26, "green": 0.26, "blue": 0.26},
            "textFormat": {"foregroundColor": _COLOR_HEADER_TEXT, "bold": True},
        },
    })

    # ── Filas de transacciones identificadas ─────────────────────
    identified_sorted = sorted(identified, key=lambda t: t.get("category", ""))
    last_category = None

    for t in identified_sorted:
        # Separador de categoría
        if t["category"] != last_category:
            last_category = t["category"]
            cat_row = _row()
            rows.append([t["category"], "", "", "", "", "", "", ""])
            formats.append({
                "range": f"A{cat_row}",
                "format": {
                    "backgroundColor": _COLOR_SUMMARY_BG,
                    "textFormat": {"bold": True, "italic": True},
                },
            })

        rows.append([
            t.get("date", ""),
            t.get("description", ""),
            t.get("installments", ""),
            t.get("amount_ars", ""),
            t.get("amount_usd", ""),
            t.get("category", ""),
            f"{summary['card_type']} {summary['card_last4']}",
            summary.get("source_file", ""),
        ])

    rows.append([""])  # espacio

    # ── Sección no identificadas ──────────────────────────────────
    if unidentified:
        unk_header_row = _row()
        rows.append(["⚠ Transacciones no identificadas", "", "", "", "", "", "", ""])
        formats.append({
            "range": f"A{unk_header_row}:H{unk_header_row}",
            "format": {
                "backgroundColor": _COLOR_UNKNOWN_BG,
                "textFormat": {"bold": True, "fontSize": 11},
            },
        })

        for t in unidentified:
            unk_row = _row()
            rows.append([
                t.get("date", ""),
                t.get("description", ""),
                t.get("installments", ""),
                t.get("amount_ars", ""),
                t.get("amount_usd", ""),
                "⚠ No identificada",
                f"{summary['card_type']} {summary['card_last4']}",
                summary.get("source_file", ""),
            ])
            formats.append({
                "range": f"A{unk_row}:H{unk_row}",
                "format": {"backgroundColor": _COLOR_UNKNOWN_BG},
            })

        rows.append([""])

    # ── Resumen por categoría ─────────────────────────────────────
    summary_header_row = _row()
    rows.append(["Resumen por categoría", "", "Total $", "Total USD", "", "", "", ""])
    formats.append({
        "range": f"A{summary_header_row}:H{summary_header_row}",
        "format": {
            "backgroundColor": {"red": 0.20, "green": 0.45, "blue": 0.65},
            "textFormat": {"foregroundColor": _COLOR_HEADER_TEXT, "bold": True},
        },
    })

    by_category = defaultdict(lambda: {"ars": 0.0, "usd": 0.0})
    for t in identified:
        by_category[t["category"]]["ars"] += _to_float(t.get("amount_ars", ""))
        by_category[t["category"]]["usd"] += _to_float(t.get("amount_usd", ""))

    for cat, totals in sorted(by_category.items()):
        ars_str = f"${totals['ars']:,.2f}" if totals["ars"] else ""
        usd_str = f"U$S{totals['usd']:,.2f}" if totals["usd"] else ""
        rows.append([cat, "", ars_str, usd_str, "", "", "", ""])

    if unidentified:
        unk_ars = sum(_to_float(t.get("amount_ars", "")) for t in unidentified)
        unk_usd = sum(_to_float(t.get("amount_usd", "")) for t in unidentified)
        rows.append([
            f"⚠ No identificadas ({len(unidentified)} transacciones)",
            "",
            f"${unk_ars:,.2f}" if unk_ars else "",
            f"U$S{unk_usd:,.2f}" if unk_usd else "",
            "", "", "", "",
        ])

    rows.append([""])

    # Total general
    total_ars = sum(_to_float(t.get("amount_ars", "")) for t in transactions)
    total_usd = sum(_to_float(t.get("amount_usd", "")) for t in transactions)
    total_row = _row()
    rows.append([
        "TOTAL",
        "",
        f"${total_ars:,.2f}",
        f"U$S{total_usd:,.2f}" if total_usd else "",
        "", "", "", "",
    ])
    formats.append({
        "range": f"A{total_row}:H{total_row}",
        "format": {
            "backgroundColor": _COLOR_TOTAL_BG,
            "textFormat": {"foregroundColor": _COLOR_TOTAL_TEXT, "bold": True},
        },
    })

    return rows, formats


def _normalize(text: str) -> str:
    """Normaliza texto para comparación robusta: minúsculas, sin acentos, sin espacios extra."""
    import unicodedata
    text = text.strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


def _to_float(value: str) -> float:
    if not value:
        return 0.0
    cleaned = value.replace("$", "").replace("U$S", "").strip()
    # Formato argentino: 1.234.567,89 → punto=miles, coma=decimal
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    # Solo coma como decimal: 1234,89
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    # Solo punto — si hay más de uno, o si hay exactamente 3 dígitos después → miles
    elif "." in cleaned:
        parts = cleaned.split(".")
        if len(parts) > 2 or (len(parts) == 2 and len(parts[-1]) == 3):
            cleaned = cleaned.replace(".", "")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


# ── Escritura en Google Sheets ────────────────────────────────────────────

def _write_sheet(worksheet, rows: list, formats: list, summary: dict) -> None:
    # Escribir todas las filas de una vez
    worksheet.update("A1", rows, value_input_option="USER_ENTERED")

    # Aplicar formatos
    for fmt in formats:
        try:
            worksheet.format(fmt["range"], fmt["format"])
        except Exception:
            pass  # No bloquear si falla un formato individual

    # Ajustar ancho de columnas
    try:
        spreadsheet = worksheet.spreadsheet
        sheet_id = worksheet.id
        requests = [
            {
                "updateDimensionProperties": {
                    "range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i + 1},
                    "properties": {"pixelSize": width},
                    "fields": "pixelSize",
                }
            }
            for i, width in enumerate([100, 280, 90, 110, 100, 220, 130, 180])
        ]
        spreadsheet.batch_update({"requests": requests})
    except Exception:
        pass
