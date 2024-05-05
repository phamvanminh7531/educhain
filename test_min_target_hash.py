import random
import time
import json
from core.utils import calculate_hash
from datetime import datetime

target_hash = '0x7aff850000000000000000000000000000000000000000000000000000'
diff = int(target_hash, 16)


noonce = 0



start = time.time()

while True:
    noonce = noonce + 1

    data_for_hash = {
    'time': datetime.timestamp(datetime.now()),
    'data' : 'test_target_hash',
    'nonnce': noonce
        }

    curr_hash = calculate_hash(json.dumps(data_for_hash))
    
    print("Current hash: ", curr_hash)

    if int(curr_hash, 16) <= diff:
        end = time.time()
        print("Done! with hash: ", curr_hash)
        print("The time of execution of above program is :", (end-start), "s")
        break