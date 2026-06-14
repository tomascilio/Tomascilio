"""
Automatizador de resúmenes de tarjeta → Google Sheets (Finanzas Tomi o Mara)

Uso:
    python main.py archivo.xlsx
    python main.py resumen_visa.pdf --profile mara
    python main.py *.xlsx --dry-run

Qué hace:
    1. Detecta banco, tarjeta y fecha de cierre del archivo
    2. Extrae y categoriza cada transacción
    3. Crea/reemplaza una hoja "Consumos [Mes Año]" en el sheet del perfil con:
       - Tabla de transacciones categorizadas
       - Sección "Transacciones no identificadas" con la info completa
       - Resumen agrupado por categoría al final
"""

import sys
import argparse
from pathlib import Path

from parser_excel import parse_excel
from parser_pdf import parse_pdf
from categorizer import categorize_transactions
from sheets_updater import update_google_sheet
from profiles import get_profile, DEFAULT_PROFILE


def main():
    parser = argparse.ArgumentParser(description="Cargá resúmenes de tarjeta en Google Sheets")
    parser.add_argument("files", nargs="+", help="Archivos .xlsx o .pdf a procesar")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostrá el resultado sin escribir en Google Sheets",
    )
    parser.add_argument(
        "--profile",
        default=DEFAULT_PROFILE,
        help="Perfil a usar: 'tomi' (default) o 'mara'",
    )
    args = parser.parse_args()

    profile = get_profile(args.profile)
    print(f"Perfil: {args.profile}")

    all_transactions = []

    for filepath in args.files:
        path = Path(filepath)
        if not path.exists():
            print(f"[ERROR] No se encontró el archivo: {filepath}")
            sys.exit(1)

        print(f"\nProcesando: {path.name}")

        if path.suffix.lower() in (".xlsx", ".xls"):
            summary = parse_excel(path)
        elif path.suffix.lower() == ".pdf":
            summary = parse_pdf(path)
        else:
            print(f"[ERROR] Formato no soportado: {path.suffix} (usá .xlsx o .pdf)")
            sys.exit(1)

        print(f"  Banco/tarjeta : {summary['bank']} {summary['card_type']} terminada en {summary['card_last4']}")
        print(f"  Cierre        : {summary['closing_date']}")
        print(f"  Transacciones : {len(summary['transactions'])}")

        categorized = categorize_transactions(summary["transactions"])
        summary["transactions"] = categorized
        all_transactions.append(summary)

    if args.dry_run:
        _print_dry_run(all_transactions)
    else:
        for summary in all_transactions:
            update_google_sheet(summary, profile=profile)
            print(f"\n✓ Hoja actualizada ({args.profile})")


def _print_dry_run(summaries):
    print("\n" + "=" * 60)
    print("DRY RUN — no se escribió nada en Google Sheets")
    print("=" * 60)
    for s in summaries:
        print(f"\n[{s['bank']} {s['card_type']} {s['card_last4']}] — {s['closing_date']}")
        for t in s["transactions"]:
            cat = t.get("category", "⚠ No identificada")
            print(f"  {t['date']:<12} {t['description']:<35} {t.get('amount_ars', ''):>15}  → {cat}")


if __name__ == "__main__":
    main()
