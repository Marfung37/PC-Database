from os import system, path
from itertools import islice
import subprocess
import re
import threading
import csv
import sys

sys.path.append(path.dirname(path.realpath(__file__)) + "/utils")
from pieces import extendPieces


def thread_function(lines, lineNum, threadNum):
    for line in lines:
        setup = line["Setup"]
        pieces = line["Pieces"]
        percent = line["Solve %"]
        pieces = map("".join, re.findall("(.+?{.*?}):|([^{}]+?):|(.+?)$", pieces))
        
        numerator = 0
        denominator = 0
        error = False
        for partNum, piecesPart in enumerate(pieces):
            try: 
                queues = extendPieces([piecesPart])
                with open(f"input/patterns_{threadNum}.txt", "w") as infile:
                    infile.write("\n".join(queues))

                percentOut = subprocess.check_output(f"java -jar sfinder.jar percent -t {setup} -pp input/patterns_{threadNum}.txt -P {partNum + 1} -d 180 2>/dev/null".split()).decode().split("\n")
            except subprocess.CalledProcessError:
                print(f"{lineNum}: Had issues running percent")
                print(f"extendedPieces '{piecesPart}' > input/patterns.txt; java -jar sfinder.jar percent -t {setup} -d 180 2>/dev/null")
                error = True
                break

            percentLine = ""
            if len(percentOut) > 23:
                # check 33 which is most common
                if len(percentOut) > 33 and percentOut[33].startswith('success'):
                    percentLine = percentOut[33]
                else:
                    for lastOutLine in percentOut[23:]:
                        if lastOutLine.startswith('success'):
                            percentLine = lastOutLine
                            break
            else:
                print(f'{lineNum}: Problem processing pieces {pieces}')
                lineNum += 1
                error = True
                break

            fractionMatchObj = re.match('^success = \d+\.\d\d% \((\d+)/(\d+)\)', percentLine)
            if fractionMatchObj is not None:
                fractionVals = list(map(int, fractionMatchObj.groups()))
                numerator += fractionVals[0]
                denominator += fractionVals[1]
            else:
                print(f"{lineNum}: Couldn't find percent")
                error = True
                break
        
        if error:
            lineNum += 1
            continue
        
        calcPercent = f'{numerator / denominator * 100:.2f}%'
        fraction = f'{numerator}/{denominator}'
        print(f'{lineNum}: {fraction}')

        if calcPercent != percent:
            print(f'{lineNum}: percent is calculated to be {calcPercent} instead of {percent}')
            print(f"extendedPieces '{';'.join(pieces)}' > input/patterns.txt; " + f"java -jar sfinder.jar percent -t {setup} -d 180")
        
        outputFile.write(calcPercent + "\n")
        lineNum += 1

        # if lineNum % 100 == 0:
        #     print(f"{lineNum} done")
    
    print(f'Thread {threadNum} finished')


start = 2
numThreads = 1

filename = sys.argv[1]
sqlInput = open(filename, "r")

sqlLines = list(csv.DictReader(sqlInput, delimiter='\t'))
outputFile = open("percentOut.txt", "w")

lineNum = start
threadLineSize = len(sqlLines) // numThreads

threads = []
for index in range(numThreads - 1):
    threadStart = index * threadLineSize
    thread = threading.Thread(target=thread_function, args=(sqlLines[threadStart: threadStart + threadLineSize], start + threadStart, index))

    threads.append(thread)
    thread.start()

# main thread
threadStart = (numThreads - 1) * threadLineSize
thread_function(sqlLines[threadStart: threadStart + threadLineSize], start + threadStart, "main")

for index, thread in enumerate(threads):
    thread.join()
sqlInput.close()
outputFile.close()
