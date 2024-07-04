# Fill out the rest of the columns and verify columns are reasonable

from utils.constants import FILENAMES, BUILDDELIMITOR, PIECESDELIMITOR
from utils.fileReader import queryWhere
from utils.formulas import LONUM2PCNUM, LONUM2BAGCOMP
from utils.queue_utils import BAG, PIECEVALS, sort_queue
from utils.fumen_utils import get_pieces
from collections import Counter
import re

IDLEN = 10
NUMPIECESINPC = 10
SEE = 7

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
    if len(duplicates) == 2 and duplicates[1][1] > 1: # more than 1 duplicates
        raise ValueError(f"Leftover has '{duplicates[0][0]}' and '{duplicates[1][0]}' duplicated but only one piece can be duplicated in {row}")

    # TODO: Issue as not matching with other calculated IDs
    duplicate_piece: str = bin(0 if duplicates[0][1] == 1 else 8 - PIECEVALS[duplicates[0][0]])[2:].zfill(3)
    
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
    hex_id = '%.*X' % (IDLEN, int(binary_id, 2))

    return hex_id

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
        pieces_used: Counter[str] = build_counter
        pieces_used.subtract(leftover_counter)

        pieces_not_used: str = sort_queue("".join((-pieces_used).elements()))
        pieces_used_str: str = sort_queue("".join((+pieces_used).elements()))

        parts: list[str] = []

        # pieces not used from leftover
        if pieces_not_used:
            # reduce length by doing listing pieces not in rather than in bag
            if len(pieces_not_used) > 3:
                leftover_pieces_used: str = sort_queue("".join(set(row["Leftover"]) - set(pieces_not_used)))
                parts.append(f"[^{leftover_pieces_used}]!")
            else:
                if len(pieces_not_used) == 1:
                    # just one piece
                    parts.append(pieces_not_used)
                else:
                    parts.append(f"[{pieces_not_used}]!")

        # pieces used from next bag
        if pieces_used_str:
            # reduce length by doing listing pieces in rather than not in bag
            if len(pieces_used_str) > 3:
                pieces_left: str = sort_queue("".join(set(BAG) - set(pieces_used_str)))
                parts.append(f"[{pieces_left}]!")
            else:
                parts.append(f"[^{pieces_used_str}]!")
        else:
            # didn't use any of next bag
            num_to_add = bag_comp[1] - (11 - len(row["Build"]) - SEE)

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

        # if there's third bag in the pc
        if len(bag_comp) > 2:
            num_to_add = bag_comp[2] - (11 - len(row["Build"]) - SEE)
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
                simplified_row: dict = {
                    "ID": row["ID"],
                    "Leftover": row["Leftover"],
                    "Setup": row["Setup"],
                }
                print(f"Computed '{key}' differs '{row[key]}' -> '{new}' in {simplified_row}")
            else:
                row[key] = new

    for row in db:
        # check if the necessary columns are filled
        if not (row["Leftover"] and row["Setup"]):
            raise ValueError(f"Required fields 'Leftover' and 'Setup' are missing in {row}")

        # fill build
        update(row, "Build", lambda: generate_build(row))

        # fill id
        # update(row, "ID", lambda: generate_id(row))

        # cover dependence based on leftover and build
        update(row, "Cover Dependence", lambda: generate_cover_dependence(row))

        # pieces based on leftover and build
        # update(row, "Pieces", lambda: generate_pieces(row))

    
if __name__ == "__main__":
    from utils.constants import FILENAMES
    from utils.fileReader import openFile
    import csv

    db = openFile(FILENAMES[8])

    fill_columns(db)

    outfile = open("output/filled_columns.tsv", "w")

    fieldnames = db[0].keys()
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')

    writer.writeheader()
    writer.writerows(db)

    outfile.close()

