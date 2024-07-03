from fractions import Fraction
from utils.pieces import sort_queues, extendPieces

def add_queue_to_tree(covering_tree: dict, queue: str, fraction: Fraction) -> bool:
    '''
    Adds a queue with its percent to a tree for each queue

    Parameters:
        covering_tree (dict): a tree represented with dict with keys TILJSZO with dicts with TILJSZO down
        queue (str): a queue to be added to the tree
        fraction (fraction): the fraction of the solve chance for that queue

    Returns:
        bool: whether the tree has changed
    '''
       
    # get the first node (the root)
    node = covering_tree

    # index of each piece of the queue
    queue_index = 0

    # check if the piece is in the current level of the tree
    while queue_index < len(queue) and queue[queue_index] in node:
        # traverse to next level
        piece = queue[queue_index]
        node = node[piece]
        queue_index += 1
    
    # check if this node has a chance associated with it
    if "chance" in node:

        # compare the chance to the chance for this queue
        if node["chance"] < fraction:
            node["chance"] = fraction
            return True

        return False
    
    # not covered already in the tree, add to tree
    while queue_index < len(queue):
        piece = queue[queue_index]
        
        # create new node
        node[piece] = {}

        # traverse to that node
        node = node[piece]

        queue_index += 1
    
    # add the chance
    node["chance"] = fraction

    return True

def add_setup_cover_queues(db: list[dict], covering_tree: dict):
    '''
    Goes through each line of the db to add their covering queues to the tree

    Parameters:
        db (list): a list of rows in the format of a dictionary
        covering_tree (dict): a tree represented with dict with keys TILJSZO with dicts with TILJSZO down
    '''

    for line in db:
        # check if this setup has a solve fraction
        if line["Solve Fraction"] == "NULL":
            continue

        # get the cover dependence
        pattern = line["Cover Dependence"]

        # convert the fraction in db to a fraction obj
        percent = Fraction(line["Solve Fraction"])

        # get the queues from cover dependence
        queues = extendPieces(pattern)

        # check if the data just is 1
        if line["Cover Data"] == '1':
            # add all queues
            for queue in queues:
                add_queue_to_tree(covering_tree, queue, percent)
        else:
            # read the bit string for if covered
            bit_str = int(line["Cover Data"], 16) 
            
            # add the queue if the bit is 1
            for queue in queues:
                if bit_str & 1 == '1':
                    add_queue_to_tree(covering_tree, queue, percent)
                bit_str >>= 1

def read_tree_stats(covering_tree: dict, general_pattern: str) -> dict:
    '''
    Calculate various stats from the covering tree and provided queues to covered

    Parameters:
        covering_tree (dict): a tree represented with dict with keys TILJSZO with dicts with TILJSZO down
        general_pattern (str): a pattern for extended pieces that represents all queues to be covered by the setups in db

    '''

    # dict of the various stats
    result_stats = {
        "Not Covered Queues": [],
        "Cover Fraction": [0, 0],
        "Cover Percent": 0,
        "Worst Queues": [],
        "Worst Fraction": Fraction(1, 1),
        "Worst Percent": 0,
        "Average Fraction": Fraction(0, 1),
        "Average Percent": 0,
    }

    # get the queues from the pattern
    queues = extendPieces(general_pattern)

    # go through each queue
    for queue in queues:
        # current best solve chance
        best_chance = -1

        # index for piece in queue
        queue_index = 0

        # get first node (root)
        node = covering_tree

        # while can traverse further in the tree
        while queue_index < len(queue) and queue[queue_index] in node:
            # traverse to next level
            piece = queue[queue_index]
            node = node[piece]
            queue_index += 1

            # check if a chance is on this tree level and best one so far
            if "chance" in node and best_chance < node["chance"]:
                best_chance = node["chance"]

        # check if there's no percent for this queue
        if best_chance == -1:
            # queue not covered
            result_stats["Not Covered Queues"].append(queue)

        else:
            # queue is covered
            # increment numerator
            result_stats["Cover Fraction"][0] += 1

            # check if this chance is the lowest chance of all queues
            if best_chance < result_stats["Worst Fraction"]:
                result_stats["Worst Fraction"] = best_chance
                result_stats["Worst Queues"] = [queue]

            # append to list of queues with worst chance
            elif best_chance == result_stats["Worst Fraction"]:
                result_stats["Worst Queues"].append(queue)

            result_stats["Average Fraction"] += best_chance
        
        result_stats["Cover Fraction"][1] += 1

    # sort the queues that are not covered
    result_stats["Not Covered Queues"] = sort_queues(result_stats["Not Covered Queues"])

    # calculate the cover percent
    cover_percent = result_stats['Cover Fraction'][0] / result_stats['Cover Fraction'][1]
    result_stats["Cover Percent"] = f"{cover_percent:.2%}"

    # sort the queues that have the lowest non-zero percent
    result_stats["Worst Queues"] = sort_queues(result_stats["Worst Queues"])

    # calculate the percentage for worst fraction
    result_stats["Worst Percent"] = f"{float(result_stats['Worst Fraction']):.2%}"

    # calculate the percentage for average
    result_stats["Average Fraction"] /= result_stats["Cover Fraction"][1]
    result_stats["Average Percent"] = f"{float(result_stats['Average Fraction']):.2%}"

    return result_stats

