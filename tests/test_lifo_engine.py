"""
Test del motore LIFO per validare il calcolo delle plusvalenze.

Esegui con: python -m pytest tests/test_lifo_engine.py
"""

import pytest
from datetime import datetime
from cfs.core import LIFOEngine
from cfs.models import Transaction, TransactionType


def test_lifo_simple_buy_and_sell():
    """Test semplice: acquisto e vendita di 1 BTC."""
    engine = LIFOEngine()

    # Acquisto 1 BTC a EUR 30.000
    buy_tx = Transaction(
        timestamp=datetime(2024, 1, 15, 10, 0, 0),
        transaction_type=TransactionType.BUY,
        asset="BTC",
        quantity=1.0,
        price_fiat=30000.00,
        total_fiat=30000.00,
        fees=10.00,
        exchange="young_platform",
        transaction_id="tx_buy_001"
    )

    # Vendo 1 BTC a EUR 40.000
    sell_tx = Transaction(
        timestamp=datetime(2024, 6, 15, 14, 0, 0),
        transaction_type=TransactionType.SELL,
        asset="BTC",
        quantity=1.0,
        price_fiat=40000.00,
        total_fiat=40000.00,
        fees=20.00,
        exchange="young_platform",
        transaction_id="tx_sell_001"
    )

    engine.process_transactions([buy_tx, sell_tx])

    # Verifiche
    assert len(engine.capital_gains) == 1
    cap_gain = engine.capital_gains[0]
    
    # Costo per unità = (30000 + 10) / 1 = 30010
    # Plusvalenza = (40000 - 30010) * 1 = 9990
    assert cap_gain.cost_per_unit == 30010.00
    assert cap_gain.selling_price_per_unit == 40000.00
    assert cap_gain.capital_gain == pytest.approx(9990.00, rel=1e-2)
    assert cap_gain.holding_period_days == 152  # Circa 5 mesi


def test_lifo_multiple_lots():
    """Test LIFO con multipli lotti: Last In, First Out."""
    engine = LIFOEngine()

    # Lotto 1: 1 BTC @ EUR 30.000 (1 gennaio)
    lot1 = Transaction(
        timestamp=datetime(2024, 1, 1, 10, 0, 0),
        transaction_type=TransactionType.BUY,
        asset="BTC",
        quantity=1.0,
        price_fiat=30000.00,
        total_fiat=30000.00,
        fees=0,
        exchange="young_platform",
        transaction_id="tx_001"
    )

    # Lotto 2: 1 BTC @ EUR 35.000 (15 giugno)
    lot2 = Transaction(
        timestamp=datetime(2024, 6, 15, 10, 0, 0),
        transaction_type=TransactionType.BUY,
        asset="BTC",
        quantity=1.0,
        price_fiat=35000.00,
        total_fiat=35000.00,
        fees=0,
        exchange="young_platform",
        transaction_id="tx_002"
    )

    # Vendita di 1.5 BTC @ EUR 40.000 (15 dicembre)
    sell = Transaction(
        timestamp=datetime(2024, 12, 15, 14, 0, 0),
        transaction_type=TransactionType.SELL,
        asset="BTC",
        quantity=1.5,
        price_fiat=40000.00,
        total_fiat=60000.00,
        fees=0,
        exchange="young_platform",
        transaction_id="tx_sell_001"
    )

    engine.process_transactions([lot1, lot2, sell])

    # Verifiche LIFO
    # Primo: 1.0 BTC dal Lotto 2 (35.000) -> PnL = (40.000 - 35.000) * 1 = 5.000
    # Secondo: 0.5 BTC dal Lotto 1 (30.000) -> PnL = (40.000 - 30.000) * 0.5 = 5.000
    # Totale PnL = 10.000

    assert len(engine.capital_gains) == 2

    # Prima vendita (da Lotto 2)
    assert engine.capital_gains[0].quantity_sold == 1.0
    assert engine.capital_gains[0].cost_per_unit == 35000.00
    assert engine.capital_gains[0].capital_gain == pytest.approx(5000.00, rel=1e-2)

    # Seconda vendita (da Lotto 1)
    assert engine.capital_gains[1].quantity_sold == 0.5
    assert engine.capital_gains[1].cost_per_unit == 30000.00
    assert engine.capital_gains[1].capital_gain == pytest.approx(5000.00, rel=1e-2)

    # Total PnL
    total_pnl = engine.get_total_capital_gains()
    assert total_pnl == pytest.approx(10000.00, rel=1e-2)


def test_lifo_capital_loss():
    """Test LIFO con minusvalenza."""
    engine = LIFOEngine()

    buy = Transaction(
        timestamp=datetime(2024, 1, 15, 10, 0, 0),
        transaction_type=TransactionType.BUY,
        asset="BTC",
        quantity=1.0,
        price_fiat=40000.00,
        total_fiat=40000.00,
        fees=0,
        exchange="young_platform",
        transaction_id="tx_buy_001"
    )

    # Vendo a prezzo inferiore
    sell = Transaction(
        timestamp=datetime(2024, 6, 15, 14, 0, 0),
        transaction_type=TransactionType.SELL,
        asset="BTC",
        quantity=1.0,
        price_fiat=35000.00,
        total_fiat=35000.00,
        fees=0,
        exchange="young_platform",
        transaction_id="tx_sell_001"
    )

    engine.process_transactions([buy, sell])

    # Minusvalenza = (35.000 - 40.000) * 1 = -5.000
    assert len(engine.capital_gains) == 1
    assert engine.capital_gains[0].capital_gain == pytest.approx(-5000.00, rel=1e-2)

    total_losses = engine.get_total_capital_losses()
    assert total_losses == pytest.approx(5000.00, rel=1e-2)


def test_lifo_final_balances():
    """Test calcolo saldi finali (holding residuali)."""
    engine = LIFOEngine()

    # Acquisto 2 BTC
    buy = Transaction(
        timestamp=datetime(2024, 1, 15, 10, 0, 0),
        transaction_type=TransactionType.BUY,
        asset="BTC",
        quantity=2.0,
        price_fiat=30000.00,
        total_fiat=60000.00,
        fees=0,
        exchange="young_platform",
        transaction_id="tx_buy_001"
    )

    # Vendo 1 BTC
    sell = Transaction(
        timestamp=datetime(2024, 6, 15, 14, 0, 0),
        transaction_type=TransactionType.SELL,
        asset="BTC",
        quantity=1.0,
        price_fiat=40000.00,
        total_fiat=40000.00,
        fees=0,
        exchange="young_platform",
        transaction_id="tx_sell_001"
    )

    engine.process_transactions([buy, sell])

    # Residui: 1 BTC
    assert engine.final_balances["BTC"] == pytest.approx(1.0, rel=1e-2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
