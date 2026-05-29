"""
Carga manual de transacciones desde screenshots de Mercado Pago - Mayo 2026.
Correr una sola vez: python3 cargar_manual.py
"""

import sys
sys.path.insert(0, '.')
from sheets_updater import update_google_sheet

transactions = [
    {"date": "27/05/2026", "description": "Mercado Libre",   "installments": "", "amount_ars": "43990",     "amount_usd": "", "category": "Otros variables"},
    {"date": "22/05/2026", "description": "Mercado Libre",   "installments": "", "amount_ars": "22822.49",  "amount_usd": "", "category": "Otros variables"},
    {"date": "18/05/2026", "description": "Claude Ai",       "installments": "", "amount_ars": "",          "amount_usd": "20", "category": "IA (CLAUDE, MIDJOU)"},
    {"date": "18/05/2026", "description": "Escuela Da Vinci","installments": "", "amount_ars": "333187",    "amount_usd": "", "category": "Facultad"},
    {"date": "15/05/2026", "description": "Coto",            "installments": "", "amount_ars": "334963.59", "amount_usd": "", "category": "Comida / Supermercado"},
    {"date": "14/05/2026", "description": "Venti Latam",     "installments": "", "amount_ars": "80500",     "amount_usd": "", "category": "Salidas / Ocio / Rest."},
    {"date": "09/05/2026", "description": "Midjourney Inc.", "installments": "", "amount_ars": "",          "amount_usd": "10", "category": "IA (CLAUDE, MIDJOU)"},
    {"date": "09/05/2026", "description": "Tuenti",          "installments": "", "amount_ars": "16650",     "amount_usd": "", "category": "Celular - Tuenti"},
]

summary = {
    "bank": "Mercado Pago",
    "card_type": "Mastercard",
    "card_last4": "MP",
    "closing_date": "2026-05",
    "transactions": transactions,
    "source_file": "screenshot_manual",
}

print("Cargando transacciones manuales en Finanzas Tomi...")
update_google_sheet(summary)
print("\nListo.")
