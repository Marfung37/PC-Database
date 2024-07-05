# Fill out the rest of the columns and verify columns are reasonable

from utils.constants import FILENAMES, BUILDDELIMITOR, PIECESDELIMITOR
from utils.fileReader import queryWhere, openFile
from utils.formulas import LONUM2PCNUM, LONUM2BAGCOMP
from utils.queue_utils import BAG, PIECEVALS, sort_queue, extended_pieces_equals
from utils.fumen_utils import is_pc
from simple_checks import duplicate_rows, generate_build, sort_db
from collections import Counter
from typing import Callable
import re

IDLEN = 10
NUMPIECESINPC = 10
HOLD = 1
SEE = 7

def generate_id(row: dict, input_db: list[dict]) -> str:
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
    pc_num: int = LONUM2PCNUM(len(row["Leftover"]))
    pc_num_bin: str = bin(pc_num)[2:].zfill(3)

    # edge case that I doubt will ever be used
    four_duplicate: bool = 4 in build_piece_counts.values()
    eigth_pc: bool = pc_num == 1 and 2 in leftover_piece_counts.values()
    first_bit: str = '1' if four_duplicate or eigth_pc else '0'
    if eigth_pc:
        pc_num = 8
        pc_num_bin = bin(0)[2:].zfill(3)

    # which piece is duplicated in leftover
    duplicates = leftover_piece_counts.most_common(2)

    if duplicates[0][1] > 2: # duplicated more than 2
        raise ValueError(f"Leftover has {duplicates[0][1]} '{duplicates[0][0]}' but there can only be at most 2 of a piece in {row}")
    if len(duplicates) == 2 and duplicates[1][1] > 1: # more than 1 duplicates
        raise ValueError(f"Leftover has '{duplicates[0][0]}' and '{duplicates[1][0]}' duplicated but only one piece can be duplicated in {row}")

    duplicate_piece: str = bin(0 if duplicates[0][1] == 1 else PIECEVALS[duplicates[0][0]])[2:].zfill(3)
    
    # existance of pieces for sorting
    piece_existance: str = "".join(('0' if piece in leftover else '1' for piece in BAG))

    # length of build
    build_length: str = bin(NUMPIECESINPC - len(build))[2:].zfill(4)

    # get piece counts
    piece_counts_binary = "".join((bin(int(abs(build_piece_counts[piece] - 3.5) - 0.5))[2:].zfill(2) if piece in build_piece_counts else "11" for piece in BAG))

    # temp unique id
    unique_id: str = '1' * 8

    # 1 + 3 + 3 + 7 + 4 + 14 + 8
    binary_id = first_bit + pc_num_bin + duplicate_piece + piece_existance + build_length + piece_counts_binary + unique_id
    hex_id = '%.*X' % (IDLEN, int(binary_id, 2))

    # find the correct unique id
    found_unique_ids: list[int]

    input_filtered_db: list[dict] = queryWhere(input_db, where=f"ID<>")
    input_filtered_db = queryWhere(input_filtered_db, where=f"ID<={hex_id}")
    input_filtered_db = queryWhere(input_filtered_db, where=f"ID>={hex_id[:8] + "00"}")

    found_unique_ids = [int(x["ID"][-2:],16) for x in input_filtered_db]

    known_db: list[dict] = openFile(FILENAMES[pc_num])
    filtered_db: list[dict] = queryWhere(known_db, where=f"ID<={hex_id}")
    filtered_db = queryWhere(filtered_db, where=f"ID>={hex_id[:8] + "00"}")

    found_unique_ids += [int(x["ID"][-2:], 16) for x in filtered_db]

    # non empty, if empty is new id
    if found_unique_ids:
        old_id: str = row["ID"]

        # get a new id that it could be
        unique_id = '%.*X' % (2, min(found_unique_ids) - 1)
        hex_id = hex_id[:8] + unique_id

        row["ID"] = hex_id


        # check with duplicate pieces from simple checks if duplicate row (ie should be itself)
        part_db: list[dict] = [row] + filtered_db
        sort_db(part_db)

        # run to check for duplicate rows
        collisions: list[list[str]] = duplicate_rows(part_db)

        # reset the id
        row["ID"] = old_id
        if collisions:
            # multiple collisions
            if len(collisions) > 1 or hex_id not in collisions[0]:
                raise RuntimeError(f"Database has duplicate rows in pc {pc_num}")

            hex_id = collisions[0][1 - collisions[0].index(hex_id)] # other id that isn't itself

    return hex_id

