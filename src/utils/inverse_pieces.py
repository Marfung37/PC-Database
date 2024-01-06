# Script that is inverse function of extendPieces

from .pieces import extendPieces
from typing import Callable

def matching_queue(queue: str, pattern: str, equality: Callable[[str, str], bool] = lambda x, y: x == y) -> int:
    '''
    Find where a queue is within the extended pieces
    
    Parameters:
        queue (str): A tetris format queue
        pattern (str): A pattern for extended pieces

    Returns:
        int: index where the queue was found in the extended pieces

    '''

    # check if valid input
    validPieces = set("TILJSZO")
    for piece in queue:
        if piece not in validPieces:
            raise ValueError(f"The piece '{piece}' is not a valid piece")

    # get a generator obj of the output queues
    outQueues = extendPieces(pattern)

    return binary_search(queue, list(outQueues), equality=equality)

def compare_queues(q1: str, q2: str) -> bool:
    '''
    Determine if a queue is less than another queue following TILJSZO order

    Parameters:
        q1 (str): A tetris format queue
        q2 (str): A tetris format queue

    Returns:
        bool: Whether q1 is less than q2

    '''

    # dict assigning value for each piece
    pieceVals = {
        'T': 1,
        'I': 2,
        'L': 3,
        'J': 4,
        'S': 5,
        'Z': 6,
        'O': 7,
    }

    # Go through each piece from left to right
    for p1, p2 in zip(q1, q2):

        # if piece in q1 is less than piece in q2
        if pieceVals[p1] < pieceVals[p2]:
            return True

        # if piece in q1 is greater than piece in q2
        elif pieceVals[p1] > pieceVals[p2]:
            return False

        # otherwise same piece

    # exactly the same queues
    return False

def binary_search(queue: str, 
                 queue_lst: list[str], 
                 compare: Callable[[str, str], bool] = compare_queues, 
                 equality: Callable[[str, str], bool] = lambda x, y: x == y) -> int:
    '''
    Find where a queue is found to be started with in the list of queues with binary search

    Parameters:
        queue (str): A tetris format queue
        queue_lst (list): A list of tetris format queues sorted by TILJSZO
        compare (func): a compare functional obj that returns a boolean when comparing queues
        equality (func): a equality functional obj that returns boolean when two queues are equal

    Returns:
        int: index where the queue was found in the list and -1 if not found

    '''
    low = 0
    high = len(queue_lst) - 1

    while low <= high:
        mid = low + (high - low) // 2

        # check if queue was found already
        if equality(queue_lst[mid], queue):
            return mid

        # check if less than
        if compare(queue, queue_lst[mid]):
            high = mid - 1
        else:
            low = mid + 1

    return -1
