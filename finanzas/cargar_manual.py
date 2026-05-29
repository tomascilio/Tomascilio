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
    # Facultad: Escuela Da Vinci MP $333.187 + cuotas Visa $17.275
    {"date": "", "description": "Facultad total", "installments": "", "amount_ars": "350462", "amount_usd": "", "category": "Facultad", "card": "Visa 3416 + MP Mastercard"},

    # Servicios: Telecentro AMEX $67.242,48
    {"date": "", "description": "Telecentro", "installments": "", "amount_ars": "67242.48", "amount_usd": "", "category": "Servicios (luz, gas, internet)", "card": "AMEX 7928"},

    # Celular: Tuenti MP $16.650
    {"date": "", "description": "Tuenti", "installments": "", "amount_ars": "16650", "amount_usd": "", "category": "Celular - Tuenti", "card": "MP Mastercard"},

    # Créditos: Plan V Visa $254.833,96
    {"date": "", "description": "Plan V crédito", "installments": "", "amount_ars": "254833.96", "amount_usd": "", "category": "Créditos", "card": "Visa 3416"},

    # Programas Adobe: Visa US$25,07
    {"date": "", "description": "Adobe", "installments": "", "amount_ars": "", "amount_usd": "25.07", "category": "Programas (Adobe)", "card": "Visa 3416"},

    # IA: Claude MP US$20 + Midjourney MP US$10
    {"date": "", "description": "IA total", "installments": "", "amount_ars": "", "amount_usd": "30", "category": "IA (CLAUDE, MIDJOU)", "card": "MP Mastercard"},

    # Servicios dig: Spotify US$1,31 + Apple US$4,99 + Apple US$2,99 + Google US$9,99 (Visa)
    {"date": "", "description": "Servicios digitales", "installments": "", "amount_ars": "", "amount_usd": "19.28", "category": "Servicios dig (spotify, nube, yt)", "card": "Visa 3416"},

    # ── GASTOS VARIABLES ──────────────────────────────────────
    # Comida: Coto MP $334.963,59
    {"date": "", "description": "Coto supermercado", "installments": "", "amount_ars": "334963.59", "amount_usd": "", "category": "Comida / Supermercado", "card": "MP Mastercard"},

    # Salidas: Venti Latam MP $80.500
    {"date": "", "description": "Venti Latam", "installments": "", "amount_ars": "80500", "amount_usd": "", "category": "Salidas / Ocio / Rest.", "card": "MP Mastercard"},

    # Ropa: Joyería Ororub Visa $15.466,22
    {"date": "", "description": "Joyeria Ororub", "installments": "", "amount_ars": "15466.22", "amount_usd": "", "category": "Ropa / Cuidado personal", "card": "Visa 3416"},

    # Otros variables: ML MP $43.990 + $22.822,49 + ML AMEX $26.099,66
    {"date": "", "description": "MercadoLibre total", "installments": "", "amount_ars": "92912.15", "amount_usd": "", "category": "Otros variables", "card": "MP Mastercard + AMEX 7928"},
]

summary = {
    "bank": "Resumen",
    "card_type": "Mayo",
    "card_last4": "2026",
    "closing_date": "2026-05",
    "transactions": transactions,
    "source_file": "carga_manual_mayo_2026",
}

print("Cargando valores finales en hoja Gastos...")
update_google_sheet(summary)
print("\nListo.")
