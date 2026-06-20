"""
Modulo parsers: Implementa i parser specifici per ogni exchange.
I parser leggono i file CSV/Excel e normalizzano i dati nel formato Transaction.
"""

from .young_platform import YoungPlatformParser

__all__ = ["YoungPlatformParser"]