def generate_cover_dependence(row: dict, skip_oqb: bool = True) -> str:
    '''
    Generate a default cover dependence for the row

    Expected Filled:
        Leftover
        Build

    Optionally Filled:
        Previous Setup
        Next Setup

    Parameters:
        row (dict): row in database
        skip_oqb (bool): skip if previous/next setup filled as oqb

    Return:
        generated cover dependence for that row
    '''

    cover_dependence: str = ""

    # skip if it a oqb setup
    if skip_oqb and \
        (
            ("Previous Setup" in row and row["Previous Setup"]) or \
            ("Next Setup" in row and row["Next Setup"])
        ):

        if "Cover Dependence" in row:
            return row["Cover Dependence"]
        return cover_dependence

    # count pieces in leftover
    leftover_prefix: str = ""
    leftover_counter = Counter(row["Leftover"])
    duplicate: tuple[str, int] = leftover_counter.most_common(1)[0]

    build_length: int = 0
    pieces_optional: str
    pieces_required: Counter[str] = Counter(row["Build"].split(BUILDDELIMITOR)[0])
    pieces_total: Counter[str] = Counter()
    for build in row["Build"].split(BUILDDELIMITOR):
        build_counter = Counter(build)

        # other pieces used in the setup
        pieces_required &= build_counter
        pieces_total |= build_counter

        if build_length < len(build):
            build_length = len(build)

    leftover_required = sort_queue("".join((leftover_counter & pieces_required).elements()))
    next_bag_required = sort_queue("".join((pieces_required - Counter(leftover_required)).elements()))
    pieces_optional = sort_queue("".join((pieces_total - pieces_required).elements()))

    if len(leftover_counter.keys()) == 1:
        # if the leftover is only one piece
        leftover_prefix = "".join(leftover_counter.elements())
    else:
        if duplicate[1] == 2:
            rest_of_leftover = ''.join(leftover_counter.keys())
            # do the negation to reduce length
            if len(rest_of_leftover) > 4:
                rest_of_leftover = "^" + sort_queue(''.join(set(BAG) - set(rest_of_leftover)))

            leftover_prefix = duplicate[0] + f",[{rest_of_leftover}]"
        else:
            if row["Leftover"] == "TILJSZO":
                # is just 1st pc
                leftover_prefix = "*"
            else:
                leftover_prefix = f"[{row["Leftover"]}]"

        if build_length + 1 >= len(row["Leftover"]):
            if row["Leftover"] == "TILJSZO":
                # for first use *p7 instead
                leftover_prefix += "p7"
            else:
                # exactly uses either one less or same number of pieces in leftover
                leftover_prefix += "!"
        else:
            if duplicate[1] == 2:
                leftover_prefix += f"p{build_length}"
            else:
                # only need one more than number of pieces in build
                leftover_prefix += f"p{build_length + 1}"

        # include only pieces in build + 1
        if len(leftover_required) + 1 < len(row["Leftover"]):
            # remove duplicate piece
            if duplicate[1] == 2 and duplicate[0] in leftover_required:
                leftover_required = sort_queue("".join((Counter(leftover_required) - Counter(duplicate[0])).elements()))

            leftover_prefix += f"{{{leftover_required}=1}}"

    cover_dependence = leftover_prefix

    if next_bag_required:
        max_num_optional: int = build_length - pieces_required.total()
        cover_dependence += f",*p{len(next_bag_required) + max_num_optional + 1}" + "{"
        if pieces_optional:
              cover_dependence += f"{len(next_bag_required) + 1}:"
        cover_dependence += f"{next_bag_required}=1"

        if pieces_optional:
            # any optional pieces
            cover_dependence += f"||{next_bag_required}[{pieces_optional}]={max_num_optional}"
        cover_dependence += "}"

    return cover_dependence

