"""
Modulo Transaction: Definisce il modello standardizzato per le transazioni.

Ogni transazione crypto, indipendentemente dall'exchange, viene normalizzata
in questa struttura dati per permettere una elaborazione uniforme.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TransactionType(Enum):
    """Enum per i tipi di transazione supportate."""
    BUY = "BUY"              # Acquisto (carica la pila LIFO)
    SELL = "SELL"            # Vendita (estrae dalla pila LIFO, calcola PnL)
    DEPOSIT = "DEPOSIT"      # Deposito (transfer in wallet)
    WITHDRAW = "WITHDRAW"    # Prelievo (transfer out wallet)
    TRANSFER_IN = "TRANSFER_IN"   # Transfer da wallet esterno
    TRANSFER_OUT = "TRANSFER_OUT"  # Transfer verso wallet esterno


@dataclass
class Transaction:
    """
    Modello standardizzato di una transazione crypto.

    Attributi:
        timestamp (datetime): Data e ora della transazione (sempre in UTC o locale normalizzato)
        transaction_type (TransactionType): Tipo di transazione
        asset (str): Simbolo della criptovaluta (es. "BTC", "ETH")
        quantity (float): Quantità scambiata
        price_fiat (float): Prezzo unitario in EUR (o valuta fiat)
        total_fiat (float): Importo totale in fiat (quantity * price_fiat + commissioni)
        fees (float): Commissioni in fiat (es. 1.50 EUR)
        exchange (str): Nome dell'exchange (es. "young_platform")
        transaction_id (str): ID univoco della transazione presso l'exchange
        notes (Optional[str]): Note aggiuntive

    Note sulla logica fiscale italiana:
        - BUY e DEPOSIT: Il bene entra nel portafoglio
        - SELL: Esce dal portafoglio, genera plusvalenza/minusvalenza
        - TRANSFER_IN/OUT: Non hanno impatto fiscale immediato (stessa proprietà)
        - WITHDRAW: Fisicamente il bene lascia il wallet (ma potenzialmente rientra nella quota)
    """
    
    timestamp: datetime
    transaction_type: TransactionType
    asset: str
    quantity: float
    price_fiat: float
    total_fiat: float
    fees: float
    exchange: str
    transaction_id: str
    notes: Optional[str] = None

    def __post_init__(self):
        """Validazione dei dati all'istanziazione."""
        if self.quantity < 0:
            raise ValueError(f"Quantità non può essere negativa: {self.quantity}")
        if self.price_fiat < 0:
            raise ValueError(f"Prezzo non può essere negativo: {self.price_fiat}")
        if self.fees < 0:
            raise ValueError(f"Commissioni non possono essere negative: {self.fees}")
        if not isinstance(self.timestamp, datetime):
            raise ValueError(f"Timestamp deve essere datetime: {type(self.timestamp)}")

    def __repr__(self) -> str:
        """Rappresentazione leggibile della transazione."""
        return (
            f"Transaction("
            f"timestamp={self.timestamp.isoformat()}, "
            f"type={self.transaction_type.value}, "
            f"asset={self.asset}, "
            f"qty={self.quantity}, "
            f"price={self.price_fiat}€, "
            f"total={self.total_fiat}€, "
            f"fees={self.fees}€"
            f")"
        )

    def cost_per_unit(self) -> float:
        """
        Calcola il costo effettivo per unità, includendo le commissioni.
        Questo è il valore che entra nello stack LIFO per il calcolo della plusvalenza.

        Returns:
            float: (total_fiat + fees) / quantity, oppure 0 se quantity è 0
        """
        if self.quantity == 0:
            return 0.0
        return (self.total_fiat + self.fees) / self.quantity
