# Quasi SQL program with just select, from, and where using tsv files

import re
from typing import Callable
from csv import DictReader

def compareQueues(q1: str, q2: str) -> bool:
    '''
    Determine if a queue is less than another queue following if duplicate follow TILJSZO, then TILJSZO, then longest

    Parameters:
        q1 (str): A tetris format queue
        q2 (str): A tetris format queue

    Returns:
        bool: Whether q1 is less than q2

    '''

    # in the database length is lower precedence

    # dict assigning value for each piece
    pieceVals = {
        '': 0,
        'T': 1,
        'I': 2,
        'L': 3,
        'J': 4,
        'S': 5,
        'Z': 6,
        'O': 7,
    }

    # check if duplicate
    dupPiece1 = ""
    dupPiece2 = ""
    for i in range(len(q1) - 1):
        if q1[i] == q1[i+1]:
            dupPiece1 = q1[i]
    for i in range(len(q2) - 1):
        if q2[i] == q2[i+1]:
            dupPiece2 = q2[i]

    # compare the duplicate pieces
    if pieceVals[dupPiece1] < pieceVals[dupPiece2]:
        return True
    if pieceVals[dupPiece1] > pieceVals[dupPiece2]:
        return False

    # Go through each piece from left to right
    for p1, p2 in zip(q1, q2):

        # if piece in q1 is less than piece in q2
        if pieceVals[p1] < pieceVals[p2]:
            return True

        # if piece in q1 is greater than piece in q2
        elif pieceVals[p1] > pieceVals[p2]:
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

# dict for column to the comparison function
COL2COMPARE = {
    "ID": lambda x, y: x < y,
    "Leftover": compareQueues,
}

def binarySearch(text: str, lst: list[str], compare: Callable[[str, str], bool], dir: str = "left") -> int:
    '''
    Determine if text is within the list with binary search

    Parameters:
        text (str): a string to be found in the list
        lst (list): A sorted list of strings (sorted by the compare)
        compare (func): a compare functional obj that returns a boolean when comparing strings
        dir (str): either "left" or "right" to get left or right edge of range where text is found

    Returns:
        int: index where the text is found and -1 if not

    '''

    low = 0
    high = len(lst)

    while low < high:
        mid = low + (high - low) // 2

        if dir == "right":
            mid += (high - low) % 2

        # check if text was found already
        if text == lst[mid]:
            if dir == "left":
                high = mid

                if mid - 1 < 0 or text != lst[mid - 1]:
                    low = mid

            else:
                low = mid

                if mid + 1 == len(lst) or text != lst[mid + 1]:
                    high = mid

        # check if less than
        elif compare(text, lst[mid]):
            high = mid - 1
        else:
            low = mid + 1

    # final check if the text was found
    if text == lst[low]:
        return low

    # not found
    return -1

def linearSearch(text: str, lst: list[str]) -> list[int]:
    '''
    Determine if text is within the list with binary search

    Parameters:
        text (str): a string to be found in the list
        lst (list): A sorted list of strings (sorted by the compare)

    Returns:
        list[int]: indices where text was found

    '''

    indices = []

    for i, ele in enumerate(lst):
        if text == ele:
            indices.append(i)

    return indices


def getMatchingRange(text: str, lst: list[str], op: str, compare: Callable[[str, str], bool]) -> list[tuple[int, int]]:
    '''
    Get the ranges where text is satisfies by the operator in the list

    Parameters:
        text (str): a string to be found in the list
        lst (list): a sorted list of strings (sorted by the compare)
        op (str): a operator in {<>, >=, <=, <, >, =}
        compare (func): a compare functional obj that returns a boolean when comparing strings

    Return:
        list: a list of indices where each pair represents start and end of a range exclusive of end

    '''
   
    # do the simple operators to handle
    startIndex = 0
    endIndex= len(lst)

    if op == "<=":
        endIndex = binarySearch(text, lst, compare, dir="right") + 1
    elif op == ">=":
        startIndex = binarySearch(text, lst, compare, dir="left")

    elif op == "<":
        endIndex = binarySearch(text, lst, compare, dir="left")
    elif op == ">":
        startIndex = binarySearch(text, lst, compare, dir="right") + 1

    elif op == "=":
        startIndex = binarySearch(text, lst, compare, dir="left")
        endIndex = binarySearch(text, lst, compare, dir="right") + 1

    # edge case for <> which isn't just a start and end
    if op == "<>":
        endIndex1 = binarySearch(text, lst, compare, dir="left")
        startIndex2 = binarySearch(text, lst, compare, dir="right") + 1

        return [(0, endIndex1), (startIndex2, len(lst))]

    return [(startIndex, endIndex)]

def queryWhere(filepath: str, where: str = "") -> list[dict]:
    '''
    Get all rows with the specific column filtering with where

    Parameters:
        filepath(str): path for a tsv file
        where(str): expression of in format column operator value

    Return:
        list[list[str]]: list of rows with a list of corresponding columns values
    '''

    # get data from the file
    with open(filepath, "r") as infile:
        db = list(DictReader(infile, delimiter="\t"))

    # parse the where
    if where:
        operators = ["<>", ">=", "<=", "<", ">", "="]
        whereCol, op, val = re.split(f"({'|'.join(operators)})", where)    

        # check if this column has a comparison function
        colLst = [row[whereCol] for row in db]
        if whereCol in COL2COMPARE:
            indices = getMatchingRange(val, colLst, op, COL2COMPARE[whereCol])

            # filtered out the rows
            rows = []
            for start, end in indices:
                rows += db[start: end]

            db = rows

        else:
            indices = linearSearch(val, colLst)

            db = [db[i] for i in indices]

    return db

if __name__ == "__main__":
    print(queryWhere("../../tsv/2ndPC.tsv", "Leftover=SSZO"))
