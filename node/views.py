import logging
import json
from memory.memory_path import MY_HOSTNAME
from core.io_blockchain import BlockchainMemory
from core.io_known_nodes import KnownNodesMemory
from core.transaction_validation import TransactionValidation, TransactionException
from core.block_validation import BlockValidation, NewBlockException
from core.node import Node
from core.network import Network
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


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
        transaction_validate.receive(data["transaction"])
        if transaction_validate.is_new:
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
        block.receive(data["block"])
        block.validate()
        block.add_new_block_to_blockchain()
        block.clear_block_transactions_from_mempool()
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
