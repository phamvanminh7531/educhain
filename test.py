from core.io_blockchain import BlockchainMemory

class A:
    def __init__(self):
        blockchain_memory = BlockchainMemory()
        self.blockchain = blockchain_memory.get_blockchain_from_memory()

aa = A()

while True:
    try:
        print(len(BlockchainMemory().get_blockchain_from_memory()))
    except:
        print("Err")
        continue
    print(len(aa.blockchain))
    print('-----')