def generate_pieces(row: dict, skip_oqb: bool = True) -> str:
    '''
    Generate a default pieces for the row

    Expected Filled:
        Leftover
        Build
        Setup (only for checking if 2l)

    Parameters:
        row (dict): row in database
    '''

    # skip if it a oqb setup
    if skip_oqb and \
        (
            ("Previous Setup" in row and row["Previous Setup"]) or \
            ("Next Setup" in row and row["Next Setup"])
        ):
        if "Pieces" in row:
            return row["Pieces"]
        return ""

    # check if enough pieces to solve and not special case of 7th pc and able to know last piece not seen
    special_case: bool = False
    if len(row["Build"]) + SEE < NUMPIECESINPC:
        special_case = LONUM2PCNUM(len(row["Leftover"])) == 7 and len(row["Build"]) + SEE == NUMPIECESINPC - 1
        if not special_case:
            return "NULL"

    pieces: list[str] = []

    bag_comp: list[int] = LONUM2BAGCOMP(len(row["Leftover"]))
    leftover_counter = Counter(row["Leftover"])

    for build in row["Build"].split(BUILDDELIMITOR):
        build_counter = Counter(build)

        # other pieces used in the setup
        pieces_used: Counter[str] = build_counter.copy()
        pieces_used.subtract(leftover_counter)

        pieces_not_used: str = sort_queue("".join((-pieces_used).elements()))
        pieces_used_str: str = sort_queue("".join((+pieces_used).elements()))

        parts: list[str] = []

        # pieces not used from leftover
        if pieces_not_used:
            # reduce length by doing listing pieces not in rather than in bag
            if len(pieces_not_used) > 4:
                leftover_pieces_used: str = sort_queue("".join(set(BAG) - set(pieces_not_used)))
                parts.append(f"[^{leftover_pieces_used}]!")
            else:
                if len(pieces_not_used) == 1:
                    # just one piece
                    parts.append(pieces_not_used)
                else:
                    parts.append(f"[{pieces_not_used}]!")

        if len(row["Leftover"]) > NUMPIECESINPC // 2 and \
            build_counter.total() == NUMPIECESINPC // 2 and \
            set(build_counter.keys()) == set("ILJO"):

            # is it a 2l?
            if is_pc(row["Setup"]):
                # skip adding the adding next bag
                pieces.append(",".join(parts))
                continue

        # pieces used from next bag
        if pieces_used_str:
            # reduce length by doing listing pieces in rather than not in bag
            if len(pieces_used_str) > 3:
                pieces_left: str = sort_queue("".join(set(BAG) - set(pieces_used_str)))
                if len(pieces_left) == 1:
                    # just one piece
                    parts.append(pieces_left)
                else:
                    parts.append(f"[{pieces_left}]!")
            else:
                parts.append(f"[^{pieces_used_str}]!")
        else:
            # didn't use any of next bag
            num_to_add = min(bag_comp[1] - (NUMPIECESINPC + HOLD - len(row["Build"]) - SEE - sum(bag_comp[2:])), bag_comp[1])

            # other special case on 2nd
            special_case = LONUM2PCNUM(len(row["Leftover"])) == 2 and len(row["Build"]) + SEE == NUMPIECESINPC
            if special_case:
                num_to_add += 1

            if num_to_add == 0:
                pass
            elif num_to_add == 1:
                parts.append("*")
            else:
                parts.append(f"*p{num_to_add}")

        if build_counter.total() == NUMPIECESINPC // 2:
            if set(build_counter.keys()) == set("ILJO"):
                # is it a 2l?
                if is_pc(row["Setup"]):
                    # skip adding the adding next bag
                    pieces.append(",".join(parts))
                    continue

        # if there's third bag in the pc
        if len(bag_comp) > 2:
            num_to_add = min(bag_comp[2] - (NUMPIECESINPC + HOLD - len(row["Build"]) - SEE), bag_comp[2])

            # the special case on 7th
            if special_case:
                num_to_add += 1

            # add necessary number of pieces left
            if num_to_add < 0:
                raise RuntimeError("Reach state where trying to fill pieces but not able to see enough pieces to solve")
            elif num_to_add == 0:
                pass
            elif num_to_add == 1:
                parts.append("*")
            else:
                parts.append(f"*p{num_to_add}")

        pieces.append(",".join(parts))

    return PIECESDELIMITOR.join(pieces)

def fill_columns(db: list[dict], print_disprepancy: bool = True, overwrite: bool = False, overwrite_equivalent: bool = True) -> None:
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

    def update(row: dict, 
               key: str, 
               func: Callable[[dict], str], 
               cond: Callable[[str, str], bool] = lambda old, new: new != old, 
               equivalent: Callable[[str, str], bool] = lambda old, new: new == old):
        if print_disprepancy or not row[key]:
            new = func(row)

            if print_disprepancy and row[key] and cond(row[key], new):
                simplified_row: dict = {
                    "ID": row["ID"],
                    "Leftover": row["Leftover"],
                    "Setup": row["Setup"],
                }
                print(f"Computed '{key}' differs '{row[key]}' -> '{new}' in {simplified_row}", end="")
                if overwrite or (overwrite_equivalent and equivalent(row[key], new)):
                    print(" overwritten", end="")
                    row[key] = new
                print()
            else:
                row[key] = new

    for row in db:
        # check if the necessary columns are filled
        if not (row["Leftover"] and row["Setup"]):
            raise ValueError(f"Required fields 'Leftover' and 'Setup' are missing in {row}")

        # fill build
        update(row, "Build", generate_build)

        # fill id
        update(row, "ID", lambda x: generate_id(x, db))

        # if overwrite_equivalent:
        #     equal_pieces = extended_pieces_equals
        # else:
        #     equal_pieces = lambda x,y: x == y

        # cover dependence based on leftover and build
        # update(row, "Cover Dependence", generate_cover_dependence, equivalent=equal_pieces)

        # pieces based on leftover and build
        # update(row, "Pieces", generate_pieces, equivalent=equal_pieces)
    
if __name__ == "__main__":
    from utils.constants import FILENAMES
    from utils.fileReader import openFile
    import csv

    db = openFile(FILENAMES[8])

    fill_columns(db, overwrite_equivalent=True)

    outfile = open("output/filled_columns.tsv", "w")
    
    fieldnames = db[0].keys()
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
    
    writer.writeheader()
    writer.writerows(db)
    
    outfile.close()
    

