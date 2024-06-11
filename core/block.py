import json


from core.utils import calculate_hash
from core.merkle_tree import get_transaction_proof


class BlockHeader:
    """
    Define a block header class to store infomation
    """
    def __init__(self, height: int, previous_block_hash: str, merkle_root: str, timestamp: float, noonce: int, difficulty: float, hash = None):
        self.height = height
        self.previous_block_hash = previous_block_hash
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.noonce = noonce
        self.difficulty = difficulty
        if hash:
            self.hash = hash
        else:
            self.hash = self.get_hash()

    def __eq__(self, other):
        try:
            assert self.previous_block_hash == other.previous_block_hash
            assert self.merkle_root == other.merkle_root
            assert self.timestamp == other.timestamp
            assert self.noonce == other.noonce
            assert self.difficulty == other.difficulty
            assert self.hash == other.hash
            return True
        except AssertionError:
            return False

    def get_hash(self) -> str:
        header_data = {"previous_block_hash": self.previous_block_hash,
                       "merkle_root": self.merkle_root,
                       "timestamp": self.timestamp,
                       "noonce": self.noonce}
        return calculate_hash(json.dumps(header_data))

    @property
    def to_dict(self) -> dict:
        return {
            "height": self.height,
            "previous_block_hash": self.previous_block_hash,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "noonce": self.noonce,
            "difficulty": self.difficulty,
            "hash": self.hash,
        }

    def __str__(self):
        return json.dumps(self.to_dict)

    @property
    def to_json(self) -> str:
        return json.dumps(self.to_dict)


class Block:
    """
    Block
    """
    def __init__(self, transactions: list, block_header: BlockHeader, previous_block=None):
        self.block_header = block_header
        self.transactions = transactions
        self.previous_block = previous_block

    def __eq__(self, other):
        try:
            assert self.block_header == other.block_header
            assert self.transactions == other.transactions
            return True
        except AssertionError:
            return False

    def __len__(self) -> int:
        i = 1
        current_block = self
        while current_block.previous_block:
            i = i + 1
            current_block = current_block.previous_block
        return i

    def __str__(self):
        return json.dumps({"timestamp": self.block_header.timestamp,
                           "hash": self.block_header.hash,
                           "transactions": self.transactions})
    @property
    def to_dict(self):
        block_list = []
        current_block = self
        while current_block:
            block_data = {
                "header": current_block.block_header.to_dict,
                "transactions": current_block.transactions
            }
            block_list.append(block_data)
            current_block = current_block.previous_block
        return block_list
    
    def get_user_txids(self, user_code: str):
        return_dict = {
            "user_code": user_code,
            "txids": []
        }
        current_block = self
        while current_block.previous_block:
            for transaction in current_block.transactions:
                if transaction["data"]["student_code"] == user_code:
                    return_dict["txids"].append(transaction["txid"])
            current_block = current_block.previous_block
        return return_dict
    
    def get_transaction(self, txid: str):
        return_dict = {}
        current_block = self
        while current_block.previous_block:
            for transaction in current_block.transactions:
                if transaction["txid"] == txid:
                    return_dict["transaction"] = transaction
                    return_dict["merkle_root"] = current_block.block_header.merkle_root
                    return_dict["merkle_proof"] = get_transaction_proof(
                                                        transactions = current_block.transactions,
                                                        txid = txid
                                                        )
            current_block = current_block.previous_block
        return return_dict