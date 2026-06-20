"""
Modulo core: Implementa la logica contabile e fiscale italiana (LIFO, Quadro RW, etc.)
"""

from .lifo_engine import LIFOEngine
from .fiscal_calculator import FiscalCalculator
from .models import LotEntry, CapitalGainRecord

__all__ = ["LIFOEngine", "FiscalCalculator", "LotEntry", "CapitalGainRecord"]
