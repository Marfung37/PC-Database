# coding=utf-8
import csv
import sys
import argparse
import os

args = sys.argv #filename csv_path  

InputCSV = []
with open(args[1], 'r') as csv_file:
    data = csv.reader(csv_file)

    for row in data:
        InputCSV.append(row)
    # print(InputCSV)

ungluedRow = []

f = open("temp_gluedfumens.txt", "w")
delim = "\n"
f.write(delim.join(InputCSV[0][1:]))
f.close()

os.system('node unglueFumen.js --fp temp_gluedfumens.txt --op temp_ungluedfumens.txt') #temp arrangment

g = open("temp_ungluedfumens.txt", "r")
ungluedRow = g.read().split("\n")
g.close()
# print(ungluedRow)

Records = []
for row in InputCSV[1:]: 
    sequence = row[0]
    SuccessFumens = [sequence]
    for element, fumen in zip(row[1:], ungluedRow):
        if (element == 'O'):
            SuccessFumens.append(fumen)
            # print(SuccessFumens)
    Records.append(SuccessFumens)
# print(Records)

OutputCSV = []
OutputCSV.append(["pattern", "solutionCount", "solutions", "unusedMinos", "fumens"])
delim = ";"
for record in Records:
    OutputCSV.append([record[0], len(record)-1, '', '', delim.join(record[1:])])
# print(OutputCSV)

InputFileName = args[1].split(".csv")
OutputFileName = InputFileName[0] + "_to_path.csv" + InputFileName[1]
with open(OutputFileName, 'w', newline='') as csvfile:
    OutputFileWriter = csv.writer(csvfile)
    for row in OutputCSV:
        OutputFileWriter.writerow(row)