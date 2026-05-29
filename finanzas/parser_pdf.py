"""
Parser para resúmenes de tarjeta en formato PDF.
Usa pdfplumber para extraer texto y detecta el formato de tabla.

Soporta los formatos más comunes de bancos argentinos:
  - Mercado Pago (Visa / Mastercard / AMEX)
  - BBVA, Galicia, Santander, Macro (formato tabla estándar)
"""

import re
from pathlib import Path
from datetime import datetime

try:
    import pdfplumber
except ImportError:
    raise ImportError("Instalá pdfplumber: pip install pdfplumber")


# Patrón para líneas de transacción: DD/MM/YYYY o DD/MM/YY al inicio
_DATE_RE = re.compile(r"^(\d{2}/\d{2}/\d{2,4})")
# Patrones de monto: $1.234,56 o U$S12,34
_ARS_RE = re.compile(r"\$([\d.,]+)")
_USD_RE = re.compile(r"U\$S\s*([\d.,]+)")
# Cuotas: "3 de 6" o "3/6"
_INSTALLMENT_RE = re.compile(r"\b(\d+)\s*(?:de|/)\s*(\d+)\b")


def parse_pdf(path: Path) -> dict:
    with pdfplumber.open(path) as pdf:
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    bank, card_type, card_last4 = _detect_card(full_text)
    closing_date = _detect_closing_date(full_text)
    transactions = _extract_transactions(full_text)

    return {
        "bank": bank,
        "card_type": card_type,
        "card_last4": card_last4,
        "closing_date": closing_date,
        "transactions": transactions,
        "source_file": path.name,
    }


def _detect_card(text: str) -> tuple[str, str, str]:
    text_lower = text.lower()

    if "american express" in text_lower or "amex" in text_lower:
        card_type = "American Express"
    elif "visa" in text_lower:
        card_type = "Visa"
    elif "mastercard" in text_lower:
        card_type = "Mastercard"
    else:
        card_type = "Tarjeta"

    if "mercado pago" in text_lower or "mercadopago" in text_lower:
        bank = "Mercado Pago"
    elif "bbva" in text_lower:
        bank = "BBVA"
    elif "galicia" in text_lower:
        bank = "Galicia"
    elif "santander" in text_lower:
        bank = "Santander"
    elif "macro" in text_lower:
        bank = "Macro"
    elif "naranja" in text_lower:
        bank = "Naranja X"
    else:
        bank = "Banco"

    digits = re.search(r"terminada en (\d{4})|N°\s*\d{12}(\d{4})|\b(\d{4})\b", text)
    if digits:
        card_last4 = next(g for g in digits.groups() if g)
    else:
        card_last4 = "XXXX"

    return bank, card_type, card_last4


def _detect_closing_date(text: str) -> str:
    # Buscar "Fecha de cierre" seguido de fecha
    m = re.search(
        r"[Ff]echa\s+de\s+cierre[:\s]+(\d{2}/\d{2}/\d{4})",
        text,
    )
    if m:
        d, mo, y = m.group(1).split("/")
        return f"{y}-{mo}"

    # Buscar "Período" o "Período de facturación"
    m = re.search(r"[Pp]er[íi]odo.*?(\d{2}/\d{2}/\d{4})", text)
    if m:
        d, mo, y = m.group(1).split("/")
        return f"{y}-{mo}"

    return "Desconocida"


def _extract_transactions(text: str) -> list[dict]:
    """
    Extrae transacciones del texto del PDF línea por línea.
    Busca líneas que empiecen con fecha y contengan montos.
    """
    transactions = []
    lines = text.split("\n")
    in_payments_section = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detectar sección de pagos (omitir)
        if re.search(r"pago.*tarjeta|devoluciones?", line.lower()):
            in_payments_section = True
        if re.search(r"consumos?|compras?|detalle", line.lower()):
            in_payments_section = False

        if in_payments_section:
            continue

        # Detectar línea de transacción
        date_match = _DATE_RE.match(line)
        if not date_match:
            continue

        date_str = date_match.group(1)
        # Normalizar año de 2 a 4 dígitos
        parts = date_str.split("/")
        if len(parts[2]) == 2:
            parts[2] = "20" + parts[2]
        date_str = "/".join(parts)

        # Extraer montos
        ars_match = _ARS_RE.search(line)
        usd_match = _USD_RE.search(line)
        amount_ars = ars_match.group(1) if ars_match else ""
        amount_usd = usd_match.group(1) if usd_match else ""

        # Extraer cuotas
        inst_match = _INSTALLMENT_RE.search(line)
        installments = f"{inst_match.group(1)} de {inst_match.group(2)}" if inst_match else ""

        # Descripción: todo lo que está entre la fecha y el primer monto
        desc_end = ars_match.start() if ars_match else (usd_match.start() if usd_match else len(line))
        description = line[date_match.end():desc_end].strip()
        # Limpiar número de comprobante (suele ser numérico al final)
        description = re.sub(r"\s+\d{8,}\s*$", "", description).strip()

        if not description:
            continue

        # Ignorar pagos
        if re.search(r"su pago|pago recib", description.lower()):
            continue

        transactions.append(
            {
                "date": date_str,
                "description": description,
                "installments": installments,
                "amount_ars": amount_ars,
                "amount_usd": amount_usd,
            }
        )

    return transactions
