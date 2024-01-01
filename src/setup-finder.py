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
from utils.pieces import sortQueues
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

def setupFinder(pcNum: int, queue: str) -> list[str]:
    '''
    Basic setup finder that gives a list of ids for a setup

    Parameters:
        pcNum(int): An integer 1-8 representing the pc number
        queue(str): A string representing a queue

    Returns:
        list[str]: A list of strings of ids that are valid setups
    '''

    # get leftover pieces
    leftover = queue[:PCNUM2LONUM(pcNum)]
    print(leftover)
    
    rows = queryWhere(FILENAMES[pcNum], "ID,Build,Previous Setup,Setup,Next Setup,Solve %", where=f"Leftover={leftover}")

    print(rows)

    return [""]

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
    setupFinder(pcNum, queue)

if __name__ == "__main__":
    main()
