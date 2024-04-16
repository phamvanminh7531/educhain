import logging

import requests

from core.block import Block, BlockHeader
from core.io_mem_pool import MemPool
# from core.io_known_nodes import KnownNodesMemory
from core.io_blockchain import BlockchainMemory
from core.values import NUMBER_OF_LEADING_ZEROS
from core.transaction_validation import TransactionValidation

class NewBlockException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class BlockValidation:
    def __init__(self, blockchain: Block):
        self.blockchain = blockchain
        self.new_block = None
        # self.sender = ""
        self.mempool = MemPool()
        # self.known_nodes_memory = KnownNodesMemory()
        self.blockchain_memory = BlockchainMemory()
        # self.hostname = hostname
    
    def receive(self, new_block: dict):
        """
        Recieve and init new block data from request
        """
        new_block_header = BlockHeader(**new_block["header"])
        self.new_block = Block(transactions=new_block["transactions"], block_header=new_block_header)
        try:
            """
            Check the previous hash of new block is equal to current last block in blockchain
            """
            assert self.blockchain.block_header.hash == self.new_block.block_header.previous_block_hash
        except:
            print("Previous block provided is not the most recent block")
            raise NewBlockException("", "Previous block provided is not the most recent block")
    
    def _validate_hash(self):
        """
        Check new block hash with zero difficulty
        """
        new_block_hash = self.new_block.block_header.get_hash()
        number_of_zeros_string = "".join([str(0) for _ in range(NUMBER_OF_LEADING_ZEROS)])
        try:
            assert new_block_hash.startswith(number_of_zeros_string)
        except AssertionError:
            print('Proof of work validation failed')
            raise NewBlockException("", "Proof of work validation failed")
    
    def _validate_transaction(self):
        pass
    
    def validate(self):
        self._validate_hash()
        self._validate_transaction()
    
    def add_new_block_to_blockchain(self):
        self.new_block.previous_block = self.blockchain
        self.blockchain_memory.store_blockchain_in_memory(self.new_block)
    
    def clear_block_transactions_from_mempool(self):
        current_transactions = self.mempool.get_transactions_from_memory()
        transactions_cleared = [transaction for transaction in current_transactions if not (transaction in self.new_block.transactions)]
        self.mempool.store_transactions_in_memory(transactions_cleared)