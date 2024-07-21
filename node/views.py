import logging
import json
from memory.memory_path import MY_HOSTNAME
from core.io_blockchain import BlockchainMemory
from core.io_known_nodes import KnownNodesMemory
from core.transaction_validation import TransactionValidation, TransactionException
from core.block_validation import BlockValidation, NewBlockException
from core.node import Node
from core.network import Network
from core.io_mem_pool import MemPool
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

memory_pool = MemPool()
blockchain_memory = BlockchainMemory()
my_node = Node(MY_HOSTNAME)
network = Network(my_node)
network.join_network()

# Create your views here.
@api_view(['POST'])
def validate_transaction(request):
    logging.info("New transaction validation request")
    data=request.data
    blockchain_base = blockchain_memory.get_blockchain_from_memory()
    try:
        transaction_validate = TransactionValidation(blockchain=blockchain_base, hostname=MY_HOSTNAME)
        transaction_validate.receive(data["transaction"], data["sender"])
        if transaction_validate.is_new:
            transaction_validate.validate()
            transaction_validate.store()
            transaction_validate.broadcast()
    except TransactionException as transaction_exception:
        return Response(f"{transaction_exception}", status = status.HTTP_406_NOT_ACCEPTABLE)
    return Response(data)

@api_view(['POST'])
def validate_block(request):
    data = request.data
    blockchain_base = blockchain_memory.get_blockchain_from_memory()
    try:
        block = BlockValidation(blockchain=blockchain_base, hostname=MY_HOSTNAME)
        block.receive(data["block"], data["sender"])
        block.validate()
        block.add_new_block_to_blockchain()
        block.clear_block_transactions_from_mempool()
        block.broadcast()
    except (NewBlockException, TransactionException) as new_block_exception:
        return Response(f"{new_block_exception}", status = status.HTTP_406_NOT_ACCEPTABLE)
    return Response(data, status = status.HTTP_200_OK)

@api_view(['POST'])
def new_node_advertisement(request):
    logging.info("New node advertisement request")
    data=request.data
    hostname = data["hostname"]
    known_nodes_memory = KnownNodesMemory()
    try:
        new_node = Node(hostname)
        known_nodes_memory.store_new_node(new_node)
    except TransactionException as transaction_exception:
        return Response(f'{transaction_exception}', status = status.HTTP_400_BAD_REQUEST)
    return Response(data, status = status.HTTP_200_OK)

@api_view(['GET'])
def known_node_request(request):
    logging.info("Known node request")
    return Response(network.return_known_nodes(), status = status.HTTP_200_OK)

@api_view(['GET'])
def get_blockchain(request):
    logging.info("Block request")
    blockchain_base = blockchain_memory.get_blockchain_from_memory()
    return Response(blockchain_base.to_dict, status = status.HTTP_200_OK)

@api_view(['GET'])
def get_transaction_in_pool(request):
    logging.info("Transaction in memory pool request")
    transactions = memory_pool.get_transactions_from_memory()
    return Response(transactions, status = status.HTTP_200_OK)

@api_view(['GET'])
def get_user_txids(request, user_code):
    logging.info("get user txids")
    blockchain_base = blockchain_memory.get_blockchain_from_memory()
    return Response(blockchain_base.get_user_txids(user_code=user_code), status = status.HTTP_200_OK)

@api_view(['GET'])
def get_transaction(request, txid):
    logging.info("get transaction")
    blockchain_base = blockchain_memory.get_blockchain_from_memory()
    return Response(blockchain_base.get_transaction(txid=txid), status = status.HTTP_200_OK)


@api_view(['GET'])
def reset(request):
    """
    This function just help for testing
    """
    init_block = [{"header": {"height": 0,
   "previous_block_hash": "0000000000000000000000000000000000000000000000000000000000000000",
   "merkle_root": "b0fc67989fccb5f52be2c84a54315e7da39d0c8b00d4f69a153aa71fc4b6aa6e",
   "timestamp": 1718114179.584697,
   "noonce": 24788963,
   "difficulty": 1.0,
   "hash": "000000473719e64fa65412fd93266da4ba751b45325cfd1cad6082ca2e7d49a3"},
  "transactions": [{"txid": "1bc58c69e52a4d86cbd035f1313af0327336e4a1d1b7b1694fa64453881d2f09",
    "timestamp": 1714409526.490535,
    "data": {"Genesis": "I wanna chain our education system - PVM"}}]}]
    blockchain_memory = BlockchainMemory()
    blockchain_memory.store_blockchain_dict_in_memory(init_block)
    known_nodes_memory = KnownNodesMemory()
    known_nodes_memory.store_known_nodes([])
    memory_pool = MemPool()
    memory_pool.clear_transactions_from_memory()
    my_node = Node(MY_HOSTNAME)
    network = Network(my_node)
    network.join_network()
    return Response({"result": "reset ok"}, status = status.HTTP_200_OK)

