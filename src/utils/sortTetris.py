# basic script to sort by TILJSZO

''''''
PIECEVALS = {
    'T': 1,
    'I': 2,
    'L': 3,
    'J': 4,
    'S': 5,
    'Z': 6,
    'O': 7,
}

def sortQueue(queue: str) -> str:
    '''
    Sort a queue with TILJSZO ordering

    Parameter:
        queue (str): A queue with pieces in {T,I,L,J,S,Z,O}

    Return:
        str: a sorted queue following TILJSZO ordering

    '''

    sortedQueueGen = sorted(queue, key=lambda x: PIECEVALS[x])
    sortedQueue = ''.join(list(sortedQueueGen))

    return sortedQueue


if __name__ == "__main__":
    print(sortQueue("TZJSITL"))
