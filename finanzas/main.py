"""
Automatizador de resúmenes de tarjeta → Finanzas Tomi (Google Sheets)

Uso:
    python main.py archivo.xlsx
    python main.py resumen_visa.pdf
    python main.py *.xlsx          (varios archivos)

Qué hace:
    1. Detecta banco, tarjeta y fecha de cierre del archivo
    2. Extrae y categoriza cada transacción
    3. Crea/reemplaza una hoja "Consumos [Mes Año]" en Finanzas Tomi con:
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


def main():
    parser = argparse.ArgumentParser(description="Cargá resúmenes de tarjeta en Finanzas Tomi")
    parser.add_argument("files", nargs="+", help="Archivos .xlsx o .pdf a procesar")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostrá el resultado sin escribir en Google Sheets",
    )
    args = parser.parse_args()

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
            update_google_sheet(summary)
            print(f"\n✓ Hoja actualizada en Finanzas Tomi")


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
