"""
Modelli interni per il core contabile (LIFO engine e calcoli fiscali).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class LotEntry:
    """
    Rappresenta un lotto (lot) di criptovalute acquistate, con costo di carico storico.

    Utilizzato nello stack LIFO: quando acquistiamo crypto, inseriamo un LotEntry nello stack.
    Quando vendiamo, estraiamo dal top dello stack (Last In, First Out).

    Attributi:
        quantity (float): Quantità di crypto nel lotto
        cost_per_unit (float): Costo per unità (in EUR, includendo commissioni)
        buy_date (datetime): Data di acquisto del lotto
        asset (str): Simbolo asset (BTC, ETH, etc.)
        transaction_id (str): ID transazione associato
    """
    quantity: float
    cost_per_unit: float
    buy_date: datetime
    asset: str
    transaction_id: str

    def total_cost(self) -> float:
        """Calcola il costo totale del lotto."""
        return self.quantity * self.cost_per_unit

    def __repr__(self) -> str:
        return (
            f"LotEntry(asset={self.asset}, qty={self.quantity}, "
            f"cost_unit={self.cost_per_unit:.2f}€, date={self.buy_date.date()})"
        )


@dataclass
class CapitalGainRecord:
    """
    Registra un evento di plusvalenza o minusvalenza (occasione di SELL).

    Attributi:
        sell_date (datetime): Data della vendita
        asset (str): Asset venduto
        quantity_sold (float): Quantità venduta
        selling_price_per_unit (float): Prezzo di vendita unitario (EUR)
        cost_per_unit (float): Costo storico per unità
        capital_gain (float): Plusvalenza = (selling_price - cost) * quantity
                             Minusvalenza se negativo
        holding_period_days (int): Giorni di possesso del lotto venduto
        lot_buy_date (datetime): Data di acquisto del lotto venduto
        selling_transaction_id (str): ID transazione di vendita
        cost_transaction_id (str): ID transazione di acquisto (lotto consumato)
    """
    sell_date: datetime
    asset: str
    quantity_sold: float
    selling_price_per_unit: float
    cost_per_unit: float
    capital_gain: float
    holding_period_days: int
    lot_buy_date: datetime
    selling_transaction_id: str
    cost_transaction_id: str

    def __post_init__(self):
        """Calcola automaticamente capital_gain se necessario."""
        if self.capital_gain == 0 and self.quantity_sold > 0:
            self.capital_gain = (self.selling_price_per_unit - self.cost_per_unit) * self.quantity_sold

    def is_long_term(self) -> bool:
        """
        Determina se la plusvalenza è a lungo termine (holding > 7 giorni).
        In Italia, non c'è differenza fiscale tra ST e LT nel tassamento ordinario (26%).
        Qui è solo per documentazione/reporting.
        """
        return self.holding_period_days > 7

    def __repr__(self) -> str:
        gain_type = "PlusVal" if self.capital_gain >= 0 else "MinusVal"
        return (
            f"CapitalGain({self.asset}, qty={self.quantity_sold}, "
            f"sell={self.sell_date.date()}, {gain_type}={self.capital_gain:.2f}€, "
            f"holding_days={self.holding_period_days})"
        )
