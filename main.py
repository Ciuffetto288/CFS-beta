#!/usr/bin/env python3
"""
Script principale di CFS - Crypto Fiscal System.

Interfaccia CLI per caricare i file CSV di exchange e generare report fiscali.
Uso: python main.py --file <path_to_csv> --prices <path_to_prices_json> [opzioni]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from cfs.core import FiscalCalculator, LIFOEngine
from cfs.models import Transaction
from cfs.parsers import YoungPlatformParser


DISCLAIMER_IT = """
AVVERTENZA LEGALE - DISCLAIMER

CFS (Crypto Fiscal System) è un software open-source a scopo INFORMATIVO E MATEMATICO.

NON COSTITUISCE CONSULENZA FISCALE PROFESSIONALE.

Lo sviluppatore e i collaboratori NON SI ASSUMONO ALCUNA RESPONSABILITÀ per:
  • Errori di calcolo o logici nel software
  • Sanzioni amministrative da parte dell'Agenzia delle Entrate
  • Omissioni o errori nella trasmissione dei dati alle autorità
  • Accertamenti fiscali conseguenti all'uso di questo software
  • Qualunque danno patrimoniale diretto o indiretto

L'UTENTE È ESCLUSIVAMENTE RESPONSABILE DI:
  • Verifica accurata di tutti i dati immessi e generati
  • Validazione del report con un consulente fiscale autorizzato
  • Accuratezza della dichiarazione presentata all'Agenzia delle Entrate
  • Conformità ai requisiti normativi attuali

USO: Consultare sempre un commercialista prima di presentare la dichiarazione.
"""

DISCLAIMER_EN = """
LEGAL NOTICE - DISCLAIMER

CFS (Crypto Fiscal System) is open-source software for INFORMATIONAL AND MATHEMATICAL purposes only.

IT DOES NOT CONSTITUTE PROFESSIONAL TAX ADVICE.

The developer and contributors ASSUME NO LIABILITY for:
  • Calculation or logical errors in the software
  • Administrative penalties from tax authorities
  • Omissions or errors in data transmission to authorities
  • Tax audits resulting from using this software
  • Any direct or indirect financial damage

THE USER IS SOLELY RESPONSIBLE FOR:
  • Accurate verification of all input and generated data
  • Validation of reports with an authorized tax consultant
  • Accuracy of the tax return filed with authorities
  • Compliance with current regulatory requirements

USE: Always consult a tax professional before filing your tax return.
"""

DISCLAIMER = """
╔════════════════════════════════════════════════════════════════════════════╗
║  CFS v0.2.0 - Crypto Fiscal System  |  2026 Italian Tax Reporting Tool   ║
╚════════════════════════════════════════════════════════════════════════════╝

""" + DISCLAIMER_IT + "\n---\n\n" + DISCLAIMER_EN + "\n"


def print_disclaimer(lang: str = "bi"):
    """Print disclaimer in requested language (it, en, or bi=bilingual)."""
    if lang == "it":
        print(DISCLAIMER_IT)
    elif lang == "en":
        print(DISCLAIMER_EN)
    else:
        print(DISCLAIMER)


def load_csv_file(file_path: str, exchange: str = "young_platform") -> list:
    """Load transaction CSV from specified exchange."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if exchange.lower() == "young_platform":
        return YoungPlatformParser.parse_file(str(file_path))
    else:
        raise ValueError(f"Exchange '{exchange}' not supported. Currently supported: young_platform")


def load_year_end_prices(prices_file: Optional[str]) -> Dict[str, float]:
    """Load end-of-year prices from JSON file. Returns empty dict if file not provided."""
    if not prices_file:
        return {}

    prices_file = Path(prices_file)
    if not prices_file.exists():
        raise FileNotFoundError(f"Prices file not found: {prices_file}")

    try:
        with open(prices_file, "r", encoding="utf-8") as f:
            prices = json.load(f)
        return prices
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in prices file: {e}")


