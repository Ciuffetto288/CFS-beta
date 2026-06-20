"""
File di test per il modulo Transaction.

Esegui con: python -m pytest tests/test_transaction.py
"""

import pytest
from datetime import datetime
from cfs.models import Transaction, TransactionType


def test_transaction_creation():
    """Test creazione di una transazione valida."""
    tx = Transaction(
        timestamp=datetime(2024, 1, 15, 14, 30, 0),
        transaction_type=TransactionType.BUY,
        asset="BTC",
        quantity=0.5,
        price_fiat=30000.00,
        total_fiat=15000.00,
        fees=1.50,
        exchange="young_platform",
        transaction_id="tx_123456"
    )
    
    assert tx.asset == "BTC"
    assert tx.quantity == 0.5
    assert tx.price_fiat == 30000.00
    assert tx.transaction_type == TransactionType.BUY


def test_transaction_cost_per_unit():
    """Test calcolo costo per unità includendo commissioni."""
    tx = Transaction(
        timestamp=datetime(2024, 1, 15, 14, 30, 0),
        transaction_type=TransactionType.BUY,
        asset="BTC",
        quantity=1.0,
        price_fiat=30000.00,
        total_fiat=30000.00,
        fees=10.00,  # EUR 10 di commissione
        exchange="young_platform",
        transaction_id="tx_123456"
    )
    
    # Costo = (30000 + 10) / 1 = 30010
    assert tx.cost_per_unit() == 30010.00


def test_transaction_negative_quantity_raises_error():
    """Test che quantità negativa solleva errore."""
    with pytest.raises(ValueError):
        Transaction(
            timestamp=datetime(2024, 1, 15, 14, 30, 0),
            transaction_type=TransactionType.BUY,
            asset="BTC",
            quantity=-0.5,  # Negativo!
            price_fiat=30000.00,
            total_fiat=-15000.00,
            fees=0,
            exchange="young_platform",
            transaction_id="tx_123456"
        )


def test_transaction_negative_fees_raises_error():
    """Test che commissioni negative sollevano errore."""
    with pytest.raises(ValueError):
        Transaction(
            timestamp=datetime(2024, 1, 15, 14, 30, 0),
            transaction_type=TransactionType.BUY,
            asset="BTC",
            quantity=0.5,
            price_fiat=30000.00,
            total_fiat=15000.00,
            fees=-1.50,  # Negativo!
            exchange="young_platform",
            transaction_id="tx_123456"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
