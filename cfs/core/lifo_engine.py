"""
LIFO Engine (Last In, First Out) for capital gains calculation.
Motore LIFO (Last In, First Out) per il calcolo delle plusvalenze.

Implementation of LIFO algorithm per Italian tax law:
- Each purchase (BUY, DEPOSIT) adds a LotEntry to the top of the stack
- Each sale (SELL) pops lots from the top of the stack
- Historic cost is tracked for each unit sold
- Capital gain/loss is calculated automatically

Implementazione dell'algoritmo LIFO per la fiscalità italiana:
- Ogni acquisto (BUY, DEPOSIT) aggiunge un LotEntry in cima allo stack
- Ogni vendita (SELL) estrae lotti dal top dello stack
- Il costo storico viene tracciato per ogni unità venduta
- Si calcola automaticamente la plusvalenza/minusvalenza
"""

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple

from cfs.models import Transaction, TransactionType
from .models import LotEntry, CapitalGainRecord


class LIFOEngine:
    """
    LIFO calculation engine for cryptocurrencies.
    Maintains a separate stack for each asset (BTC stack, ETH stack, etc.).
    Chronological processing order is CRITICAL.
    
    Motore di calcolo LIFO per criptovalute.
    Mantiene uno stack separato per ogni asset (BTC stack, ETH stack, etc.).
    L'ordine di elaborazione cronologico è CRUCIALE.
    """

    def __init__(self):
        """Initialize LIFO engine / Inizializza il motore LIFO."""
        self.stacks: Dict[str, List[LotEntry]] = defaultdict(list)
        self.capital_gains: List[CapitalGainRecord] = []
        self.final_balances: Dict[str, float] = defaultdict(float)

    def process_transactions(self, transactions: List[Transaction]) -> None:
        """
        Process list of transactions in chronological order, building LIFO stacks
        and calculating capital gains. | Elabora transazioni in ordine cronologico.
        
        Args / Parametri:
            transactions (List[Transaction]): Must be sorted by timestamp / Deve essere ordinata
        """
        # Sort by timestamp (CRITICAL!) / Ordina per timestamp (CRUCIALE!)
        sorted_transactions = sorted(transactions, key=lambda t: t.timestamp)

        for tx in sorted_transactions:
            if tx.transaction_type == TransactionType.BUY:
                self._handle_buy(tx)
            elif tx.transaction_type == TransactionType.SELL:
                self._handle_sell(tx)
            elif tx.transaction_type == TransactionType.DEPOSIT:
                self._handle_deposit(tx)
            elif tx.transaction_type == TransactionType.WITHDRAW:
                self._handle_withdraw(tx)
            elif tx.transaction_type == TransactionType.TRANSFER_IN:
                self._handle_transfer_in(tx)
            elif tx.transaction_type == TransactionType.TRANSFER_OUT:
                self._handle_transfer_out(tx)

        self._calculate_final_balances()

    def _handle_buy(self, tx: Transaction) -> None:
        """
        Handle purchase (BUY): add lot to LIFO stack. | Gestisce un acquisto.
        """
        lot = LotEntry(
            quantity=tx.quantity,
            cost_per_unit=tx.cost_per_unit(),
            buy_date=tx.timestamp,
            asset=tx.asset,
            transaction_id=tx.transaction_id,
        )
        self.stacks[tx.asset].append(lot)

    def _handle_sell(self, tx: Transaction) -> None:
        """
        Handle sale (SELL): pop lots from LIFO stack and calculate PnL.
        Gestisce una vendita (SELL): estrae lotti dallo stack LIFO e calcola PnL.
        """
        asset = tx.asset
        quantity_to_sell = tx.quantity

        if asset not in self.stacks or not self.stacks[asset]:
            print(f"Warning: Attempted sell of {quantity_to_sell} {asset} with no inventory.")
            return

        selling_price_per_unit = tx.price_fiat

        # Pop lots from LIFO stack (last in = first out)
        # Estrai lotti dallo stack LIFO finché quantity_to_sell > 0
        while quantity_to_sell > 0 and self.stacks[asset]:
            # Pop dall'ultimo elemento dello stack (LIFO)
            lot = self.stacks[asset].pop()

            quantity_consumed = min(quantity_to_sell, lot.quantity)
            capital_gain = (selling_price_per_unit - lot.cost_per_unit) * quantity_consumed
            holding_days = (tx.timestamp.date() - lot.buy_date.date()).days

            # Registra il capital gain
            record = CapitalGainRecord(
                sell_date=tx.timestamp,
                asset=asset,
                quantity_sold=quantity_consumed,
                selling_price_per_unit=selling_price_per_unit,
                cost_per_unit=lot.cost_per_unit,
                capital_gain=capital_gain,
                holding_period_days=holding_days,
                lot_buy_date=lot.buy_date,
                selling_transaction_id=tx.transaction_id,
                cost_transaction_id=lot.transaction_id,
            )
            self.capital_gains.append(record)

            # If lot partially consumed, return to stack with reduced qty
            # Se il lotto non è completamente consumato, rimettilo nello stack
            if lot.quantity > quantity_consumed:
                lot.quantity -= quantity_consumed
                self.stacks[asset].append(lot)

            quantity_to_sell -= quantity_consumed

    def _handle_deposit(self, tx: Transaction) -> None:
        """
        Handle deposit (crypto received from external transfer or airdrop).
        Treated as purchase for tax purposes. | Gestisce un deposito (crypto ricevuta).
        """
        lot = LotEntry(
            quantity=tx.quantity,
            cost_per_unit=tx.price_fiat,
            buy_date=tx.timestamp,
            asset=tx.asset,
            transaction_id=tx.transaction_id,
        )
        self.stacks[tx.asset].append(lot)

    def _handle_withdraw(self, tx: Transaction) -> None:
        """
        Handle withdrawal (WITHDRAW): remove crypto from LIFO stack (LIFO style, no PnL).
        Gestisce un prelievo (WITHDRAW): rimuove crypto dallo stack LIFO.
        """
        asset = tx.asset
        quantity_to_withdraw = tx.quantity

        if asset not in self.stacks or not self.stacks[asset]:
            print(f"Warning: Attempted withdrawal of {quantity_to_withdraw} {asset} with no inventory.")
            return

        # Remove from LIFO stack / Rimuovi dallo stack LIFO (últmo entrato, primo uscito)
        while quantity_to_withdraw > 0 and self.stacks[asset]:
            lot = self.stacks[asset].pop()
            quantity_removed = min(quantity_to_withdraw, lot.quantity)

            if lot.quantity > quantity_removed:
                lot.quantity -= quantity_removed
                self.stacks[asset].append(lot)

            quantity_to_withdraw -= quantity_removed

    def _handle_transfer_in(self, tx: Transaction) -> None:
        """Handle incoming transfer (from external wallet). Identical to DEPOSIT."""
        self._handle_deposit(tx)

    def _handle_transfer_out(self, tx: Transaction) -> None:
        """Handle outgoing transfer (to external wallet). Identical to WITHDRAW."""
        self._handle_withdraw(tx)

    def _calculate_final_balances(self) -> None:
        """
        Calculate final balance for each asset (residual quantities in stack).
        Used for Quadro RW (holdings monitoring). | Calcola il saldo finale per ogni asset.
        """
        for asset, stack in self.stacks.items():
            total_qty = sum(lot.quantity for lot in stack)
            self.final_balances[asset] = total_qty

    def get_total_capital_gains(self) -> float:
        """Return sum of all capital gains (or negative if losses). | Somma di tutte le plusvalenze."""
        return sum(record.capital_gain for record in self.capital_gains)

    def get_total_capital_losses(self) -> float:
        """Return sum of all capital losses (as positive number). | Somma di tutte le minusvalenze."""
        return abs(sum(min(0, record.capital_gain) for record in self.capital_gains))

    def get_net_capital_gain(self) -> float:
        """Ritorna il guadagno netto (plusvalenze - minusvalenze)."""
        return self.get_total_capital_gains() + sum(
            record.capital_gain for record in self.capital_gains if record.capital_gain < 0
        )

    def get_summary_by_asset(self) -> Dict[str, Dict]:
        """
        Ritorna un summary per asset con info utili per il Quadro RW.

        Returns:
            Dict con chiavi = asset, values = {
                "quantity_final": float,
                "total_cost": float,
                "num_lots": int,
                "buys": int,
                "sells": int,
            }
        """
        summary = {}

        for asset in set(list(self.stacks.keys()) + list(self.final_balances.keys())):
            stack = self.stacks.get(asset, [])
            total_cost = sum(lot.total_cost() for lot in stack)
            num_lots = len(stack)

            buys = len([c for c in self.capital_gains if c.asset == asset])  # Approssimazione
            sells = len([c for c in self.capital_gains if c.asset == asset])

            summary[asset] = {
                "quantity_final": self.final_balances.get(asset, 0),
                "total_cost_remaining": total_cost,
                "num_lots": num_lots,
                "sells_count": sells,
            }

        return summary
