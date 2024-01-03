#
# Basic Outline
#
# Given a pc number and queue
# Return a list of possible setups
#
# Additional Notes
# For oqb setups, need to ask for queue again (not implemented)
# Try to have images of the setups for ease (somewhat implemented)
#

# imports
from utils.directories import FILENAMES
from utils.fumenUtils import getField
from utils.sortTetris import sortQueue
from utils.reversePieces import matchingQueue
from utils.formulas import PCNUM2LONUM
from utils.fileReader import queryWhere, openFile

def setupFinder(pcNum: int, queue: str, previousSetup: str = "") -> list[dict]:
    '''
    Basic setup finder that gives a list of ids for a setup

    Parameters:
        pcNum(int): An integer 1-8 representing the pc number
        queue(str): A string representing a queue

    Returns:
        list[str]: A list of strings of ids that are valid setups
    '''

    foundSetups = []
    rows = openFile(FILENAMES[pcNum])

    # get leftover pieces sorted
    leftover = sortQueue(queue[:PCNUM2LONUM(pcNum)])
    
    # get the rows where the leftover matches
    rows = queryWhere(rows, where=f"Leftover={leftover}")

    # filter for the previous setup
    rows = queryWhere(rows, where=f"Previous Setup={previousSetup}")

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
            foundSetups.append(row)

    return foundSetups

def displaySetups(setups: list[dict]) -> None:
    '''
    Displays the setups into the terminal output

    Parameter:
        setups (list[dict]): a list of rows to display

    '''

    class PIECECOLORS:
        BLACK = '\033[30;40m'
        MAGENTA = '\033[35;45m'
        CYAN = '\033[96;106m'
        DARKYELLOW = '\033[38;5;208;48;5;208m'
        BLUE = '\033[34;44m'
        GREEN = '\033[92;102m'
        RED = '\033[91;101m'
        YELLOW = '\033[93;103m'
        ENDC = '\033[0m'

    for setup in setups:
        fields = getField(setup["Setup"], height=4)

        # for each page put side by side
        lines = []
        for row in range(4):
            line = ""
            for field in fields:
                part = field.split()[row]
                part = part.replace('_', PIECECOLORS.BLACK + '\u9606')        
                part = part.replace('T', PIECECOLORS.MAGENTA + '\u9606')        
                part = part.replace('I', PIECECOLORS.CYAN + '\u9606')        
                part = part.replace('L', PIECECOLORS.DARKYELLOW + '\u9606')        
                part = part.replace('J', PIECECOLORS.BLUE + '\u9606')        
                part = part.replace('S', PIECECOLORS.GREEN + '\u9606')        
                part = part.replace('Z', PIECECOLORS.RED + '\u9606')        
                part = part.replace('O', PIECECOLORS.YELLOW + '\u9606')        
                part += PIECECOLORS.ENDC

                line += part + " "
            
            lines.append(line)

        lines = "\n".join(lines)

        print(lines)
        print(setup["Solve %"])
        print()

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
    setups = setupFinder(pcNum, queue)
    displaySetups(setups)

if __name__ == "__main__":
    main()
