import logging

import requests

from core.block import Block, BlockHeader
from core.io_mem_pool import MemPool
from core.io_known_nodes import KnownNodesMemory
from core.io_blockchain import BlockchainMemory
from core.io_target_hash import TargetHashControl
from core.transaction_validation import TransactionValidation

class NewBlockException(Exception):
    """
    Block validation exception
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class BlockValidation:
    def __init__(self, blockchain: Block, hostname: str):
        self.blockchain = blockchain
        self.new_block = None
        self.sender = ""
        self.mempool = MemPool()
        self.known_nodes_memory = KnownNodesMemory()
        self.blockchain_memory = BlockchainMemory()
        self.target_hash_control = TargetHashControl()
        self.hostname = hostname

    def receive(self, new_block: dict, sender: str):
        """
        Recieve and init new block data from request
        """
        new_block_header = BlockHeader(**new_block["header"])


        self.new_block = Block(transactions=new_block["transactions"], block_header=new_block_header)
        self.sender = sender
        try:
            """
            Check the previous hash of new block is equal to current last block in blockchain
            """
            assert self.blockchain.block_header.hash == self.new_block.block_header.previous_block_hash
        except:
            print("Previous block provided is not the most recent block")
            raise NewBlockException("", "Previous block provided is not the most recent block")
        
    
    def _validate_transaction(self):
        pass
    
    def validate(self):
        self._validate_transaction()
    
    def add_new_block_to_blockchain(self):
        """
        Adding new block recive from network to memory and checking for recalculate target hash
        """
        self.new_block.previous_block = self.blockchain
        self.blockchain_memory.store_blockchain_in_memory(self.new_block)
        self.target_hash_control.checking_time_for_recalculate(self.blockchain_memory.get_blockchain_from_memory())
    
    def clear_block_transactions_from_mempool(self):
        """
        Delete duplicate transaction between new block and mem pool
        """
        current_transactions = self.mempool.get_transactions_from_memory()
        transactions_cleared = [transaction for transaction in current_transactions if not (transaction in self.new_block.transactions)]
        self.mempool.store_transactions_in_memory(transactions_cleared)

    def broadcast(self):
        """
        Broadcasting to all node in know_nodes_memory
        """
        logging.info(f"Broadcasting block")
        node_list = self.known_nodes_memory.known_nodes
        for node in node_list:
            if node.hostname != self.hostname and node.hostname != self.sender:
                block_content = {
                    "block": {
                        "header": self.new_block.block_header.to_dict,
                        "transactions": self.new_block.transactions
                    },
                    "sender": self.hostname
                }
                try:
                    logging.info(f"Broadcasting to {node.hostname}")
                    node.send_new_block(block_content)
                except requests.exceptions.HTTPError as error:
                    logging.info(f"Failed to broadcast block to {node.hostname}: {error}")