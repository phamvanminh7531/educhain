from memory.memory_path import TARGET_HASH_CONF_DIR
import logging
import json
from core.block import Block, BlockHeader

class TargetHashControl:
    def __init__(self):
        self.target_hash_conf_file = TARGET_HASH_CONF_DIR
    
    def calculate_target_hash_first(self, blockchain: Block):
        logging.info("First calculate target hash")
        difficulty = blockchain.block_header.difficulty
        with open(self.target_hash_conf_file, 'r+') as f:
            target_config = json.load(f)

            max_target = int(target_config["max_target"], 16)
            current_target = max_target / difficulty
            current_target_hex = hex(int(current_target))

            target_config["current_target"] = current_target_hex
            f.seek(0)
            json.dump(target_config, f, indent=2)
            f.truncate()
    
    def get_current_target(self):
        with open(self.target_hash_conf_file) as f:
            target_config = json.load(f)
        return target_config["current_target"]
    
    def get_max_target(self):
        with open(self.target_hash_conf_file) as f:
            target_config = json.load(f)
        return target_config["max_target"]

    def checking_time_for_recalculate(self, blockchain: Block):
        print("Checking")
        logging.info("Checking block for recalculate target hash")
        with open(self.target_hash_conf_file) as f:
            target_config = json.load(f)
        if (blockchain.block_header.height % target_config["len_of_block_recal"]) == 0 and blockchain.block_header.height!=0:
            self.target_hash_recalculate(blockchain)
        else:
            return None
    
    def target_hash_recalculate(self, blockchain: Block):
        print("Calculating")
        logging.info("Recalculate nexttarget hash")
        with open(self.target_hash_conf_file, 'r+') as f:
            target_config = json.load(f)
            blockchain = blockchain.to_dict
            # get timestamp of block
            actual = blockchain[0]['header']['timestamp'] - blockchain[target_config["len_of_block_recal"]-1]['header']['timestamp']
            expected = target_config["len_of_block_recal"] * target_config["time"] * 60
            raito = actual / expected
            raito = 0.25 if raito < 0.25 else raito
            raito = 4 if raito > 4 else raito

            new_target_hash = hex(int(int(target_config["current_target"], 16) * raito))
            new_target_hash = target_config["max_target"] if int(new_target_hash, 16) > int(target_config["max_target"], 16) else new_target_hash

            target_config["current_target"] = new_target_hash
            f.seek(0)
            json.dump(target_config, f, indent=2)
            f.truncate()
    
    @property
    def get_current_difficulty(self):
        with open(self.target_hash_conf_file, 'r+') as f:
            target_config = json.load(f)
        difficulty = int(target_config["max_target"], 16) / int(target_config["current_target"], 16)
        return difficulty