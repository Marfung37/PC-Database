import subprocess
from os import system
from pieces import extendPieces
from itertools import islice
import csv
from sys import argv

start = 2

filename = argv[1]
sqlInput = open(filename, "r")

sqlLines = csv.DictReader(sqlInput, delimiter='\t')
bitStrings = open("bitStrings.txt", "w")

for lineNum, line in enumerate(sqlLines):
    pieces = [line["Cover Dependence"]]
    setups = []
    
    if line["Previous Setup"]:
        setups.extend(line["Previous Setup"].split(","))
    setups.append(line["Setup"])

    queues = extendPieces(pieces)
    
    bitstr = ""
    if(not line["Cover Data"] or line["Cover Data"] != '1' or True):
        with open("input/patterns.txt", "w") as infile:
            infile.write("\n".join(queues))

        glueP = subprocess.Popen(f"node glueFumen.js {' '.join(setups)}".split(), stdout=subprocess.PIPE)
        glueFumens = glueP.stdout.read().decode().rstrip().split("\n")

        glueFumens = list(filter(lambda x: not x.startswith("Warning: "), glueFumens))
        cmd = f"java -jar sfinder.jar cover -t '{' '.join(glueFumens)}' -d 180 > /dev/null"
        system(cmd)
        with open("output/cover.csv", "r") as outfile:
            outfile.readline()
            count = 0
            for line in outfile:
                line = line.rstrip().split(",")
                fumenNum = 1
                andBool = True
                for fumen in glueFumens:
                    orBool = False
                    for i in fumen.split(" "):
                        orBool = orBool or line[fumenNum] == "O"
                        fumenNum += 1
                    
                    andBool = andBool and orBool
                
                bitstr += "1" if andBool else "0"
        
        if "0" not in bitstr:
            bitstr = "1"
    else:
        bitstr = "1"
    bitStrings.write(bitstr + "\n")

bitStrings.close()
