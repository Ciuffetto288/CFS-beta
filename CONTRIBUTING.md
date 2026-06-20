"""
CONTRIBUTING.md - Linee guida per i contributori

Grazie per l'interesse nel contribuire a CFS - Crypto Fiscal System!

## Codice di Condotta

Questo progetto è impegnato nel fornire un ambiente accogliente per tutti, 
indipendentemente dall'esperienza, dal genere, identità e espressione, età, 
religione, nazionalità, o altre caratteristiche.

## Come Contribuire

### Segnalare Bug

Se trovi un bug, apri un GitHub Issue con:
- Una descrizione chiara del problema
- Passi per riprodurre il comportamento
- Il file CSV di test (anonimizzato se necessario)
- Output completo e traceback

### Suggerire Nuove Funzionalità

Apri una GitHub Issue con:
- Un titolo descrittivo
- Una descrizione dettagliata della feature
- Esempi di come potrebbe essere usata
- Motivazione dietro la richiesta

### Aggiungere Nuovo Codice

1. **Fork il repository**
   ```bash
   git clone https://github.com/yourusername/crypto-fiscal-system.git
   ```

2. **Crea un branch per la feature**
   ```bash
   git checkout -b feature/nome-feature
   ```

3. **Sviluppa e testa**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   # Scrivi il codice e i test
   pytest
   ```

4. **Commit e Push**
   ```bash
   git commit -m "Descrizione concisa dei cambiamenti"
   git push origin feature/nome-feature
   ```

5. **Apri una Pull Request**
   - Descrivi i cambiamenti fatti
   - Referenzia l'Issue correlata (se esiste)
   - Assicurati che i test passino

## Linee Guida per il Codice

- **Python 3.10+** - Usa type hints e f-strings
- **PEP 8** - Segui lo stile Python standard
- **Docstrings** - Tutti i moduli, classi e funzioni devono avere docstring completi
- **Commenti** - Scrivi commenti chiari per la logica complessa
- **Test** - Aggiungi unit test per le nuove funzionalità

### Esempio di Buon Codice

```python
def calculate_capital_gain(
    selling_price: float,
    cost_price: float,
    quantity: float
) -> float:
    \"\"\"
    Calcola la plusvalenza da una vendita.

    Args:
        selling_price (float): Prezzo di vendita per unità
        cost_price (float): Costo per unità
        quantity (float): Quantità venduta

    Returns:
        float: Plusvalenza totale (o minusvalenza se negativa)
    \"\"\"
    return (selling_price - cost_price) * quantity
```

## Area di Focus

Queste aree sono particolarmente interessate a contributi:

1. **Parser per nuovi exchange**
   - Kraken, Coinbase, Poloniex, Binance, etc.
   - Segui il pattern in `cfs/parsers/young_platform.py`

2. **Interfaccia GUI**
   - Streamlit o CustomTkinter
   - User-friendly e accessible

3. **Test e Validazione**
   - Unit test per la logica LIFO
   - Test per scenari edge case

4. **Documentazione**
   - Guida utente in italiano
   - Tutoriali video
   - FAQ

5. **Ottimizzazione**
   - Performance per file CSV grandi
   - Parallelizzazione dell'elaborazione

## Discussioni e Domande

- Usa GitHub **Discussions** per domande generali
- Usa GitHub **Issues** per bug e feature request

## Riconoscimenti

Tutti i contributor verranno elencati nel file CONTRIBUTORS.md

Grazie per il tuo contributo! 🎉
"""
