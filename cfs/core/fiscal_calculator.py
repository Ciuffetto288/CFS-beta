"""
Fiscal calculator for Italian Quadri Dichiarazione dei Redditi.
Calcolatore fiscale per i quadri della Dichiarazione dei Redditi italiana.

Implements / Implementa:
- Quadro RW: Monitoring of crypto holdings value
- Quadro RT/W: Capital gains/losses from crypto disposals
- Patrimonial tax (imposta patrimoniale): 0.2% on ALL holdings from EUR 0

2026 RULES / NORMATIVA 2026:
- E-Money Tokens (EUR stablecoins): 26% tax rate
- Bitcoin and other crypto: 33% tax rate
- Capital gains exemption: REMOVED (taxation from first cent)
- Patrimonial tax threshold: REMOVED (applies from EUR 0)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from cfs.core.lifo_engine import LIFOEngine
from cfs.core.models import CapitalGainRecord


class FiscalCalculator:
    """
    Calcolatore delle imposte secondo la normativa italiana su criptovalute.

    La logica fiscale italiana:
    - Plusvalenze da cessione: tassate al 26% (ordinaria)
    - Monitoraggio (Quadro RW): obbligo di dichiarare il valore della crypto posseduta
    - Imposta patrimoniale: 0,2% sulle cripto valutate al 31/12 (se valore > EUR 51.646)
    - Deduzione di minusvalenze: consentita fino a EUR 48.000 annui
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Inizializza il calcolatore con i parametri fiscali.

        Args:
            config_path (str): Percorso a config.json con i parametri fiscali.
                              Se None, usa i default italiani.
        """
        self.config = self._load_config(config_path)

    @staticmethod
    def _load_config(config_path: Optional[str]) -> Dict:
        """
        Load fiscal configuration from JSON file.
        Carica la configurazione fiscale da file JSON.
        """
        default_config = {
            "capital_gains_tax_rates": {"stablecoin_eur": 0.26, "cryptocurrency": 0.33},
            "capital_gains_default_rate": 0.26,
            "patrimony_tax_rate": 0.002,
            "patrimony_tax_threshold": 0,
            "max_loss_deduction": 48000,
            "tax_year": datetime.now().year,
        }

        if not config_path:
            return default_config

        config_path = Path(config_path)
        if not config_path.exists():
            return default_config

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                default_config.update(loaded)
                return default_config
        except json.JSONDecodeError:
            return default_config

    def _get_tax_rate_for_asset(self, asset: str) -> float:
        """Get tax rate for specific crypto asset (2026 rules).
        Ottiene aliquota fiscale per un asset crypto specifico.
        EUR stablecoins (USDC, EUROC, etc.): 26% | Bitcoin/others: 33%"""
        eur_stablecoins = {"USDC", "EUROC", "EURe", "EURA", "USDT", "DAI"}
        rates = self.config.get("capital_gains_tax_rates", {})
        if asset.upper() in eur_stablecoins:
            return rates.get("stablecoin_eur", 0.26)
        return rates.get("cryptocurrency", 0.33)

    def calculate_capital_gains_tax(self, lifo_engine: LIFOEngine) -> Dict:
        """
        Calculate capital gains tax from crypto disposals (Quadro RT/W).
        Calcola imposte sulle plusvalenze da cessioni crypto (Quadro RT/W).
        Applies differentiated rates per asset type (26% EUR stablecoins, 33% other crypto).
        """
        total_gains = 0
        total_losses = 0
        records = []

        for cap_gain in lifo_engine.capital_gains:
            tax_rate = self._get_tax_rate_for_asset(cap_gain.asset)
            records.append({
                "sell_date": cap_gain.sell_date.isoformat(),
                "asset": cap_gain.asset,
                "quantity_sold": cap_gain.quantity_sold,
                "selling_price": cap_gain.selling_price_per_unit,
                "cost_price": cap_gain.cost_per_unit,
                "capital_gain": cap_gain.capital_gain,
                "tax_rate_applied": tax_rate,
                "holding_days": cap_gain.holding_period_days,
            })

            if cap_gain.capital_gain >= 0:
                total_gains += cap_gain.capital_gain
            else:
                total_losses += abs(cap_gain.capital_gain)

        max_deductible_loss = min(total_losses, self.config["max_loss_deduction"])
        net_gain = max(0, total_gains - max_deductible_loss)
        default_rate = self.config.get("capital_gains_default_rate", 0.26)
        tax_amount = net_gain * default_rate

        return {
            "total_gains": total_gains,
            "total_losses": total_losses,
            "max_deductible_loss": max_deductible_loss,
            "net_gain": net_gain,
            "tax_rate_default": default_rate,
            "tax_amount": tax_amount,
            "records": records,
        }

    def calculate_patrimony_tax(
        self,
        lifo_engine: LIFOEngine,
        year_end_prices: Dict[str, float],
    ) -> Dict:
        """
        Calculate 0.2% patrimonial tax on ALL crypto holdings at 31/12 (Quadro RW).
        Calcola imposta patrimoniale 0,2% su TUTTE le cripto al 31/12 (Quadro RW).
        
        LEGAL CORRECTION 2026 / CORREZIONE LEGALE 2026:
        - Tax applies from EUR 0 (no threshold exemption)
        - Previous threshold of EUR 51.646 is removed
        - Applies to all holdings regardless of value
        """
        holdings = {}
        total_value = 0

        for asset, quantity in lifo_engine.final_balances.items():
            price = year_end_prices.get(asset, 0)
            value = quantity * price
            holdings[asset] = {
                "quantity": quantity,
                "price_31_12": price,
                "value_eur": value,
            }
            total_value += value

        threshold = self.config.get("patrimony_tax_threshold", 0)
        is_taxable = total_value > threshold
        taxable_amount = total_value if is_taxable else 0
        tax_amount = taxable_amount * self.config["patrimony_tax_rate"]

        return {
            "holdings": holdings,
            "total_value": total_value,
            "threshold": threshold,
            "is_taxable": is_taxable,
            "taxable_amount": taxable_amount,
            "tax_rate": self.config["patrimony_tax_rate"],
            "tax_amount": tax_amount,
        }

    def generate_fiscal_report(
        self,
        lifo_engine: LIFOEngine,
        year_end_prices: Dict[str, float],
    ) -> Dict:
        """
        Genera un report fiscale completo con tutte le componenti.

        Args:
            lifo_engine (LIFOEngine): Motore LIFO elaborato
            year_end_prices (Dict[str, float]): Prezzi al 31/12

        Returns:
            Dict: Report completo
        """
        cap_gains_tax = self.calculate_capital_gains_tax(lifo_engine)
        patrimony_tax = self.calculate_patrimony_tax(lifo_engine, year_end_prices)

        total_tax = cap_gains_tax["tax_amount"] + patrimony_tax["tax_amount"]

        return {
            "tax_year": self.config["tax_year"],
            "generated_at": datetime.now().isoformat(),
            "capital_gains": cap_gains_tax,
            "patrimony": patrimony_tax,
            "total_tax_liability": total_tax,
            "summary": {
                "net_capital_gains": cap_gains_tax["net_gain"],
                "total_holdings_value": patrimony_tax["total_value"],
                "total_tax": total_tax,
            },
        }