def average_percent(db: list[dict], general_pattern: str) -> dict:
    '''
    Calculate the average percent of the given database along with other stats of worst percent and their queues and overall cover the setups have

    Parameters:
        db (list): a list of rows in the format of a dictionary
        general_pattern (str): a pattern for extended pieces that represents all queues to be covered by the setups in db

    Returns:
        dict: a dictionary with the various stats
    '''

    # tree providing the percent associated with each queue
    covering_tree = {}

    add_setup_cover_queues(db, covering_tree)

    return read_tree_stats(covering_tree, general_pattern)
   
def display_stats(result_stats: dict, display_not_covered: bool = False, display_worst: bool = False):
    '''
    Display the statistics from running average percent

    Parameter:
        result_stats (dict): dictionary with various stats from running average percent
    '''

    if display_not_covered:
        print("Not Covered")
        print("\n".join(result_stats["Not Covered Queues"]))
    
    if display_worst:
        print("Worst Queues")
        print("\n".join(result_stats["Worst Queues"]))

    print(f"Worst Percent: {result_stats['Worst Percent']} [{str(result_stats['Worst Fraction'])}]")

    cover_fraction = '/'.join(map(str, result_stats['Cover Fraction']))
    print(f"Cover Percent: {result_stats['Cover Percent']} [{cover_fraction}]")

    print(f"Average Percent: {result_stats['Average Percent']} [{str(result_stats['Average Fraction'])}]")

def user_input() -> tuple[int, str, str, bool, bool]:
    '''
    Barebones user input
    
    Returns:
        int: An integer 1-8 representing the pc number
        str: A filter with column name and value
        str: A string that represents the general pattern

    '''

    # Ask user for pc number
    pc_num = int(input("Enter the PC number: "))

    # Ask user if want to filter for anything
    filter_char = input(f"Want to filter from PC {pc_num} (Y/n): ")

    where_str = ""
    if filter_char.lower() != "n":
        where_str = input("Enter filter string (Ex: Leftover=ILJO): ")

    # Ask user for queue
    general_pattern = input("Enter the general pattern these setups should cover: ")

    # Ask user if want queues not covered
    not_covered = input("Want to display queues not covered (y/N): ").lower() == 'y'

    # Ask user if want worst queues
    worst_queues = input("Want to display worst percent queues (y/N): ").lower() == 'y'

    return pc_num, where_str, general_pattern, not_covered, worst_queues

def main():
    '''Main function to handle user input and display output'''

    from utils.constants import FILENAMES
    from utils.fileReader import openFile, queryWhere
    
    pc_num, where_str, general_pattern, not_covered, worst_queues = user_input()

    db = openFile(FILENAMES[pc_num])
    db = queryWhere(db, where=where_str)

    display_stats(average_percent(db, general_pattern), display_not_covered=not_covered, display_worst=worst_queues)


if __name__ == "__main__":
    main()
