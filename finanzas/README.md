# Automatizador de resúmenes de tarjeta → Finanzas Tomi

Carga resúmenes de tarjeta (Excel o PDF) directamente en tu Google Sheet.

## Setup (una sola vez)

### 1. Instalá las dependencias

```bash
cd finanzas
pip install -r requirements.txt
```

### 2. Creá las credenciales OAuth de Google

1. Entrá a [Google Cloud Console](https://console.cloud.google.com/)
2. Creá un proyecto nuevo (o usá uno existente)
3. Activá la **Google Sheets API** y la **Google Drive API**
4. Andá a **Credentials → Create Credentials → OAuth client ID**
5. Tipo: **Desktop app**
6. Descargá el JSON y guardalo en esta carpeta como `credentials.json`

La primera vez que corras el script, se abre el browser para que autorices el acceso.
El token queda guardado en `token.json` (no lo subas a git).

### 3. Verificá que el Spreadsheet ID sea el correcto

El ID está hardcodeado en `sheets_updater.py`:
```
SPREADSHEET_ID = "1qrLkvC2oNFz42aeXxAnsE26LdJnNhk5cgqld-XZi82Q"
```

---

## Uso

```bash
# Un archivo Excel
python main.py resumen_visa.xlsx

# Un PDF
python main.py resumen_amex.pdf

# Varios archivos a la vez
python main.py *.xlsx *.pdf

# Ver resultado sin escribir en Sheets
python main.py resumen.xlsx --dry-run
```

---

## Qué genera en Google Sheets

Crea una hoja llamada **"Consumos Mayo 2026"** (o el mes del cierre) con:

| Sección | Contenido |
|---|---|
| **Transacciones** | Lista completa ordenada por categoría |
| **No identificadas** | Fondo naranja, info completa de la línea |
| **Resumen** | Total por categoría ($ y USD) |
| **TOTAL** | Suma general |

---

## Categorías

Las categorías coinciden exactamente con las de tu hoja "Gastos" en Finanzas Tomi:

**Fijos:** Vivienda/Alquiler · Servicios · Programas (Adobe) · IA · Servicios dig · Celular · Facultad · Créditos · Psicóloga

**Variables:** Comida/Supermercado · Salidas/Ocio · Salud/Farmacia · Ropa · Transporte · Arreglos casa · Tocadiscos

Para agregar reglas nuevas, editá `CATEGORY_RULES` en `categorizer.py`.

---

## Agregar un banco nuevo / formato nuevo

- **Excel:** El parser detecta automáticamente el formato estándar de Mercado Pago. Si tu banco exporta diferente, abrí un issue o editá `parser_excel.py`.
- **PDF:** El parser de PDF es más flexible pero puede necesitar ajustes por banco. Corré con `--dry-run` primero para verificar.