def save_report(report: Dict, output_path: str) -> None:
    """Save fiscal report as JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nReport saved to: {output_path}")


def format_currency(value: float, decimals: int = 2) -> str:
    """Formatta un valore come valuta EUR."""
    return f"€ {value:,.{decimals}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def print_report_summary(report: Dict, lang: str = "bi") -> None:
    """Print fiscal report summary in requested language."""
    summary = report.get("summary", {})
    capital_gains = report.get("capital_gains", {})
    patrimony = report.get("patrimony", {})

    if lang in ("it", "bi"):
        print("\n" + "=" * 80)
        print("QUADRO RT/W - PLUSVALENZE E MINUSVALENZE")
        print("-" * 80)
        print(f"  Guadagni totali:             {format_currency(capital_gains.get('total_gains', 0))}")
        print(f"  Perdite totali:              {format_currency(capital_gains.get('total_losses', 0))}")
        print(f"  Perdite deducibili:          {format_currency(capital_gains.get('max_deductible_loss', 0))}")
        print(f"  Guadagno netto imponibile:   {format_currency(capital_gains.get('net_gain', 0))}")
        print(f"  Aliquota media:              {capital_gains.get('tax_rate_default', 0.26) * 100:.0f}%")
        print(f"  Imposte dovute:              {format_currency(capital_gains.get('tax_amount', 0))}")
        print()
        
        print("QUADRO RW - MONITORAGGIO CAMBI")
        print("-" * 80)
        print(f"  Valore complessivo holding:  {format_currency(patrimony.get('total_value', 0))}")
        if patrimony.get("is_taxable"):
            print(f"  Aliquota imposta patrimoniale: {patrimony.get('tax_rate', 0.002) * 100:.2f}%")
            print(f"  Imposte patrimoniali dovute:   {format_currency(patrimony.get('tax_amount', 0))}")
        else:
            print(f"  Patrimonio non tassabile (valore <= soglia)")
        print()

        holdings = patrimony.get("holdings", {})
        if holdings:
            print("  Holdings al 31/12:")
            for asset, data in holdings.items():
                qty = data.get("quantity", 0)
                value = data.get("value_eur", 0)
                if qty > 0:
                    print(f"    {asset:10s}: {qty:15.8f} units = {format_currency(value)}")
        print()

        print("=" * 80)
        total_tax = report.get("total_tax_liability", 0)
        print(f"IMPOSTE TOTALI STIMATE:       {format_currency(total_tax)}")
        print("=" * 80)
        print(f"\nTransazioni elaborate:       {len(capital_gains.get('records', []))}")
        print(f"Anno fiscale:                {report.get('tax_year', 'N/A')}")
        print()

    if lang in ("en", "bi"):
        print("\n" + "=" * 80)
        print("QUADRO RT/W - CAPITAL GAINS AND LOSSES")
        print("-" * 80)
        print(f"  Total gains:                 {format_currency(capital_gains.get('total_gains', 0))}")
        print(f"  Total losses:                {format_currency(capital_gains.get('total_losses', 0))}")
        print(f"  Deductible losses:           {format_currency(capital_gains.get('max_deductible_loss', 0))}")
        print(f"  Net taxable gain:            {format_currency(capital_gains.get('net_gain', 0))}")
        print(f"  Average tax rate:            {capital_gains.get('tax_rate_default', 0.26) * 100:.0f}%")
        print(f"  Tax due:                     {format_currency(capital_gains.get('tax_amount', 0))}")
        print()

        print("QUADRO RW - HOLDINGS MONITORING")
        print("-" * 80)
        print(f"  Total portfolio value:       {format_currency(patrimony.get('total_value', 0))}")
        if patrimony.get("is_taxable"):
            print(f"  Patrimonial tax rate:        {patrimony.get('tax_rate', 0.002) * 100:.2f}%")
            print(f"  Patrimonial tax due:         {format_currency(patrimony.get('tax_amount', 0))}")
        else:
            print(f"  Patrimony not taxable (value <= threshold)")
        print()

        holdings = patrimony.get("holdings", {})
        if holdings:
            print("  Holdings at 31/12:")
            for asset, data in holdings.items():
                qty = data.get("quantity", 0)
                value = data.get("value_eur", 0)
                if qty > 0:
                    print(f"    {asset:10s}: {qty:15.8f} units = {format_currency(value)}")
        print()

        print("=" * 80)
        total_tax = report.get("total_tax_liability", 0)
        print(f"TOTAL ESTIMATED TAX:         {format_currency(total_tax)}")
        print("=" * 80)
        print(f"\nTransactions processed:      {len(capital_gains.get('records', []))}")
        print(f"Tax year:                    {report.get('tax_year', 'N/A')}")
        print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CFS - Crypto Fiscal System v0.2.0 | Italian crypto tax calculator (2026 rules)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --file transactions.csv
  python main.py --file transactions.csv --prices prices_31_12_2026.json
  python main.py --file transactions.csv --prices prices.json --output report.json
  python main.py --file transactions.csv --lang en

Tax year: 2026 | Rules: 26% EUR stablecoins, 33% crypto | Patrimonial tax: 0.2% (no threshold)
        """,
    )

    parser.add_argument("--file", type=str, required=True, help="Path to CSV file (Young Platform export)")
    parser.add_argument("--exchange", type=str, default="young_platform", help="Exchange source (default: young_platform)")
    parser.add_argument("--prices", type=str, help="Path to JSON file with 31/12 prices per asset")
    parser.add_argument("--config", type=str, help="Path to config.json with custom fiscal parameters")
    parser.add_argument("--output", type=str, help="Path to save full report as JSON")
    parser.add_argument("--lang", type=str, choices=["it", "en", "bi"], default="bi", 
                       help="Language: it=Italian, en=English, bi=Bilingual (default)")
    parser.add_argument("--no-disclaimer", action="store_true", help="Skip disclaimer prompt")

    args = parser.parse_args()

    if not args.no_disclaimer:
        print_disclaimer(args.lang)
        if args.lang == "en":
            response = input("\nAccept terms and proceed? (yes/no): ").strip().lower()
        else:
            response = input("\nAccetti i termini e desideri proseguire? (yes/no): ").strip().lower()
        if response != "yes":
            sys.exit(0)

    try:
        # Load CSV transactions
        transactions = load_csv_file(args.file, args.exchange)

        # Sort by timestamp for chronological processing
        transactions_sorted = sorted(transactions, key=lambda t: t.timestamp)

        # Process with LIFO engine
        lifo = LIFOEngine()
        lifo.process_transactions(transactions_sorted)

        # Load end-of-year prices
        year_end_prices = load_year_end_prices(args.prices)

        # Calculate taxes and generate report
        fiscal_calc = FiscalCalculator(args.config)
        report = fiscal_calc.generate_fiscal_report(lifo, year_end_prices)

        # Display results
        print_report_summary(report, args.lang)

        # Save detailed report if requested
        if args.output:
            save_report(report, args.output)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
