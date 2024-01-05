# various functions related to queues

import re
from py_fumen_py import Mino
from .pieces import extendPieces

MINOVALS = {
    Mino.T: 1,
    Mino.I: 2,
    Mino.L: 3,
    Mino.J: 4,
    Mino.S: 5,
    Mino.Z: 6,
    Mino.O: 7,
}

PIECEVALS = {
    'T': 1,
    'I': 2,
    'L': 3,
    'J': 4,
    'S': 5,
    'Z': 6,
    'O': 7,
}

MIRRORPIECES = {
    'L': 'J',
    'J': 'L',
    'S': 'Z',
    'Z': 'S',
}

def sort_queue(queue: str) -> str:
    '''
    Sort a queue with TILJSZO ordering

    Parameter:
        queue (str): A queue with pieces in {T,I,L,J,S,Z,O}

    Return:
        str: a sorted queue following TILJSZO ordering

    '''

    sorted_queue_gen = sorted(queue, key=lambda x: PIECEVALS[x])
    sorted_queue = ''.join(list(sorted_queue_gen))

    return sorted_queue

def sort_queues(queues: list[str]) -> list[str]:
    '''
    Sort a list of queues with TILJSZO ordering

    Parameter:
        queues (list[str]): a list of queues

    Return:
        list[str]: sorted list of queues
    '''

    # create function to set value for the queue 
    queue_val = lambda q: int(''.join(
                        (str(PIECEVALS[p]) for p in q)
                        ))

    sorted_queues = sorted(queues, key=queue_val)
    
    return sorted_queues

def mirror_queue(queue: str) -> str:
    '''
    Mirrors the pieces in the queue and sorts them again

    Parameter:
        queue (str): A queue with pieces in {T,I,L,J,S,Z,O}

    Return:
        str: the pieces mirrored and sorted again

    '''

    new_queue = ""

    # go through each piece and change to mirror if there is one
    for piece in queue:
        if piece in MIRRORPIECES:
            new_queue += MIRRORPIECES[piece]
        else:
            new_queue += piece

    return sort_queue(new_queue)    

def mirror_pattern(pattern: str) -> str:
    '''
    Mirrors the pieces in the pattern

    Parameter:
        pattern (str): an extended pieces pattern

    Return:
        str: a mirrored extended pieces pattern

    '''

    new_pattern = ""

    # go through each piece and change to mirror if there is one
    for char in pattern:
        if char in MIRRORPIECES:
            new_pattern += MIRRORPIECES[char]
        else:
            new_pattern += char

    return new_pattern

def extended_pieces_equals(pattern1: str, pattern2: str) -> bool:
    '''
    Check if two extended pieces are equal

    Parameter:
        pattern1 (str): a extended pieces pattern
        pattern2 (str): a extended pieces pattern

    Return:
        bool: whether the two patterns are equal
    '''

    # if coming from the database, could separated by colons
    pattern1_split = split_colon_extended_pieces(pattern1)
    pattern2_split = split_colon_extended_pieces(pattern2)

    for pattern1_part, pattern2_part in zip(pattern1_split, pattern2_split):
        # compute the two queues
        queues1 = extendPieces(pattern1_part)
        queues2 = extendPieces(pattern2_part)

        # compare each queue one by one
        for q1, q2 in zip(queues1, queues2):
            if q1 != q2:
                return False

    return True

def split_colon_extended_pieces(pattern: str) -> list[str]:
    '''
    Split by colon for extended pieces found in database

    Parameter:
        pattern (str): a extended pieces pattern

    Return:
        list: a list of extended pieces
    '''

    splitted_pattern = map("".join, re.findall("(.+?{.*?}):|([^{}]+?):|(.+?)$", pattern))

    return list(splitted_pattern)
