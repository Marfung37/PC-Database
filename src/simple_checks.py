# some basic checks

from utils.fileReader import queryWhere
from utils.queue_utils import extended_pieces_equals, sort_queue, extended_pieces_startswith
from utils.fumen_utils import permutated_equals, get_pieces
from fill_columns import generate_build

def is_sorted(db: list[dict]) -> bool:
    '''
    Checks if the ids in the database is sorted

    Parameter:
        db (list)

    Return:
        bool: whether the db is sorted
    '''

    # go through each row
    for row_num in range(len(db) - 1):
        # check if current row is not less than next row
        if not (db[row_num]["ID"] < db[row_num + 1]["ID"]):
            return False

    return True

def duplicate_rows(db: list[dict], check_pieces: bool = False) -> list[list[str]]:
    '''
    Check if there's duplicate rows in the database

    Parameter:
        db (list)
        check_pieces (bool): whether to also check if the pieces are the same

    Return:
        list[list[str]]: a list of grouped together ids which are duplicates
    '''

    # take advantage of id being an encoding of the row
    # if the first 8 hexdigits are the same than possibly the same

    # the result
    result = []

    # current row index
    row_num = 0

    # check if it's sorted
    if not is_sorted(db):
        raise ValueError("The db passed to duplicate_rows is not sorted")

    # go through the rows
    while row_num < len(db):

        possible_rows = [db[row_num]]

        # get the first 8 hexdigits
        sub_id = possible_rows[0]["ID"][:8]

        # find all rows that match
        row_num += 1
        while db[row_num]["ID"].startswith(sub_id):
            possible_rows.append(db[row_num])
            row_num += 1

        # check pairwise each row
        for i in range(len(possible_rows)):
            duplicates = [db[i]]
            for j in range(i, len(possible_rows)):
                row1, row2 = db[i], db[j]
                
                # check if the two setups are the same
                same_fumen = permutated_equals(row1["Setup"], row2["Setup"])

                # don't have same fumen, definitely not duplicate setup
                if not same_fumen:
                    continue

                # check cover dependence
                same_cover_dependence = extended_pieces_equals(row1["Cover Dependence"], row2["Cover Dependence"])

                # check pieces
                same_pieces = False
                if check_pieces:
                    row1_null = row1["Pieces"] == "NULL"
                    row2_null = row2["Pieces"] == "NULL"
                        
                    if row1_null or row2_null:
                        same_pieces = row1_null and row2_null
                    else:
                        same_pieces = extended_pieces_equals(row1["Pieces"], row2["Pieces"])

                # if they have same cover dependence and same pieces (if relavent)
                if same_cover_dependence and (not check_pieces or same_pieces):
                    duplicates.append(row2)

            # if there's duplicates
            if len(duplicates) > 1:
                result.append(duplicates)

    return result

def assign_build(db: list[dict], print_error: bool = True, overwrite: bool = False) -> None:
    '''
    Determine what pieces are in the setup

    Parameter:
        db (list)
        print_error (bool): whether to print errors out
        overwrite (bool): whether to overwrite the build column
    '''

    for row in db:
        # get the pieces and sort them
        build = generate_build(row)

        if overwrite:
            row["Build"] = build

        # compare to what's in build column already
        if row["Build"] != build and print_error:
            print(f"{row['ID']} build differs from calculated: {row['Build']} -> {build}")

def check_oqb(db: list[dict], print_error: bool = True) -> list[list[dict]]:
    '''
    Checks if next setup cover dependences starts with its previous setup

    Check if the next setup has the previous setup marked correctly

    Parameter:
        db (list)
        print_error (bool): whether to print errors out

    Return:
        list[dict]: rows that have issues
    '''

    result = []

    # query for setups that have next setup
    previous_setup_rows = queryWhere(db, "Previous Setup<>")
    next_setup_rows = queryWhere(db, "Next Setup<>")

    for row in next_setup_rows:
        prev_id = row["ID"]
        cover_dependence = row["Cover Dependence"]
        next_setups_id = row["Next Setup"].split(":")

        # rows with issues
        issue_rows = [row]

        for id in next_setups_id:
            next_setup = queryWhere(db, f"ID={id}")[0]
            issue = False

            # check if this setup starts with the cover dependence from the previous setup
            if not extended_pieces_startswith(cover_dependence, next_setup["Cover Dependence"]):
                if print_error:
                    print(f"{prev_id} -> {id} have different cover dependence: {cover_dependence} -> {next_setup['Cover Dependence']}")
                
                issue_rows.append(next_setup)
                issue = True

            # check if this setup has the previous setup correct
            if next_setup["Previous Setup"] != prev_id:
                if print_error:
                    print(f"{id} is missing the previous setup {prev_id}")
                
                if not issue:
                    issue_rows.append(next_setup)
                    issue = True
        
        result.append(issue_rows)
    
    # check if the each previous setup has the same next setup
    for row in previous_setup_rows:
        prev_id = row["Previous Setup"]
        prev_setup = queryWhere(db, f"ID={prev_id}")[0]

        if row["ID"] not in prev_setup["Next Setup"].split(":"):
            if print_error:
                print(f"{prev_id} is missing the next setup {row['ID']}")
            result.append([row, prev_setup])

    return result


if __name__ == "__main__":
    from utils.fileReader import openFile
    from utils.directories import FILENAMES

    for i in range(1, 9):
        assign_build(openFile(FILENAMES[i]))

                

