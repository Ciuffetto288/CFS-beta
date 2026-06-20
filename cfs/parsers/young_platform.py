"""
Parser per i file CSV "Report Transazioni" di Young Platform.

Young Platform esporta le transazioni in CSV con le seguenti colonne:
- Data/Ora
- Tipo operazione (Acquisto, Vendita, Deposito, Prelievo, etc.)
- Asset
- Quantità
- Prezzo unitario (EUR)
- Commissioni (EUR)
- Totale (EUR)
- ID transazione

Questo parser legge il file e normalizza i dati nel formato Transaction standard.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List

from cfs.models import Transaction, TransactionType


class YoungPlatformParser:
    """Parser specializzato per Young Platform CSV."""

    # Mapping tra le stringhe del CSV di Young Platform e il nostro enum
    OPERATION_TYPE_MAPPING = {
        "Acquisto": TransactionType.BUY,
        "Vendita": TransactionType.SELL,
        "Deposito": TransactionType.DEPOSIT,
        "Prelievo": TransactionType.WITHDRAW,
        "acquisto": TransactionType.BUY,
        "vendita": TransactionType.SELL,
        "deposito": TransactionType.DEPOSIT,
        "prelievo": TransactionType.WITHDRAW,
    }

    # Formato data tipico: "2023-01-15 14:30:45" o varianti
    DATE_FORMATS = [
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]

    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """
        Prova a parsificare la data con i formati noti.

        Args:
            date_str (str): Stringa data da parsificare

        Returns:
            datetime: Data parsificata (UTC)

        Raises:
            ValueError: Se nessun formato corrisponde
        """
        for fmt in YoungPlatformParser.DATE_FORMATS:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        raise ValueError(
            f"Impossibile parsificare la data '{date_str}'. "
            f"Formati supportati: {YoungPlatformParser.DATE_FORMATS}"
        )

    @staticmethod
    def parse_float(value_str: str) -> float:
        """
        Parsifica numeri float gestendo separatori europea (virgola) e USA (punto).

        Args:
            value_str (str): Stringa numero

        Returns:
            float: Numero parsificato
        """
        if not value_str or not value_str.strip():
            return 0.0
        
        value_str = value_str.strip()
        # Sostituisci virgola con punto per i decimali europei
        value_str = value_str.replace(",", ".")
        return float(value_str)

    @staticmethod
    def parse_file(file_path: str) -> List[Transaction]:
        """
        Legge un file CSV di Young Platform e ritorna una lista di Transaction normalizzate.

        Args:
            file_path (str): Percorso al file CSV

        Returns:
            List[Transaction]: Lista di transazioni normalizzate

        Raises:
            FileNotFoundError: Se il file non esiste
            ValueError: Se il CSV ha un formato inatteso
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File non trovato: {file_path}")

        transactions = []

        try:
            with open(file_path, "r", encoding="utf-8") as csvfile:
                # Rileva il dialetto CSV (separatore, quotechar, etc.)
                sample = csvfile.read(1024)
                csvfile.seek(0)
                dialect = csv.Sniffer().sniff(sample)
                csvfile.seek(0)

                reader = csv.DictReader(csvfile, dialect=dialect)

                if not reader.fieldnames:
                    raise ValueError("CSV vuoto o senza intestazione")

                # Normalizza i nomi delle colonne (ignora maiuscole/minuscole, spazi)
                normalized_fieldnames = {name.strip().lower(): name for name in reader.fieldnames}

                for row_num, row in enumerate(reader, start=2):  # Start=2 perché riga 1 è header
                    try:
                        transaction = YoungPlatformParser._parse_row(row, normalized_fieldnames)
                        transactions.append(transaction)
                    except (ValueError, KeyError) as e:
                        print(f"⚠️  Errore alla riga {row_num}: {e}. Riga saltata.")
                        continue

        except csv.Error as e:
            raise ValueError(f"Errore durante la lettura del CSV: {e}")

        print(f"✓ Parsificate {len(transactions)} transazioni da {file_path.name}")
        return transactions

    @staticmethod
    def _parse_row(row: dict, normalized_fieldnames: dict) -> Transaction:
        """
        Parsifica una singola riga del CSV.

        Args:
            row (dict): Riga del CSV come dizionario
            normalized_fieldnames (dict): Mapping nome normalizzato -> nome originale

        Returns:
            Transaction: Transazione normalizzata

        Raises:
            ValueError: Se il formato non è valido
        """
        def get_field(candidates: list) -> str:
            """Ritorna il valore del primo campo candidato che esiste."""
            for candidate in candidates:
                candidate_lower = candidate.lower().strip()
                if candidate_lower in normalized_fieldnames:
                    field_name = normalized_fieldnames[candidate_lower]
                    return row.get(field_name, "").strip()
            raise KeyError(f"Nessuno dei campi candidati trovati: {candidates}")

        # Estrai i campi, con flessibilità sui nomi delle colonne
        timestamp_str = get_field(["data/ora", "data ora", "timestamp", "data", "date"])
        op_type_str = get_field(["tipo operazione", "tipo", "operazione", "type", "operation"])
        asset_str = get_field(["asset", "crypto", "valuta", "symbol", "coin"])
        quantity_str = get_field(["quantità", "quantita", "quantity", "amount", "qty"])
        price_str = get_field(["prezzo unitario", "prezzo", "price", "prezzo unitario"])
        fees_str = get_field(["commissioni", "commissione", "fees", "fee"])
        total_str = get_field(["totale", "total", "importo", "amount_eur"])
        tx_id_str = get_field(["id transazione", "id", "transaction id", "hash"])

        # Parsifica i campi
        timestamp = YoungPlatformParser.parse_date(timestamp_str)
        
        # Ricava il tipo transazione
        op_type_normalized = op_type_str.strip().lower()
        if op_type_normalized not in YoungPlatformParser.OPERATION_TYPE_MAPPING:
            raise ValueError(
                f"Tipo operazione non riconosciuto: '{op_type_str}'. "
                f"Supportati: {list(YoungPlatformParser.OPERATION_TYPE_MAPPING.keys())}"
            )
        transaction_type = YoungPlatformParser.OPERATION_TYPE_MAPPING[op_type_normalized]

        asset = asset_str.upper()
        quantity = YoungPlatformParser.parse_float(quantity_str)
        price_fiat = YoungPlatformParser.parse_float(price_str)
        fees = YoungPlatformParser.parse_float(fees_str)
        total_fiat = YoungPlatformParser.parse_float(total_str)

        # Se total_fiat non è presente o 0, calcolalo
        if total_fiat == 0:
            total_fiat = quantity * price_fiat

        return Transaction(
            timestamp=timestamp,
            transaction_type=transaction_type,
            asset=asset,
            quantity=quantity,
            price_fiat=price_fiat,
            total_fiat=total_fiat,
            fees=fees,
            exchange="young_platform",
            transaction_id=tx_id_str,
        )
