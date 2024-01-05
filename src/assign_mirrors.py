# Check if the mirror column seems reasonable

from utils.fileReader import queryWhere, binarySearch, COL2COMPARE
from utils.fumen_utils import mirror_fumen, permutated_equals
from utils.queue_utils import mirror_queue, mirror_pattern, \
                              extended_pieces_equals

def get_mirror_setup(db: list[dict], row: dict) -> dict:
    '''
    Find the row that is the mirror of this row 

    Parameters:
        db (list): a list of rows in the format of a dictionary
        row (dict): one of the rows in db

    Return:
        dict: the row that represents the mirror of this row

    '''

    result = {}

    # get the mirror of the leftover
    mirror_row_leftover = mirror_queue(row["Leftover"])

    # if the mirror leftover is the same as the row
    # they mirror setup should in theory be itself
    # this function will still compute it in case the setup is elsewhere
    # this may be the case if the mirror has a different percent

    # get the mirror of the fumen
    mirror_row_fumen = mirror_fumen(row["Setup"])

    # filter db for the leftover
    possible_setups = queryWhere(db, f"Leftover={mirror_row_leftover}")

    # filter db for the fumen
    possible_setups = queryWhere(db, f"Setup={mirror_row_fumen}", equals=permutated_equals)

    # if there's no possible setups
    if len(possible_setups) == 0:
        return result

    # if the row is found as a possible mirror, it must be the mirror
    if row in possible_setups:
        return row

    #
    # compare by cover dependence and pieces
    #

    mirror_cover_dependence = mirror_pattern(row["Cover Dependence"])
    
    # case the pieces are null
    if row["Pieces"] != "NULL":
        mirror_pieces = mirror_pattern(row["Pieces"])
    else:
        mirror_pieces = "NULL"

    for setup in possible_setups:
        try:
            # check cover dependence is the same
            if not extended_pieces_equals(mirror_cover_dependence, 
                                          setup["Cover Dependence"]):
                continue

            # case the pieces are null
            if mirror_pieces == "NULL":
                if setup["Pieces"] != "NULL":
                    continue
            else:
                # check pieces is the same
                if not extended_pieces_equals(mirror_pieces, setup["Pieces"]):
                    continue
        except:
            raise ValueError(f"{row['ID']} or {setup['ID']} ran into an error when " \
                              "comparing cover dependence and pieces")

        # there can only be one possible setup
        # if there more than one with the same of all these columns,
        # the 2 rows must be the same in every respect
        result = setup
        break

    return result

def check_mirrors(db: list[dict], 
                  print_errors: bool = False, 
                  overwrite: bool = False
                  ) -> list[dict]:
    '''
    Assign and check the ids for mirror of setups

    Parameters:
        db (list): a list of rows in the format of a dictionary
        print_errors (bool): whether to print out issues found
        overwrite (bool): whether to overwrite the mirror columns,
                          if False, just check if the mirror column is correct
    
    Return:
        list: a list of rows with the mirrors assigned and checked

    '''

    # boolean array for if the row has been checked
    row_checked = [False] * len(db)
    
    # go through the rows of the db
    for row_index, row in enumerate(db):
        # check if this row has been checked
        if row_checked[row_index]:
            continue

        # get the mirror of this row
        try:
            mirror_row = get_mirror_setup(db, row)
        except Exception as e:
            if print_errors:
                print(e)

            continue

        # if no mirror row was found
        if not mirror_row:
            if print_errors:
                print(f"{row['ID']} couldn't find a mirror" +
                       (" but marked as 'NULL'" if row["Mirror"] == "NULL" else ""))
            continue

        # if the mirror row is the same row
        if row == mirror_row:
            # set that this row is checked
            row_checked[row_index] = True

            # if overwriting
            if overwrite:
                row["Mirror"] = "NULL"

            # the mirror id should be NULL in this case
            if row["Mirror"] != "NULL" and print_errors:
                print(f"{row['ID']} should a mirror id of 'NULL'")

            continue


        # get the index of this mirror row
        mirror_index = binarySearch(mirror_row["ID"], db, "ID", COL2COMPARE["ID"])

        # set this row and mirror to checked
        row_checked[row_index] = True
        row_checked[mirror_index] = True

        # if overwrite just write the id and mirror id columns
        if overwrite:
            row["Mirror"] = mirror_row["ID"]
            mirror_row["Mirror"] = row["ID"]

        # check if the ids are matching correctly
        matching_mirrors = row["ID"] == mirror_row["Mirror"] and \
                           row["Mirror"] == mirror_row["ID"]
        
        # if not matching print error message
        if not matching_mirrors and print_errors:
            print(f"{row['ID']} and {mirror_row['ID']} are mirrors but " \
                   "aren't noted as such in the database")

    return db

if __name__ == "__main__":
    from utils.directories import FILENAMES
    from utils.fileReader import openFile, queryWhere

    db = openFile(FILENAMES[2])

    check_mirrors(db, print_errors=True)
