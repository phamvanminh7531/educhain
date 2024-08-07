from core.block import Block
from core.io_mem_pool import MemPool
from core.io_known_nodes import KnownNodesMemory
from core.node import EcertNode
import logging
import requests
from core.utils import calculate_hash
import json
import binascii
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

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

    def receive(self, transaction_data: dict, sender = ""):
        """
        Recieve and init transaction data from request
        """
        self.transaction_data = transaction_data
        self.sender = sender
    
    def _signature_validate(self):
        """
        Validate teacher digital signature signed in certificate
        """
        signature = binascii.unhexlify(self.transaction_data["signature"])
        public_key = binascii.unhexlify(self.transaction_data["public_key"])
        try:
            """
            Validate public key of teacher
            """
            assert self.transaction_data["public_key_hash"] == calculate_hash(
                                                                    str(self.transaction_data["data"]["teacher_code"]) + 
                                                                    self.transaction_data["public_key"]
                                                                )
        except:
            print("Public key validate failed")
            raise TransactionException("", "Digital signature validate failed, data of transaction may be changed")
        new_cert_data_byte = json.dumps(self.transaction_data["data"], indent=2).encode('utf-8')
        new_hasher = SHA256.new(new_cert_data_byte)
        verifier = PKCS1_v1_5.new(RSA.import_key(public_key))
        try:
            """
            Validate digital signature
            """
            assert verifier.verify(new_hasher, signature) == True
        except:
            print("Digital signature validate failed")
            raise TransactionException("", "Digital signature validate failed, data of transaction may be changed")
    
    def _hash_validate(self):
        """
        Validate hash of txid
        """
        current_txid = self.transaction_data["txid"]
        # Hash again to validate
        new_transaction_data = {
            "timestamp" : self.transaction_data["timestamp"],
            "data" : self.transaction_data["data"]
        }
        new_transaction_data_byte = json.dumps(new_transaction_data, indent=2)
        new_txid = calculate_hash(new_transaction_data_byte)
        try:
            """
            Check the txid of transaction is equal to current txid
            """
            assert current_txid == new_txid
        except:
            print("Validate TXID hash failed")
            raise TransactionException("", "Txid validate failed, data of transaction may be changed")
    
    def validate(self):
        logging.info("Validating transaction")        
        self._signature_validate()
        self._hash_validate()
        self.is_valid = True


    
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
        if self.is_valid:
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
                    node.send_transaction({"transaction": self.transaction_data, "sender": self.hostname})
                except requests.ConnectionError:
                    logging.info(f"Failed broadcasting to {node.hostname}")