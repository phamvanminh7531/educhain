import json
import logging
from datetime import datetime

from core.block import Block, BlockHeader
from core.io_blockchain import BlockchainMemory
from core.io_mem_pool import MemPool
from core.merkle_tree import get_merkle_root
from core.utils import calculate_hash
from core.values import NUMBER_OF_LEADING_ZEROS


class BlockException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class ProofOfWork:
    def __init__(self):
        logging.info("Starting Proof of Work")
        # self.known_nodes_memory = KnownNodesMemory()
        blockchain_memory = BlockchainMemory()
        # self.hostname = hostname
        self.mempool = MemPool()
        self.blockchain = blockchain_memory.get_blockchain_from_memory()
        self.new_block = None

    @staticmethod
    def get_noonce(block_header: BlockHeader) -> int:
        """
        Find nononce number when hashing block
        """
        logging.info("Trying to find noonce")
        block_header_hash = ""
        noonce = block_header.noonce
        starting_zeros = "".join([str(0) for _ in range(NUMBER_OF_LEADING_ZEROS)])
        while not block_header_hash.startswith(starting_zeros):
            noonce = noonce + 1
            block_header_content = {
                "previous_block_hash": block_header.previous_block_hash,
                "merkle_root": block_header.merkle_root,
                "timestamp": block_header.timestamp,
                "noonce": noonce
            }
            block_header_hash = calculate_hash(json.dumps(block_header_content))
        logging.info("Found the noonce!")
        return noonce

    def create_new_block(self):
        logging.info("Creating new block")
        transactions = self.mempool.get_transactions_from_memory()
        if transactions:
            block_header = BlockHeader(
                merkle_root=get_merkle_root(transactions),
                previous_block_hash=self.blockchain.block_header.hash,
                timestamp=datetime.timestamp(datetime.now()),
                noonce=0,
                hash=None
            )
            block_header.noonce = self.get_noonce(block_header)
            block_header.hash = block_header.get_hash()
            self.new_block = Block(transactions=transactions, block_header=block_header)
        else:
            raise BlockException("", "No transaction in mem_pool")

