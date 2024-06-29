# Various functions representing useful calculations
def hex2bin(hex_string: str) -> str:
    '''
    Convert a hexadecimal string into binary preserving leading zeros
    '''

    length = (len(hex_string) - 1) * 4 
    binary = (bin(int(hex_string[:-1], 16))[2:]).zfill(length)

    # add last hex digit
    binary += (bin(int(hex_string[-1], 16))[2:]).zfill(4)

    return binary


def bin2hex(binary: str) -> str:
    '''
    Convert a binary string into uppercase hex preserving leading zeros
    '''

    # add number of trailing zeros to be multiple of 4
    length = (len(binary) + 3) // 4

    hex_digits = '%.*x' % (length, int(binary, 2))

    return hex_digits.upper()

def PCNUM2LONUM(pcNum: int) -> int:
    '''
    Convert a given pc number to the length of leftover

    Parameters:
        pcNum(int): a pc number in range 1-9

    Return:
        int: a length of the leftover in range 1-7
    '''
    
    return ((pcNum * 4) + 2) % 7 + 1

def LONUM2PCNUM(leftoverNum: int) -> int:
    '''
    Convert a given length of leftover to pc number
    
    Parameters:
        leftoverNum(int): length of the leftover in range 1-7

    Return:
        int: a pc number in range 1-7
    '''

    return (leftoverNum * 2) % 7 + 1

def PCNUM(pieces: int, minos: int = 0) -> int:
    '''
    Compute the pc number from the number of pieces placed and number of minos already on board

    Undefined behavior if minos is odd
    
    Parameters:
        pieces(int): number of pieces placed
        minos(int): number of minos on board (default 0 for empty board)

    Return:
        int: a pc number in range 1-7
    '''

    # simplify calculations a bit by modulo 7 for pieces
    pieces %= 7

    # the effective number of pieces placed onto the board 
    minos2pieces = 3 * (minos % 4) + 2 * (minos % 7)

    # the effective number of total pieces 
    effectivePieces = (pieces - minos2pieces) % 7

    # pc number
    pcNum = (5 * effectivePieces) % 7 + 1

    return pcNum

if __name__ == "__main__":
    print(PCNUM2LONUM(1))
    print(LONUM2PCNUM(7))
    print(hex2bin("34DFD7"))
