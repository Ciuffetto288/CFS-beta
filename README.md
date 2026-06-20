# CFS - Crypto Fiscal System

**Version:** 0.2.0 | **Last Updated:** June 2026 | **Status:** Production Ready

---

## Overview

**Crypto Fiscal System (CFS)** is an open-source Python application designed to calculate capital gains, losses, and patrimonial taxes on cryptocurrency transactions according to **Italian tax regulations (2026)**. 

CFS implements the **LIFO (Last In, First Out)** algorithm for capital gains calculation and generates compliant tax reports for Italian fiscal authorities (Agenzia delle Entrate), specifically for:

- **Quadro RW** - Monitoring of cryptocurrency holdings at year-end (31/12)
- **Quadro RT/W** - Capital gains and losses from cryptocurrency disposals

### Key Features

- ✅ **LIFO Algorithm Implementation**: Accurate cost basis tracking and capital gain/loss matching
- ✅ **2026 Italian Tax Compliance**: Differentiated tax rates, updated thresholds, bilingual support
- ✅ **Differentiated Tax Rates**:
  - **26%** on E-Money Tokens (EUR-anchored stablecoins: USDC, EUROC, EURe, EURA, USDT, DAI)
  - **33%** on Bitcoin and other cryptocurrencies
- ✅ **Patrimonial Tax**: 0.2% on ALL holdings from EUR 0 (no exemption threshold)
- ✅ **Loss Deduction**: Up to EUR 48,000 per fiscal year
- ✅ **Young Platform Integration**: Native CSV parser for Young Platform exchange exports
- ✅ **Multi-Language CLI**: Bilingual interface (Italian/English)
- ✅ **JSON-Based Configuration**: Easy normative updates for future tax year changes
- ✅ **Comprehensive Reporting**: Detailed capital gains records, holdings snapshots, tax liability summaries

---

## Legal Notice & Disclaimer

**IMPORTANT:** CFS is an **informational and mathematical tool only** and does NOT constitute professional tax advice.

**CFS Developers assume NO LIABILITY for:**
- Calculation or logical errors in the software
- Administrative penalties from tax authorities
- Omissions or data transmission errors
- Tax audits resulting from this software's use
- Any direct or indirect financial damages

**Users are SOLELY RESPONSIBLE for:**
- Verifying all input and generated data
- Validating reports with an authorized tax consultant (commercialista)
- Accuracy of tax returns filed with authorities
- Compliance with current Italian tax regulations

**ALWAYS CONSULT A TAX PROFESSIONAL BEFORE FILING YOUR RETURN.**

---

## System Requirements

- **Python**: 3.10 or higher
- **Operating System**: macOS, Linux, or Windows
- **Dependencies**: See [requirements.txt](requirements.txt)
- **RAM**: Minimum 512 MB (recommended 1 GB for large portfolios)
- **Storage**: ~100 MB for application and data

---

## Installation

### Option 1: Using Git (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/crypto-fiscal-system.git
cd crypto-fiscal-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Direct Download

1. Download the repository as ZIP
2. Extract to your desired location
3. Create and activate a virtual environment as shown above
4. Install dependencies: `pip install -r requirements.txt`

---

## Quick Start

### Basic Usage

```bash
python main.py --file transactions.csv
```

### Full Report with Prices and Output

```bash
python main.py \
  --file transactions.csv \
  --prices prices_31_12_2026.json \
  --output report_2026.json
```

### Bilingual Output

```bash
# Italian output
python main.py --file transactions.csv --lang it

# English output
python main.py --file transactions.csv --lang en

# Bilingual output (default)
python main.py --file transactions.csv --lang bi
```

### Custom Configuration

```bash
python main.py \
  --file transactions.csv \
  --config custom_config.json \
  --output report.json
```

---

## Input Files Format

### CSV Transactions (Young Platform Export)

Export your Young Platform transaction history as CSV with the following columns:

```
Date,Time,Type,Asset,Quantity,Price (EUR),Fee (EUR),Total (EUR)
2026-01-15,10:30:00,BUY,BTC,0.5,42000.00,5.00,21005.00
2026-01-20,14:45:30,BUY,ETH,2.0,2500.00,2.00,5002.00
2026-02-10,09:15:00,SELL,BTC,0.25,45000.00,3.00,11247.00
```

**Supported Transaction Types:**
- `BUY` - Purchase transaction
- `SELL` - Sale/disposal transaction
- `DEPOSIT` - Incoming transfer (from external wallet/airdrop)
- `WITHDRAW` - Outgoing transfer (to external wallet)
- `TRANSFER_IN` - Internal transfer received
- `TRANSFER_OUT` - Internal transfer sent

### Year-End Prices (JSON)

Create a JSON file with cryptocurrency prices at 31 December (for Quadro RW valuation):

