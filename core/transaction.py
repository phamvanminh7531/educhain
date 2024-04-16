from datetime import datetime
import json
from core.utils import calculate_hash


class Transaction():
    def __init__(self, data: dict):
        self.data = data
        self.timestamp = datetime.timestamp(datetime.now())
        self.txid = self.get_transaction_hash()
    
    def get_transaction_hash(self) -> str:
        transaction_data = {
            "timestamp" : self.timestamp,
            "data" : self.data
        }
        transaction_bytes = json.dumps(transaction_data, indent=2)
        return calculate_hash(transaction_bytes)
    
    @property
    def transaction_data(self) -> dict:
        transaction_data = {
            "txid": self.txid,
            "timestamp": self.timestamp,
            "data": self.data,
        }
        return transaction_data