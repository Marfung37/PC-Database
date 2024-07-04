# Various functions representing useful calculations

def PCNUM2LONUM(pc_num: int) -> int:
    '''
    Convert a given pc number to the length of leftover

    Parameters:
        pc_num(int): a pc number in range 1-9

    Return:
        int: a length of the leftover in range 1-7
    '''
    
    return ((pc_num * 4) + 2) % 7 + 1

def LONUM2PCNUM(leftover_num: int) -> int:
    '''
    Convert a given length of leftover to pc number
    
    Parameters:
        leftover_num(int): length of the leftover in range 1-7

    Return:
        int: a pc number in range 1-7
    '''

    return (leftover_num * 2) % 7 + 1

def LONUM2BAGCOMP(leftover_num: int) -> list[int]:
    '''
    Generate the bag composition of the pc to 11 pieces

    Parameters:
        leftover_num(int): length of the leftovere in range 1-7

    Return:
        list[int]: number of pieces for each bag in the pc
    '''

    bag_comp: list[int] = [leftover_num]

    while sum(bag_comp) < 11:
        bag_comp.append(min(11 - sum(bag_comp), 7))
    
    return bag_comp

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
    print(LONUM2BAGCOMP(7))
