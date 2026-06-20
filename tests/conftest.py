"""
Script di inizializzazione pytest per i test.
Consente di aggiungere fixture e configurazioni comuni.
"""

import sys
from pathlib import Path

# Aggiungi il root del progetto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
