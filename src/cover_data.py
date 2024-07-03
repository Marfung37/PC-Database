import subprocess
from csv import reader
from os import path

from utils.constants import ROOT, SFINDERPATH, KICKPATH
from utils.pieces import extendPieces
from utils.fileReader import queryWhere
from utils.disassemble import disassemble
from utils.formulas import bin2hex

PATTERNSPATH = path.join(ROOT, "src", "input", "patterns.txt")
COVERPATH = path.join(ROOT, "src", "output", "cover.csv")

def get_order_of_setups(row: dict, db: list[dict]) -> list[str]:
    '''
    Get the previous setups to this setup

    Parameter:
        row (dict): a row in database format as a dictionary
        db (list): a list of the rows in the database

    Return:
        list[str]: fumens ordered by the first setup to build to last one
    '''

    setups = []
    
    # get the fumen and previous setup for this row
    fumen = row["Setup"]
    previous_setup_id = row["Previous Setup"]

    # add to setups
    setups.append(fumen)

    # go through the previous setups
    while previous_setup_id:
        
        try:
            # find the row that had the previous setup id
            row = queryWhere(db, where=f"ID={previous_setup_id}")[0]
        except:
            # error
            raise ValueError(f"The previous setup {previous_setup_id} was not found")

        # get the fumen and previous setup for this row
        fumen = row["Setup"]
        previous_setup_id = row["Previous Setup"]

        # add to setups
        setups.append(fumen)

    # reverse the order of the fumens
    setups.reverse()

    return setups

def get_cover_data(db: list[dict], overwrite: bool = False) -> list[dict]:
    '''
    Run cover on setups to get the cover data for the setup from cover dependency

    Parameter:
        db (list): a list of rows in the format of a dictionary
        overwrite (bool): whether to overwrite the cover data if new computed cover data differs

    Return:
        list: a list of rows with the cover data replaced
    '''

    # go through each row of the 
    for row in db:

        # if the column has cover data filled in
        previous_cover_data = ""
        if row["Cover Data"]:
            previous_cover_data = row["Cover Data"]

        # get the dependency
        pattern = row["Cover Dependence"]

        # get the queues from the pattern
        try:
            queues = list(extendPieces(pattern))
        except:
            # error
            print(f"Unable to process '{pattern}' for id '{row['ID']}'")
            continue

        # no queues were outputted
        if len(queues) == 0:
            print(f"{row['ID']} cover dependence returned no queues")
            continue

        # get the corresponding order of setups to do
        setups = get_order_of_setups(row, db)

        # output bit string
        bitstr = ""

        # write the queues into the patterns file
        with open(PATTERNSPATH, "w") as infile:
            infile.write("\n".join(queues))
        
        # get the glue fumen verison of the setups
        glue_fumens = disassemble(setups, print_error=False) 
        
        # run cover on the setup fumens
        sfinder_cmd = f"java -jar {SFINDERPATH} cover -t '{' '.join(map(' '.join, glue_fumens))}' -K {KICKPATH} " \
                     f"-d 180 -o {COVERPATH} -pp {PATTERNSPATH}"
        subprocess.run(sfinder_cmd.split(), stdout = subprocess.DEVNULL)

        # DEBUG
        # print(sfinderCmd)
        
        # open the csv file
        outfile = open(COVERPATH, "r")
        csvfile = reader(outfile)

        # skip header
        next(csvfile)

        # go through each line
        for line in csvfile:
            # start at 1 as first column is queues
            fumen_num = 1

            # go through all fumens, if all work then this queue is covered by the setup
            and_bool = True
            for fumens in glue_fumens:
                # go through for each page of the fumen
                or_bool = False
                for _ in fumens:
                    or_bool = or_bool or line[fumen_num] == "O"
                    fumen_num += 1
                
                # check if this fumen is also possible
                and_bool = and_bool and or_bool

                # if ever false can just break out
                if not and_bool: break
            
            # create the bit string for the cover of the setup
            bitstr += "1" if and_bool else "0"
    
        # simplify the cover dependency completely describes the setup
        if "0" not in bitstr:
            bitstr = "1"

        # check for error
        if "1" not in bitstr:
            # should at least cover one queue
            print(f"{row['ID']} return a cover of 0%")
            print(f"Cover dependency is written improperly or incorrect previous setup")
            continue

        # check if the cover data before is different after computing it
        if previous_cover_data and previous_cover_data != bin2hex(bitstr):
            print(f"{row['ID']} previous cover data differ from the new calculated value {previous_cover_data} -> {bin2hex(bitstr)}")
            
            # overwrite
            if overwrite:
                row["Cover Data"] = bin2hex(bitstr)
        
        else:
            # update the cover data
            row["Cover Data"] = bin2hex(bitstr)

        outfile.close()

    return db
    
if __name__ == "__main__":
    from utils.constants import FILENAMES
    from utils.fileReader import openFile
    import csv

    db = openFile(FILENAMES[2])

    db = get_cover_data(db, overwrite=True)

    outfile = open("output/cover_data.tsv", "w")

    fieldnames = db[0].keys()
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')

    writer.writeheader()
    writer.writerows(db)

    outfile.close()
