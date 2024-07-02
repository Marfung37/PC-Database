# Fill out the rest of the columns and verify columns are reasonable

from utils.directories import FILENAMES
from utils.fileReader import queryWhere
from utils.formulas import LONUM2PCNUM
from utils.pieces import BAG
from utils.queue_utils import PIECEVALS
from collections import Counter
import re

def generate_id(row: dict) -> str:
    '''
        Generate an id for a given row

        Parameters:
            row - row in database that should have "Leftover" and "Build"

        Return:
            hexadecimal id for that setup
    '''

    # check if leftover and build follow expected format
    if not re.match(f"[{BAG}]+", row["Leftover"]):
        raise ValueError("Leftover does not follow expected format of pieces TILJSZO")
    if not re.match(f"([{BAG}];?)+", row["Build"]):
        raise ValueError("Build does not follow expected format of pieces TILJSZO delimitated by semicolon for multiple setups")

    # id based on leftover and first part of  build
    leftover = row["Leftover"]
    build = row["Build"].split(";")[0]

    leftover_piece_counts = Counter(leftover)
    build_piece_counts = Counter(build)

    # PC number
    pc_num: str = bin(LONUM2PCNUM(len(leftover))).zfill(3)[2:]

    # edge case that I doubt will ever be used
    four_duplicate: bool = 4 in build_piece_counts.values()
    eigth_pc: bool = pc_num == 1 and 2 in leftover_piece_counts.values()
    first_bit: str = '1' if four_duplicate or eigth_pc else '0'

    # which piece is duplicated in leftover
    duplicates = leftover_piece_counts.most_common(2)

    if duplicates[0][1] > 2: # duplicated more than 2
        raise ValueError(f"Leftover has {duplicates[0][1]} '{duplicates[0][0]}' but there can only be at most 2 of a piece in {row}")
    if duplicates[1][1] > 1: # more than 1 duplicates
        raise ValueError(f"Leftover has '{duplicates[0][0]}' and '{duplicates[1][0]}' duplicated but only one piece can be duplicated in {row}")

    duplicate_piece: str = bin(0 if duplicates[0][1] == 1 else 8 - PIECEVALS[duplicates[0][0]])[2:]
    
    # existance of pieces for sorting
    piece_existance: str = "".join(('1' if piece in leftover else '0' for piece in BAG))

    # length of build
    build_length: str = bin(len(build)).zfill(4)[2:]

    # get piece counts
    piece_counts_binary = "".join((bin(build_piece_counts[piece]).zfill(2)[2:] if piece in build_piece_counts else "00" for piece in BAG))

    # unique id
    unique_id: str = '1' * 8

    binary_id = first_bit + pc_num + duplicate_piece + piece_existance + build_length + piece_counts_binary + unique_id

    return binary_id

if __name__ == "__main__":
    print(len(generate_id({"Leftover": "IILJ", "Build": "ILJ"})))