```json
{
  "BTC": 48500.00,
  "ETH": 2850.50,
  "USDC": 1.00,
  "EUROC": 1.00,
  "DAI": 0.98
}
```

### Custom Configuration (Optional)

Override default fiscal parameters by creating a custom `config.json`:

```json
{
  "tax_year": 2026,
  "capital_gains_tax_rates": {
    "stablecoin_eur": 0.26,
    "cryptocurrency": 0.33
  },
  "capital_gains_default_rate": 0.26,
  "patrimony_tax_rate": 0.002,
  "patrimony_tax_threshold": 0,
  "max_loss_deduction": 48000,
  "enable_logging": false
}
```

---

## Output Report

CFS generates a comprehensive JSON report containing:

### Capital Gains (Quadro RT/W)
- Total gains and losses
- Net taxable gain
- Detailed transaction records
- Tax liability calculation

### Holdings Monitoring (Quadro RW)
- Asset-by-asset portfolio value
- Holdings at 31/12 with unit prices
- Patrimonial tax calculation

### Tax Summary
- Total capital gains tax
- Patrimonial tax
- **Total tax liability**

Example output structure:
```json
{
  "tax_year": 2026,
  "summary": {
    "total_transactions": 42,
    "total_disposals": 15,
    "total_holdings_value": 125500.00
  },
  "capital_gains": {
    "total_gains": 8500.00,
    "total_losses": 1200.00,
    "net_gain": 7300.00,
    "tax_rate_default": 0.26,
    "tax_amount": 1898.00,
    "records": [...]
  },
  "patrimony": {
    "total_value": 125500.00,
    "is_taxable": true,
    "tax_rate": 0.002,
    "tax_amount": 251.00,
    "holdings": {...}
  },
  "total_tax_liability": 2149.00
}
```

---

## Project Architecture

### Directory Structure

```
crypto-fiscal-system/
├── README.md                    # Documentation
├── ARCHITECTURE.md              # Technical design
├── CONTRIBUTING.md              # Contribution guidelines
├── GETTING_STARTED.md          # Setup guide
├── requirements.txt            # Python dependencies
├── main.py                     # CLI entry point
├── config/
│   └── config.json            # Fiscal parameters
└── cfs/
    ├── __init__.py
    ├── models/                # Data models
    │   ├── transaction.py
    │   ├── models.py
    │   └── __init__.py
    ├── parsers/              # Exchange parsers
    │   ├── young_platform.py
    │   └── __init__.py
    ├── core/                 # Tax calculation engine
    │   ├── fiscal_calculator.py
    │   ├── lifo_engine.py
    │   └── __init__.py
    └── utils/               # Utilities
        ├── validators.py
        └── __init__.py
```

### Core Components

| Component | Purpose |
|-----------|---------|
| `LIFOEngine` | Implements LIFO algorithm for capital gain matching |
| `FiscalCalculator` | Calculates tax liability (Quadro RT/W and RW) |
| `YoungPlatformParser` | Parses Young Platform CSV exports |
| `Transaction` | Standardized transaction data model |
| `CapitalGainRecord` | Capital gain/loss record model |

---

## Italian Tax Rules (2026)

### Capital Gains Tax (Imposta sui Redditi Diversi)

**Tax Rates by Asset Type:**
- **E-Money Tokens (EUR-anchored stablecoins)**: 26%
  - Includes: USDC, EUROC, EURe, EURA, USDT, DAI
- **All other cryptocurrencies** (including Bitcoin, Ethereum, etc.): 33%

**Deduction Rules:**
- Capital losses can offset capital gains
- Maximum annual loss deduction: **EUR 48,000**
- Unused losses cannot be carried forward

**Capital Gains Exemption:**
- **REMOVED in 2026** (previously EUR 2,000)
- Taxation applies **from the first cent** (dal primo centesimo)

### Patrimonial Tax (Imposta Patrimoniale)

**Tax Details:**
- Rate: **0.2%** on ALL cryptocurrency holdings
- Calculation date: **31 December**
- **Threshold: REMOVED in 2026** (previously EUR 51,646)
- Applies to: **All holdings from EUR 0 and above** (linear, no exemption)

**Reporting:**
- Quadro RW (Monitoraggio Cambi)
- Initial and final holding values
- Asset-by-asset breakdown

### Filing Requirements

- **Form**: Dichiarazione dei Redditi (Italian tax return)
- **Quadri**: RW and RT/W sections
- **Deadline**: Depends on filing status (typically June 30)
- **Currency**: EUR (convert foreign prices to EUR using official rates)

---

## Usage Examples

### Example 1: Complete Tax Calculation

```bash
python main.py \
  --file young_platform_2026.csv \
  --prices prices_31_12_2026.json \
  --output tax_report_2026.json \
  --lang bi
```

### Example 2: Check Configuration

