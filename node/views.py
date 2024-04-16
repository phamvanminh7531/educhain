import logging
import json
from core.io_blockchain import BlockchainMemory
from core.transaction_validation import TransactionValidation, TransactionException
from core.block_validation import BlockValidation, NewBlockException
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


blockchain_memory = BlockchainMemory()

# Create your views here.
@api_view(['POST'])
def validate_transaction(request):
    logging.info("New transaction validation request")
    data=request.data
    blockchain_base = blockchain_memory.get_blockchain_from_memory()
    try:
        transaction_validate = TransactionValidation(blockchain=blockchain_base)
        transaction_validate.receive(data["transaction"])
        if transaction_validate.is_new:
            transaction_validate.store()
    except TransactionException as transaction_exception:
        return Response(f"{transaction_exception}", status = status.HTTP_406_NOT_ACCEPTABLE)
    return Response(data)

@api_view(['POST'])
def validate_block(request):
    data = request.data
    blockchain_base = blockchain_memory.get_blockchain_from_memory()
    try:
        block = BlockValidation(blockchain=blockchain_base)
        block.receive(data["block"])
        block.validate()
        block.add_new_block_to_blockchain()
        block.clear_block_transactions_from_mempool()
    except (NewBlockException, TransactionException) as new_block_exception:
        return Response(f"{new_block_exception}", status = status.HTTP_406_NOT_ACCEPTABLE)
    return Response(data)