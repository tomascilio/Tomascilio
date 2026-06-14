"""
Carga los valores de Mayo 2026 en la hoja Gastos de Finanzas Mara.
Mastercard Black + Visa Signature (BBVA).
Correr: python3 cargar_manual_mara.py
"""

import sys
sys.path.insert(0, '.')
from sheets_updater import update_google_sheet
from profiles import get_profile

# Visa Signature + Mastercard Black — cierre 28 May 26
transactions = [
    # ── ROPA (cuotas de meses anteriores en Visa) ─────────────
    {"date": "", "description": "Ropa cuotas total", "installments": "", "amount_ars": "184799.89", "amount_usd": "", "category": "Ropa / Cuidado personal", "card": "Visa Signature"},

    # ── RAPPI ─────────────────────────────────────────────────
    # Mastercard: Rappi $54.256 + $30.190 = $84.446
    # Visa: PedidosYa Rapanui $8.189 + propina $600 + Mostaza $42.829 - dev $13.479,89 + propina $750 = $38.888,11
    {"date": "", "description": "Rappi / PedidosYa total", "installments": "", "amount_ars": "123334.11", "amount_usd": "", "category": "Rappi", "card": "Mastercard + Visa Signature"},

    # ── TRANSPORTE ────────────────────────────────────────────
    # Cabify x2: $10.130,63 + $7.707,43 = $17.838,06
    {"date": "", "description": "Cabify total", "installments": "", "amount_ars": "17838.06", "amount_usd": "", "category": "Transporte fijo (SUBE)", "card": "Mastercard"},

    # ── SALIDAS / OCIO ────────────────────────────────────────
    # Hertz Argentina $180.925
    {"date": "", "description": "Hertz auto", "installments": "", "amount_ars": "180925", "amount_usd": "", "category": "Salidas / Ocio / Rest.", "card": "Visa Signature"},

    # ── PERROS ────────────────────────────────────────────────
    # Capricho Animal cuota 1/3 $29.326,68
    {"date": "", "description": "Capricho Animal (1/3)", "installments": "1 de 3", "amount_ars": "29326.68", "amount_usd": "", "category": "Perros", "card": "Visa Signature"},

    # ── IA ────────────────────────────────────────────────────
    {"date": "", "description": "Claude AI", "installments": "", "amount_ars": "", "amount_usd": "20", "category": "IA (CLAUDE, MIDJOU)", "card": "Visa Signature"},

    # ── SERVICIOS DIGITALES ───────────────────────────────────
    # Apple x3: US$11,19 + US$6,99 + US$9,99 = US$28,17
    # Mubi: US$59,93 | LinkedIn: US$2,61
    {"date": "", "description": "Servicios dig total", "installments": "", "amount_ars": "", "amount_usd": "90.71", "category": "Servicios dig (spotify, nube, yt)", "card": "Visa Signature"},

    # ── OTROS VARIABLES ───────────────────────────────────────
    # ML $8.990 + 3M3A $51.500 + Simonewege $71.280 + MeryReservas $30.000
    # + CCA $19.635 + ValentinRamall $320.970 + Distrib.Indep $40.111,11 + BigBox $27.000
    {"date": "", "description": "Otros variables total", "installments": "", "amount_ars": "569486.11", "amount_usd": "", "category": "Otros variables", "card": "Visa Signature"},
]

profile = get_profile("mara")

summary = {
    "bank": "BBVA",
    "card_type": "Mayo",
    "card_last4": "2026",
    "closing_date": "2026-05",
    "transactions": transactions,
    "source_file": "carga_manual_mara_mayo_2026",
}

print("Cargando valores Mayo 2026 en Finanzas Mara...")
update_google_sheet(summary, profile=profile)
print("\nListo.")
