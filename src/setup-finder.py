#
# Basic Outline
#
# Given a pc number and queue
# Return a list of possible setups
#
# Additional Notes
# For oqb setups, need to ask for queue again
# Try to have images of the setups for ease
#

# imports
import os
from utils.sortTetris import sortQueue
from utils.reversePieces import matchingQueue
from utils.formulas import PCNUM2LONUM
from utils.fileReader import queryWhere

# dict of pc number to filename/paths
FILENAMES = {
    1: os.path.join("..", "tsv", "1stPC.tsv"),
    2: os.path.join("..", "tsv", "2ndPC.tsv"),
    3: os.path.join("..", "tsv", "3rdPC.tsv"),
    4: os.path.join("..", "tsv", "4thPC.tsv"),
    5: os.path.join("..", "tsv", "5thPC.tsv"),
    6: os.path.join("..", "tsv", "6thPC.tsv"),
    7: os.path.join("..", "tsv", "7thPC.tsv"),
    8: os.path.join("..", "tsv", "8thPC.tsv"),
}

def setupFinder(pcNum: int, queue: str, previousSetup: str = "") -> list[str]:
    '''
    Basic setup finder that gives a list of ids for a setup

    Parameters:
        pcNum(int): An integer 1-8 representing the pc number
        queue(str): A string representing a queue

    Returns:
        list[str]: A list of strings of ids that are valid setups
    '''

    ids = []

    # check if the previous setup match up first
    if previousSetup:
        rows = queryWhere(FILENAMES[pcNum], where=f"Previous Setup={previousSetup}")
    else:
        # get leftover pieces sorted
        leftover = sortQueue(queue[:PCNUM2LONUM(pcNum)])
        
        # get the rows where the leftover matches
        rows = queryWhere(FILENAMES[pcNum], where=f"Leftover={leftover}")

    # go through the rows
    for row in rows:
        found = False
        index = matchingQueue(queue, row["Cover Dependence"], equality=lambda x, y: y.startswith(x))

        # if the dependence is fully described
        if row["Cover Data"] == "1":
            # check if found in the dependence
            if index != -1:
                found = True

        elif row["Cover Data"][index] == "1":
            found = True

        if found:
            ids.append(row["ID"])

    return ids

def userInput() -> tuple[int, str]:
    '''
    Barebones user input for the pc number and queue
    
    Returns:
        int: An integer 1-8 representing the pc number
        str: A string that represents a queue

    '''

    # Ask user for pc number
    pcNum = int(input("Enter the PC number: "))

    # Ask user for queue
    queue = input("Enter the queue you can see: ")

    return pcNum, queue


def main() -> None:
    '''
    Main function to run rest of program
    '''

    pcNum, queue = userInput()
    print(setupFinder(pcNum, queue))

if __name__ == "__main__":
    main()
