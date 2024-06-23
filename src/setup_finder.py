# -*- coding: utf-8 -*-

#
# Basic Outline
#
# Given a pc number and queue
# Return a list of possible setups
#
# Additional Notes
# For oqb setups, need to ask for queue again (somewhat implemented)
# Try to have images of the setups for ease (somewhat implemented)
#

# imports
from utils.directories import FILENAMES
from utils.fumen_utils import get_field
from utils.queue_utils import sort_queue
from utils.inverse_pieces import matching_queue
from utils.formulas import PCNUM2LONUM, hex2bin
from utils.fileReader import queryWhere, openFile

# color of pieces when printed out to terminal using ANSI color codes
class PIECECOLORS:
    BLACK = '\033[30;40m'
    MAGENTA = '\033[35;45m'
    CYAN = '\033[96;106m'
    ORANGE = '\033[38;5;208;48;5;208m'
    BLUE = '\033[34;44m'
    GREEN = '\033[92;102m'
    RED = '\033[91;101m'
    YELLOW = '\033[93;103m'
    ENDC = '\033[0m'

# a square shaped character that leads to better displayed setups
SQUARECHAR = '\u9606'


def setupFinder(pcNum: int, queue: str, previousSetup: str = "") -> list[dict]:
    '''
    Basic setup finder that gives a list of ids for a setup

    Parameters:
        pcNum(int): An integer 1-8 representing the pc number
        queue(str): A string representing a queue

    Returns:
        list[str]: A list of strings of ids that are valid setups
    '''

    queue = queue.upper()

    foundSetups = []
    rows = openFile(FILENAMES[pcNum])

    # get leftover pieces sorted
    leftover = sort_queue(queue[:PCNUM2LONUM(pcNum)])
    
    # get the rows where the leftover matches
    rows = queryWhere(rows, where=f"Leftover={leftover}")

    # filter for the previous setup
    rows = queryWhere(rows, where=f"Previous Setup={previousSetup}")

    # go through the rows
    for row in rows:
        found = False
        index = matching_queue(queue, row["Cover Dependence"], equality=lambda x, y: y.startswith(x))

        if index == -1:
            continue

        # if the dependence is fully described
        if row["Cover Data"] == "1":
            found = True

        elif hex2bin(row["Cover Data"])[index] == "1":
            found = True

        if found:
            foundSetups.append(row)

    return foundSetups

def bestChanceSetups(setups: list[dict]):
    null_setups = []
    best_setups = []
    best_chance = 0
    for setup in setups:
        if setup["Solve %"] == "NULL":
            null_setups.append(setup)
            continue

        setup_percent = float(setup["Solve %"][:-1])
        if best_chance < setup_percent:
            best_chance = setup_percent
            best_setups = [setup]
        elif best_chance == setup_percent:
            best_setups.append(setup)
    best_setups += null_setups

    return best_setups

def displaySetups(setups: list[dict]) -> int:
    '''
    Displays the setups into the terminal output

    Parameter:
        setups (list[dict]): a list of rows to display

    Returns:
        int: user input for which setup they chose
    '''

    null_setup = False
    for num, setup in enumerate(setups):
        num += 1 # increment so num is 1-len(setup)

        if setup["Solve %"] == "NULL":
            null_setup = True

        # print the setup's ID
        print(setup["ID"])
        fields = get_field(setup["Setup"], height=4)

        # for each page put side by side
        lines = []
        for row in range(4):
            line = ""
            for field in fields:
                part = field.split()[row]
                part = part.replace('_', PIECECOLORS.BLACK      + SQUARECHAR)        
                part = part.replace('T', PIECECOLORS.MAGENTA    + SQUARECHAR)        
                part = part.replace('I', PIECECOLORS.CYAN       + SQUARECHAR)        
                part = part.replace('L', PIECECOLORS.ORANGE     + SQUARECHAR)        
                part = part.replace('J', PIECECOLORS.BLUE       + SQUARECHAR)        
                part = part.replace('S', PIECECOLORS.GREEN      + SQUARECHAR)        
                part = part.replace('Z', PIECECOLORS.RED        + SQUARECHAR)        
                part = part.replace('O', PIECECOLORS.YELLOW     + SQUARECHAR)        
                part += PIECECOLORS.ENDC

                line += part + " "
            
            lines.append(line)

        lines = "\n".join(lines)

        print(lines)
        print(f"{num}. {setup['Solve %']}")
        print()

    if null_setup:
        choice: str = input("Enter which setup you chose: ")
        choice_int: int = 0

        good_user_input = False
        
        while not good_user_input:
            if choice.isnumeric():
                choice_int: int = int(choice)
                if 1 <= choice_int <= len(setups):
                    good_user_input = True

        choice_int -= 1
        if setups[choice_int]["Next Setup"]: 
            return choice_int

    return -1

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

    # special case for 1st pc for greater ease
    if pcNum == 1 and len(queue) == 6:
        bag = set("TILJSZO")
        last_piece = (bag - set(queue)).pop()
        queue += last_piece

    return pcNum, queue


def main(continuous: bool = False) -> None:
    '''
    Main function to run rest of program

    Parameter:
        continuous (bool): assumes user will go to next pc
    '''

    pcNum, queue = userInput()

    # DEBUG
    # pcNum = 3
    # queue = "TTILJSZ"
    
    while True:    
        setups = setupFinder(pcNum, queue)
        setups = bestChanceSetups(setups)

        choice = displaySetups(setups)

        while choice != -1:
            # Ask user for queue
            queue += input("Enter the additional pieces you can see in order: ")
        
            setups = setupFinder(pcNum, queue, previousSetup=setups[choice]["ID"])
            setups = bestChanceSetups(setups)
            choice = displaySetups(setups)
        
        print("Now just solve!")
        
        if continuous:
            # Ask user for queue
            queue = input("Enter the queue you can see: ")
            
            pcNum += 1
            if pcNum == 8:
                pcNum = 1

        else:
            # just break if not continuous
            break
            
        
if __name__ == "__main__":
    main(continuous=True)
