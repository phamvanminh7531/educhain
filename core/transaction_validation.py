from core.block import Block
from core.io_mem_pool import MemPool
from core.io_known_nodes import KnownNodesMemory
import logging
import requests

class TransactionException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class TransactionValidation:
    def __init__(self, blockchain: Block, hostname: str):
        self.blockchain = blockchain
        self.transaction_data = {}
        self.is_valid = False
        self.known_node_memory = KnownNodesMemory()
        self.mempool = MemPool()
        self.hostname = hostname
        self.sender = ""

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

    def broadcast(self):
        logging.info("Broadcasting to all nodes")
        node_list = self.known_node_memory.known_nodes
        for node in node_list:
            if node.hostname != self.hostname and node.hostname != self.sender:
                try:
                    logging.info(f"Broadcasting to {node.hostname}")
                    node.send_transaction({"transaction": self.transaction_data})
                except requests.ConnectionError:
                    logging.info(f"Failed broadcasting to {node.hostname}")