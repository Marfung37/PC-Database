# Quasi SQL program with just select, from, and where using tsv files

import re
from csv import DictReader

def queryWhere(filepath: str, columns: list[str], where: str = "") -> list[list[str]]:
    '''
    Get all rows with the specific column filtering with where

    Parameters:
        filepath(str): path for a tsv file
        columns(str): names of columns to return
        where(str): expression of in format column operator value

    Return:
        list[list[str]]: list of rows with a list of corresponding columns values
    '''

    # get data from the file
    with open(filepath, "r") as infile:
        db = list(DictReader(infile))

    # parse the where
    operators = ["<>", ">=", "<=", "<", ">", "="]
    whereCol, op, val = re.split(f"({'|'.join(operators)})", where)

    
    
    # Temp return
    return [[""]]



def compareQueues(q1: str, q2: str) -> bool:
    '''
    Determine if a queue is less than another queue following TILJSZO order

    Parameters:
        q1 (str): A tetris format queue
        q2 (str): A tetris format queue

    Returns:
        bool: Whether q1 is less than q2

    '''

    # in the database length is lower precedence

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
        elif pieceVals[p1] < pieceVals[p2]:
            return False

        # otherwise same piece

    # comparing the lengths of the queues
    # a longer queue is less than a shorter queue
    if len(q1) > len(q2):
        return True
    elif len(q1) < len(q2):
        return False

    # exactly the same queues
    return False

def binarySearch(queue: str, queueLst: list[str], compare = compareQueues) -> bool:
    '''
    Determine if a queue is within the list of queues with binary search

    Parameters:
        queue (str): A tetris format queue
        queueLst (list): A list of tetris format queues sorted by TILJSZO

    Returns:
        bool: Whether the queue was found in the list

    '''

    low = 0
    high = len(queueLst)

    while(low != high):
        mid = (low + high) // 2

        # check if queue was found already
        if queue == queueLst[mid]:
            return True

        # check if less than
        if compare(queue, queueLst[mid]):
            high = mid - 1
        else:
            low = mid + 1

    # final check if the queue was found
    return queue == queueLst[low]


