"""
Parser para resúmenes de tarjeta en formato Excel (.xlsx).
Soporta el formato de Mercado Pago / BBVA / Galicia que exporta:
  - Encabezado con nombre de tarjeta, fecha de cierre, montos totales
  - Sección "Pago de tarjeta y devoluciones"
  - Sección de transacciones con columnas: Fecha, Descripción, Cuotas, Comprobante, Monto $, Monto USD
"""

import re
from pathlib import Path
from datetime import datetime

import openpyxl


def parse_excel(path: Path) -> dict:
    wb = openpyxl.load_workbook(path)
    ws = wb.active

    rows = [
        [cell.value for cell in row]
        for row in ws.iter_rows()
        if any(cell.value is not None for cell in row)
    ]

    bank, card_type, card_last4 = _detect_card(rows)
    closing_date = _detect_closing_date(rows)
    transactions = _extract_transactions(rows)

    return {
        "bank": bank,
        "card_type": card_type,
        "card_last4": card_last4,
        "closing_date": closing_date,
        "transactions": transactions,
        "source_file": path.name,
    }


def _detect_card(rows: list) -> tuple[str, str, str]:
    """Detecta banco, tipo de tarjeta y últimos 4 dígitos."""
    # Mercado Pago se detecta por el patrón "Merpago*" en las transacciones
    full_text = " ".join(str(cell) for row in rows for cell in row if cell).lower()
    if "merpago*" in full_text or "mercadopago" in full_text:
        guessed_bank = "Mercado Pago"
    else:
        guessed_bank = None

    for row in rows[:5]:
        for cell in row:
            if cell and isinstance(cell, str):
                cell_lower = cell.lower()

                # Detectar tipo de tarjeta
                if "visa" in cell_lower:
                    card_type = "Visa"
                elif "american express" in cell_lower or "amex" in cell_lower:
                    card_type = "American Express"
                elif "mastercard" in cell_lower:
                    card_type = "Mastercard"
                else:
                    continue

                # Detectar banco emisor
                if any(kw in cell_lower for kw in ["mercadopago", "mercado pago", "merpago"]):
                    bank = "Mercado Pago"
                elif "bbva" in cell_lower:
                    bank = "BBVA"
                elif "galicia" in cell_lower:
                    bank = "Galicia"
                elif "santander" in cell_lower:
                    bank = "Santander"
                elif "macro" in cell_lower:
                    bank = "Macro"
                elif "naranja" in cell_lower:
                    bank = "Naranja X"
                else:
                    bank = guessed_bank or "Banco"

                # Últimos 4 dígitos
                digits = re.search(r"\b(\d{4})\b", cell)
                card_last4 = digits.group(1) if digits else "XXXX"

                return bank, card_type, card_last4

    return "Banco", "Tarjeta", "XXXX"


def _detect_closing_date(rows: list) -> str:
    """Busca 'Fecha de cierre' y devuelve la fecha en formato YYYY-MM."""
    for i, row in enumerate(rows):
        for cell in row:
            if cell and isinstance(cell, str) and "fecha de cierre" in cell.lower():
                # La fecha está en la siguiente fila, misma columna
                if i + 1 < len(rows):
                    next_row = rows[i + 1]
                    for val in next_row:
                        if val and isinstance(val, str):
                            # Formato DD/MM/YYYY
                            m = re.search(r"(\d{2})/(\d{2})/(\d{4})", val)
                            if m:
                                d, mo, y = m.groups()
                                return f"{y}-{mo}"
                        elif val and isinstance(val, datetime):
                            return val.strftime("%Y-%m")
    return "Desconocida"


def _extract_transactions(rows: list) -> list[dict]:
    """
    Extrae transacciones de la sección del titular de la tarjeta.
    Ignora la sección de pagos y devoluciones.
    """
    transactions = []
    in_transactions = False

    for row in rows:
        first_cell = row[0] if row else None
        second_cell = row[1] if len(row) > 1 else None

        # Detectar encabezado de la sección de transacciones
        if (
            first_cell
            and isinstance(first_cell, str)
            and "fecha" in first_cell.lower()
            and second_cell
            and isinstance(second_cell, str)
            and "descripción" in second_cell.lower()
        ):
            # Solo activar si es la sección del titular (no de pagos)
            in_transactions = True
            continue

        if not in_transactions:
            continue

        # Fin de sección
        if first_cell and isinstance(first_cell, str) and "subtotal" in first_cell.lower():
            break

        # Fila de transacción: debe tener descripción y al menos un monto
        description = row[1] if len(row) > 1 else None
        if not description or not isinstance(description, str):
            continue

        # Fecha (puede ser None en cuotas subsiguientes)
        date = row[0]
        if isinstance(date, datetime):
            date = date.strftime("%d/%m/%Y")
        elif date:
            date = str(date)
        else:
            date = ""

        installments = str(row[2]) if len(row) > 2 and row[2] else ""
        amount_ars = _parse_amount(row[4] if len(row) > 4 else None)
        amount_usd = _parse_amount(row[5] if len(row) > 5 else None)

        # Ignorar pagos y devoluciones (montos negativos en la sección principal son raros,
        # pero los chequeamos igual)
        if description.lower().strip().startswith("su pago"):
            continue

        transactions.append(
            {
                "date": date,
                "description": description.strip(),
                "installments": installments.strip(),
                "amount_ars": amount_ars,
                "amount_usd": amount_usd,
            }
        )

    return transactions


def _parse_amount(value) -> str:
    """Convierte cualquier representación de monto a string limpio, o '' si no hay valor."""
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # Quitar símbolo de moneda y limpiar
        cleaned = value.replace("$", "").replace("U$S", "").replace("US$", "").strip()
        return cleaned if cleaned else ""
    return ""
