# Quasi SQL program with just select, from, and where using tsv files

import re
from typing import Callable
from csv import DictReader
from bisect import bisect_left, bisect_right
from functools import cmp_to_key
from typing import Any

DEFAULT_COMPARE = lambda x, y: (x > y) - (x < y)
DEFAULT_EQUALS = lambda x, y: x == y

def compareQueues(q1: str, q2: str) -> int:
    '''
    Determine if a queue is less than another queue following if duplicate follow TILJSZO, then TILJSZO, then longest

    Parameters:
        q1 (str): A tetris format queue
        q2 (str): A tetris format queue

    Returns:
        -1 if q1 < q2
        0 if q1 == q2
        1 if q1 > q2
    '''

    # in the database length is lower precedence

    # dict assigning value for each piece
    # TODO: Remove this piece vals
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
        return -1
    if pieceVals[dupPiece1] > pieceVals[dupPiece2]:
        return 1

    # Go through each piece from left to right
    for p1, p2 in zip(q1, q2):

        # if piece in q1 is less than piece in q2
        if pieceVals[p1] < pieceVals[p2]:
            return -1

        # if piece in q1 is greater than piece in q2
        elif pieceVals[p1] > pieceVals[p2]:
            return 1

        # otherwise same piece

    # comparing the lengths of the queues
    # a longer queue is less than a shorter queue
    if len(q1) > len(q2):
        return -1
    elif len(q1) < len(q2):
        return 1

    # exactly the same queues
    return 0

# dict for column to the comparison function
COL2COMPARE = {
    "ID": DEFAULT_COMPARE,
    "Leftover": compareQueues,
}

def linearSearch(text: str, 
                 db: list[dict],
                 column_name: str,
                 op: str,
                 equals: Callable[[str, str], bool] = DEFAULT_EQUALS
                 ) -> list[int]:
    '''
    Determine if text is within the list with binary search

    Parameters:
        text (str): a string to be found in the list
        db (list): a list of rows in the format of a dictionary
        op (str): operator that should be only = and <>
        column_name (str): name of the column to binary search

    Returns:
        list[int]: indices where text was found

    '''

    # determine the right function
    if op == "=":
        operation = equals
    elif op == "<>":
        operation = lambda x, y: not equals(x, y)
    else:
        # issue
        raise ValueError(f"Got an invalid operator for linear search '{op}'")

    indices = []

    # go through all of db
    for i, row in enumerate(db):
        # if the element in the list is the same as text
        if operation(text, row[column_name]):
            indices.append(i)

    return indices


def getMatchingRange(text: str,
                     db: list[dict],
                     column_name: str,
                     op: str, compare: Callable[[Any, Any], int],
                     ) -> list[tuple[int, int]]:
    '''
    Get the ranges where text is satisfies by the operator in the list

    Parameters:
        text (str): a string to be found in the list
        db (list): a list of rows in the format of a dictionary
        column_name (str): name of the column to binary search
        op (str): a operator in {<>, >=, <=, <, >, =}
        compare (func): a compare functional obj that returns a boolean when comparing strings

    Return:
        list: a list of indices where each pair represents start and end of a range exclusive of end

    '''
   
    # do the simple operators to handle
    startIndex = 0
    endIndex = len(db)

    key_func = lambda x: cmp_to_key(compare)(x[column_name])

    if op == "<=":
        endIndex = bisect_right(db, cmp_to_key(compare)(text), key=key_func)

    elif op == ">=":
        startIndex = bisect_left(db, cmp_to_key(compare)(text), key=key_func)

    elif op == "<":
        endIndex = bisect_left(db, cmp_to_key(compare)(text), key=key_func)

    elif op == ">":
        startIndex = bisect_right(db, cmp_to_key(compare)(text), key=key_func)

    elif op == "=":
        startIndex = bisect_left(db, cmp_to_key(compare)(text), key=key_func)
        endIndex = bisect_right(db, cmp_to_key(compare)(text), key=key_func)

    # edge case for <> which isn't just a start and end
    elif op == "<>":
        startIndex2 = bisect_right(db, cmp_to_key(compare)(text), key=key_func)
        endIndex1 = bisect_left(db, cmp_to_key(compare)(text), key=key_func)

        return [(0, endIndex1), (startIndex2, len(db))]

    return [(startIndex, endIndex)]

def openFile(filepath: str) -> list[dict]:
    '''
    Get all rows from file as a list of dictionaries representing a row

    Parameters:
        filepath (str): the filepath of a tsv database file

    Return:
        list[dict]: list of rows from the file
    '''

    # get data from the file
    with open(filepath, "r") as infile:
        db = list(DictReader(infile, delimiter="\t"))

    return db

def queryWhere(db: list[dict], 
               where: str = "", 
               compare: Callable[[str, str], bool] = DEFAULT_COMPARE,
               equals: Callable[[str, str], bool] = DEFAULT_EQUALS,
               ) -> list[dict]:
    '''
    Get all rows with the specific column filtering with where

    Parameters:
        db (list): a list of rows in the format of a dictionary
        where (str): expression of in format column operator value
        compare (func): function to compare for binary search
        equals (func): function to compare for linear search

    Return:
        list[dict]: list of filtered rows from where
    '''
    
    if len(db) == 0:
        return db

    # parse the where
    if where:
        operators = ["<>", ">=", "<=", "<", ">", "="]
        where_col, op, val = re.split(f"({'|'.join(operators)})", where)    

        # set compare to default compare function if the column has one
        is_default_compare = True
        if where_col in COL2COMPARE and compare is DEFAULT_COMPARE:
            compare = COL2COMPARE[where_col]
            is_default_compare = False

        # if compare has been changed or a compare was passed in
        if not is_default_compare or compare is not DEFAULT_COMPARE:
            indices = getMatchingRange(val, db, where_col, op, compare=compare)

            # filtered out the rows
            rows = []
            for start, end in indices:
                rows += db[start: end]

            db = rows

        else:
            indices = linearSearch(val, db, where_col, op, equals=equals)

            # filtered out the rows
            db = [db[i] for i in indices]

    return db

if __name__ == "__main__":
    print(queryWhere(openFile("../../tsv/2ndPC.tsv"), "Leftover=SSZO"))
