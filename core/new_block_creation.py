import json
import logging
from datetime import datetime
import requests

from core.block import Block, BlockHeader
from core.io_blockchain import BlockchainMemory
from core.io_mem_pool import MemPool
from core.io_known_nodes import KnownNodesMemory
from core.merkle_tree import get_merkle_root
from core.utils import calculate_hash

target_hash = '0x7aff850000000000000000000000000000000000000000000000000000'
diff = int(target_hash, 16)


class BlockException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class ProofOfWork:
    def __init__(self, hostname: str):
        logging.info("Starting Proof of Work")
        self.known_nodes_memory = KnownNodesMemory()
        blockchain_memory = BlockchainMemory()
        self.hostname = hostname
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
        while True:
            noonce = noonce + 1
            block_header_content = {
                "previous_block_hash": block_header.previous_block_hash,
                "merkle_root": block_header.merkle_root,
                "timestamp": block_header.timestamp,
                "noonce": noonce
            }
            block_header_hash = calculate_hash(json.dumps(block_header_content))
            logging.info(f"Current hash {block_header_hash}")
            if int(block_header_hash, 16) < diff:
                break
        logging.info("Found the noonce!")
        return noonce

    def create_new_block(self):
        logging.info("Creating new block")
        transactions = self.mempool.get_transactions_from_memory()
        if transactions:
            block_header = BlockHeader(
                height = len(self.blockchain),
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

    def broadcast(self) -> bool:
        logging.info("Broadcasting to other nodes")
        node_list = self.known_nodes_memory.known_nodes
        broadcasted_node = False
        for node in node_list:
            if node.hostname != self.hostname:
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
                    broadcasted_node = True
                except requests.exceptions.ConnectionError as e:
                    logging.info(f"Failed broadcasting to {node.hostname}: {e}")
                except requests.exceptions.HTTPError as e:
                    logging.info(f"Failed broadcasting to {node.hostname}: {e}")
        return broadcasted_node

