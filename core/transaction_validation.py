from core.block import Block
from core.io_mem_pool import MemPool
import logging

class TransactionException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class TransactionValidation:
    def __init__(self, blockchain: Block):
        self.blockchain = blockchain
        self.transaction_data = {}
        self.is_valid = False
        self.mempool = MemPool()

    def receive(self, transaction_data: dict):
        """
        Recieve and init transaction data from request
        """
        self.transaction_data = transaction_data
    
    @property
    def is_new(self):
        """
        Check if current transaction is new from transaction list in memory pool
        """
        current_transactions = self.mempool.get_transactions_from_memory()
        if self.transaction_data in current_transactions:
            return False
        return True

    def store(self):
        """
        Storing current transaction to memory pool
        """
        logging.info("Storing transaction data in memory")
        logging.info(f"Transaction data: {self.transaction_data}")
        current_transactions = self.mempool.get_transactions_from_memory()
        current_transactions.append(self.transaction_data)
        self.mempool.store_transactions_in_memory(current_transactions)