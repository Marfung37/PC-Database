import subprocess
from csv import reader
from os import system, path, devnull

from utils.directories import ROOT, SFINDERPATH, KICKPATH
from utils.pieces import extendPieces
from utils.fileReader import queryWhere

GLUEFUMENPATH = path.join(ROOT, "src", "utils", "glueFumen.js")
PATTERNSPATH = path.join(ROOT, "src", "input", "patterns.txt")
COVERPATH = path.join(ROOT, "src", "output", "cover.csv")

def getCoverData(db: list[dict], overwrite: bool = False) -> list[dict]:
    '''
    Run cover on setups to get the cover data for the setup from cover dependency

    Parameter:
        db (list): a list of rows in the format of a dictionary
        overwrite (bool): whether to overwrite the cover data if new computed cover data differs

    Return:
        list: a list of rows with the cover data replaced
    '''

    # go through each row of the database
    for row in db:

        # if the column has cover data filled in
        previousCoverData = ""
        if row["Cover Data"]:
            previousCoverData = row["Cover Data"]

        # get the dependency
        pattern = row["Cover Dependence"]

        # get the queues from the pattern
        try:
            queues = extendPieces(pattern)
        except:
            # error
            print(f"Unable to process '{pattern}' for id '{row['ID']}'")
            continue

        # get the corresponding order of setups to do
        setups = getOrderOfSetups(row, db)

        # output bit string
        bitstr = ""

        # write the queues into the patterns file
        with open(PATTERNSPATH, "w") as infile:
            infile.write("\n".join(queues))
        
        # get the glue fumen verison of the setups
        glueCmd = f"node {GLUEFUMENPATH} {' '.join(setups)}".split()
        glueP = subprocess.Popen(glueCmd, stdout=subprocess.PIPE)
        glueFumens = glueP.stdout.read().decode().rstrip().split("\n")
        glueFumens = list(filter(lambda x: not x.startswith("Warning: "), glueFumens))
        
        # run cover on the setup fumens
        sfinderCmd = f"java -jar {SFINDERPATH} cover -t '{' '.join(glueFumens)}' -K {KICKPATH} " \
                     f"-d 180 -o {COVERPATH} -pp {PATTERNSPATH} > {devnull}"
        system(sfinderCmd)
        
        # open the csv file
        outfile = open(COVERPATH, "r")
        csvFile = reader(outfile)

        # skip header
        next(csvFile)

        # go through each line
        for line in csvFile:
            # start at 1 as first column is queues
            fumenNum = 1

            # go through all fumens, if all work then this queue is covered by the setup
            andBool = True
            for fumen in glueFumens:
                # go through for each page of the fumen
                orBool = False
                for _ in fumen.split(" "):
                    orBool = orBool or line[fumenNum] == "O"
                    fumenNum += 1
                
                # check if this fumen is also possible
                andBool = andBool and orBool

                # if ever false can just break out
                if not andBool: break
            
            # create the bit string for the cover of the setup
            bitstr += "1" if andBool else "0"
    
        # simplify the cover dependency completely describes the setup
        if "0" not in bitstr:
            bitstr = "1"

        # check for error
        if "1" not in bitstr:
            # should at least cover one queue
            print(f"{row['ID']} cover dependency is written improperly that the setup covers none of the queues")
            continue

        # check if the cover data before is different after computing it
        if previousCoverData and previousCoverData != bitstr:
            print(f"{row['ID']} previous cover data was {previousCoverData} but after computing it, it is {bitstr}")
            
            # overwrite
            if overwrite:
                row["Cover Data"] = bitstr
        
        else:
            # update the cover data
            row["Cover Data"] = bitstr

        outfile.close()

    return db

def getOrderOfSetups(row: dict, db: list[dict]) -> list[str]:
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
    previousSetupID = row["Previous Setup"]

    # add to setups
    setups.append(fumen)

    # go through the previous setups
    while previousSetupID:
        
        # find the row that had the previous setup id
        row = queryWhere(db, where=f"ID={previousSetupID}")[0]

        # get the fumen and previous setup for this row
        fumen = row["Setup"]
        previousSetupID = row["Previous Setup"]

        # add to setups
        setups.append(fumen)

    # reverse the order of the fumens
    setups.reverse()

    return setups
    
if __name__ == "__main__":
    from utils.fileReader import openFile

    db = openFile(path.join(ROOT, "tsv", "3rdPC.tsv"))
    db = queryWhere(db, where="Leftover=T")

    db = getCoverData(db)
