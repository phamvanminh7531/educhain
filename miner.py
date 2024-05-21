import logging
import os
import time
from core.io_mem_pool import MemPool
from core.new_block_creation import ProofOfWork, BlockException
from core.io_blockchain import BlockchainMemory
from memory.memory_path import MY_HOSTNAME

logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s: %(message)s')


def main():
    mempool = MemPool()
    mempool.clear_transactions_from_memory()


    while True:
        pow = ProofOfWork(MY_HOSTNAME)
        try:
            pow.create_new_block()
            pow.clear_block_transactions_from_mempool()
            pow.broadcast()
        except BlockException:
            logging.info("No transaction in mem pool")
        time.sleep(2)


if __name__ == "__main__":
    main()
