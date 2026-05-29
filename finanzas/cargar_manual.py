"""
Carga los valores correctos en la hoja Gastos de Finanzas Tomi.
REEMPLAZA el valor existente — no suma encima.
Correr: python3 cargar_manual.py
"""

import sys
sys.path.insert(0, '.')
from sheets_updater import update_google_sheet

# Valores finales correctos (suma de Excel + screenshots de MP)
# Visa 3416 + AMEX 7928 + Mercado Pago Mastercard
transactions = [
    # ── GASTOS FIJOS ──────────────────────────────────────────
    # Facultad: Escuela Da Vinci screenshot $333.187 + cuotas Visa $17.275
    {"date": "", "description": "Facultad total", "installments": "", "amount_ars": "350462", "amount_usd": "", "category": "Facultad"},

    # Servicios: Telecentro AMEX $67.242,48
    {"date": "", "description": "Servicios internet", "installments": "", "amount_ars": "67242.48", "amount_usd": "", "category": "Servicios (luz, gas, internet)"},

    # Celular: Tuenti screenshot $16.650
    {"date": "", "description": "Tuenti", "installments": "", "amount_ars": "16650", "amount_usd": "", "category": "Celular - Tuenti"},

    # Créditos: Plan V Visa $254.833,96
    {"date": "", "description": "Plan V credito", "installments": "", "amount_ars": "254833.96", "amount_usd": "", "category": "Créditos"},

    # Programas Adobe: Visa US$25,07
    {"date": "", "description": "Adobe", "installments": "", "amount_ars": "", "amount_usd": "25.07", "category": "Programas (Adobe)"},

    # IA: Claude US$20 + Midjourney US$10
    {"date": "", "description": "IA total", "installments": "", "amount_ars": "", "amount_usd": "30", "category": "IA (CLAUDE, MIDJOU)"},

    # Servicios dig: Spotify US$1,31 + Apple US$4,99 + Apple US$2,99 + Google US$9,99
    {"date": "", "description": "Servicios digitales", "installments": "", "amount_ars": "", "amount_usd": "19.28", "category": "Servicios dig (spotify, nube, yt)"},

    # ── GASTOS VARIABLES ──────────────────────────────────────
    # Comida: Coto screenshot $334.963,59
    {"date": "", "description": "Coto supermercado", "installments": "", "amount_ars": "334963.59", "amount_usd": "", "category": "Comida / Supermercado"},

    # Salidas: Venti Latam $80.500
    {"date": "", "description": "Venti Latam", "installments": "", "amount_ars": "80500", "amount_usd": "", "category": "Salidas / Ocio / Rest."},

    # Ropa: Joyería Ororub Visa $15.466,22
    {"date": "", "description": "Joyeria Ororub", "installments": "", "amount_ars": "15466.22", "amount_usd": "", "category": "Ropa / Cuidado personal"},

    # Otros variables: MercadoLibre x2 screenshot $43.990 + $22.822,49 + ML AMEX $26.099,66
    {"date": "", "description": "MercadoLibre total", "installments": "", "amount_ars": "92912.15", "amount_usd": "", "category": "Otros variables"},
]

summary = {
    "bank": "Mercado Pago",
    "card_type": "Mastercard",
    "card_last4": "TOTAL",
    "closing_date": "2026-05",
    "transactions": transactions,
    "source_file": "carga_manual_mayo_2026",
}

print("Cargando valores finales en hoja Gastos...")
update_google_sheet(summary)
print("\nListo.")
