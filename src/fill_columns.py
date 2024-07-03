# Fill out the rest of the columns and verify columns are reasonable

from utils.constants import FILENAMES, BUILDDELIMITOR
from utils.fileReader import queryWhere
from utils.formulas import LONUM2PCNUM
from utils.queue_utils import BAG, PIECEVALS, sort_queue
from utils.fumen_utils import get_pieces
from collections import Counter
import re

def generate_id(row: dict) -> str:
    '''
    Generate an id for a given row

    Expected Filled:
        Leftover
        Build

    Parameters:
        row (dict): row in database

    Return:
        hexadecimal id for that setup
    '''

    # check if leftover and build follow expected format
    if not re.match(f"[{BAG}]+", row["Leftover"]):
        raise ValueError("Leftover does not follow expected format of pieces TILJSZO")
    if not re.match(f"([{BAG}]{BUILDDELIMITOR}?)+", row["Build"]):
        raise ValueError("Build does not follow expected format of pieces TILJSZO delimitated by semicolon for multiple setups")

    # id based on leftover and first part of build
    leftover = row["Leftover"]
    build = row["Build"].split(BUILDDELIMITOR)[0]

    leftover_piece_counts = Counter(leftover)
    build_piece_counts = Counter(build)

    # PC number
    pc_num: str = bin(LONUM2PCNUM(len(leftover)))[2:].zfill(3)

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
    build_length: str = bin(len(build))[2:].zfill(4)

    # get piece counts
    piece_counts_binary = "".join((bin(build_piece_counts[piece])[2:].zfill(2) if piece in build_piece_counts else "00" for piece in BAG))

    # unique id
    # TODO: get the unique id for this setup
    unique_id: str = '1' * 8

    # 1 + 3 + 3 + 7 + 4 + 14 + 8
    binary_id = first_bit + pc_num + duplicate_piece + piece_existance + build_length + piece_counts_binary + unique_id

    return binary_id

def generate_build(row: dict) -> str:
    '''
    Compute the pieces in the setup

    Expected Filled:
        Setup

    Parameters:
        row (dict): row in database

    Return:
        pieces in the setup
    '''

    build: str

    # get the pieces from the setup
    pieces = get_pieces(row["Setup"])
    build_lst = list(map(sort_queue, map("".join, map(str, pieces))))

    if len(set(build_lst)) == 1:
        build = build_lst[0]
    else:
        build = BUILDDELIMITOR.join(build_lst)

    return build

def generate_cover_dependence(row: dict) -> str:
    '''
    Generate a default cover dependence for the row

    Expected Filled:
        Leftover
        Build

    Parameters:
        row (dict): row in database
    '''

    cover_dependence: str = ""

    # count pieces in leftover
    leftover_prefix: str = ""
    leftover_counter = Counter(row["Leftover"])
    duplicate: tuple[str, int] = leftover_counter.most_common(1)[0]

    if duplicate[1] == 2:
        leftover_prefix = f"{duplicate[0]},[{''.join(leftover_counter.keys())}]!"
    else:
        if row["Leftover"] == "TILJSZO":
            leftover_prefix = "*p7"
        else:
            leftover_prefix = f"[{row["Leftover"]}]!"

    pieces_used: str = ""
    for build in row["Build"].split(BUILDDELIMITOR):
        build_counter = Counter(build)

        # other pieces used in the setup
        pieces_used += "".join((build_counter - leftover_counter).elements())

    cover_dependence = leftover_prefix + f",*p{len(pieces_used) + 1}{{{pieces_used}=1}}"

    return cover_dependence

def fill_columns(db: list[dict], print_disprepancy: bool = True) -> None:
    '''
    Modify database data to fill out rest of default columns, excluding Leftover, Setup, Previous Setup, and Next Setup, which first two are required.
    If a column has already been filled out, no change will be made.

    Expected Filled:
        Leftover
        Setup

    Parameters:
        db (list): a list of the rows in the database
        print_disprepancy (bool) - whether to print disprepancies (Build, Cover Data, Solve %, Solve Fraction)
    '''

    def update(row: dict, key: str, func, cond = lambda old, new: new != old):
        if print_disprepancy or not row[key]:
            new = func()

            if print_disprepancy and row[key] and cond(row[key], new):
                print(f"Computed '{key}' differs '{row[key]}' -> '{new}' in {row}")
            else:
                row[key] = new

    for row in db:
        # check if the necessary columns are filled
        if not (row["Leftover"] and row["Setup"]):
            raise ValueError(f"Required fields 'Leftover' and 'Setup' are missing in {row}")

        # fill build
        update(row, "Build", 
               lambda: generate_build(row),
               lambda old, new: new != old.split(BUILDDELIMITOR)[0])

        # fill id
        update(row, "ID", lambda: generate_id(row))

        # cover dependence based on leftover and build
        update(row, "Cover Dependence", lambda: generate_cover_dependence(row))

    
if __name__ == "__main__":
    from utils.constants import FILENAMES
    from utils.fileReader import openFile
    import csv

    db = openFile("input/db.tsv")

    fill_columns(db)

    outfile = open("output/filled_columns.tsv", "w")

    fieldnames = db[0].keys()
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')

    writer.writeheader()
    writer.writerows(db)

    outfile.close()