Edit `config/config.json` to verify:
- Tax year is set to `2026`
- Tax rates are correct
- Thresholds are `0` (not 51,646)

### Example 3: Generate Italian Report Only

```bash
python main.py --file transactions.csv --lang it
```

---

## Troubleshooting

### Issue: "File not found: transactions.csv"
**Solution**: Ensure the CSV file path is correct and the file exists in the specified location.

### Issue: "Exchange 'unknown' not supported"
**Solution**: Only Young Platform is currently supported. Export transactions from Young Platform as CSV.

### Issue: "Invalid JSON in prices file"
**Solution**: Ensure the prices JSON file is valid. Use a JSON validator online or check formatting.

### Issue: "Nessun lotto in pancia" (No lots in inventory)
**Solution**: This may indicate chronologically unsorted transactions. Ensure CSV transactions are in chronological order (oldest to newest).

### Issue: Tax calculations seem incorrect
**Solution**:
1. Verify all input data in the CSV file
2. Check price values are in EUR
3. Confirm config.json has 2026 rules applied
4. Consult a tax professional for validation

---

## Configuration Reference

### config.json Parameters

| Parameter | Type | 2026 Value | Description |
|-----------|------|-----------|-------------|
| `tax_year` | int | 2026 | Fiscal year for calculations |
| `capital_gains_default_rate` | float | 0.26 | Default tax rate for capital gains |
| `capital_gains_tax_rates` | dict | See below | Per-asset tax rates |
| `stablecoin_eur` | float | 0.26 | Tax rate for EUR stablecoins |
| `cryptocurrency` | float | 0.33 | Tax rate for other cryptocurrencies |
| `patrimony_tax_rate` | float | 0.002 | Patrimonial tax rate (0.2%) |
| `patrimony_tax_threshold` | float | 0 | Patrimonial tax threshold (removed) |
| `max_loss_deduction` | float | 48000 | Maximum annual loss deduction (EUR) |
| `enable_logging` | bool | false | Enable debug logging |

---

## Advanced Topics

### Modifying the LIFO Algorithm

The LIFO implementation in [cfs/core/lifo_engine.py](cfs/core/lifo_engine.py) uses a stack-based approach:

1. **BUY/DEPOSIT transactions** push cost lots onto the stack
2. **SELL/WITHDRAW transactions** pop lots from the top (last in = first out)
3. Capital gain/loss is calculated per lot as: `(selling_price - cost_price) × quantity`

### Adding Support for New Exchanges

To add a new exchange parser:

1. Create a new file in `cfs/parsers/` (e.g., `binance_parser.py`)
2. Implement a parser class with a `parse_file(file_path)` method
3. Return a list of `Transaction` objects
4. Update `main.py` to recognize the new exchange
5. Add tests in `tests/` directory

---

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Run with coverage:

```bash
python -m pytest tests/ --cov=cfs
```

---

## Performance

- **Small portfolios** (< 1,000 transactions): < 1 second
- **Medium portfolios** (1,000 - 10,000 transactions): 1-5 seconds
- **Large portfolios** (> 10,000 transactions): 5-30 seconds

Performance depends on system resources and file I/O speed.

---

## Support & Community

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

### MIT License Summary

You are free to:
- ✅ Use commercially
- ✅ Modify the code
- ✅ Distribute
- ✅ Use privately

With conditions:
- ⚠️ License and copyright notice must be included
- ⚠️ Changes must be documented

---

## Changelog

### v0.2.0 (June 2026) - Current

**Features:**
- Bilingual CLI support (Italian/English)
- Differentiated tax rates (26% EUR stablecoins, 33% other crypto)
- Updated 2026 tax thresholds (EUR 0, no exemption)
- Cleaned CLI output (removed decorative elements)
- Professional bilingual disclaimer

**Improvements:**
- Enhanced code documentation
- Improved error messages
- Better configuration handling

### v0.1.0 (Initial Release)

- LIFO algorithm implementation
- Young Platform CSV parser
- Basic tax calculations
- Italian language support

---

## Roadmap

- [ ] Support for additional exchanges (Kraken, Coinbase, Crypto.com)
- [ ] Web-based UI dashboard
- [ ] Automated Quadro RT/W PDF generation
- [ ] Cryptocurrency price history integration
- [ ] Multi-year tax planning tool
- [ ] Integration with commercial tax software

---

## Acknowledgments

- Italian tax regulations research: Agenzia delle Entrate official documentation
- LIFO algorithm design: Financial accounting standards
- Testing and validation: Community contributors

---

## Contact

**Maintainer**: [Your Name/Organization]  
**Email**: [your.email@example.com]  
**Repository**: https://github.com/yourusername/crypto-fiscal-system

---

**Last Updated**: June 2026 | **Version**: 0.2.0 | **Status**: Production Ready

---

*For the most current information, always consult with a qualified tax professional before filing your Italian tax return.*
