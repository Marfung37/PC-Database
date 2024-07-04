import re
import threading
import subprocess

from utils.fumen_utils import is_pc, get_height
from utils.queue_utils import split_extended_pieces
from utils.pieces import extendPieces
from utils.constants import ROOT, SFINDERPATH, KICKPATH

def calculate_percent_in_range(db: list[dict], line_start: int, line_end: int, thread_num: int = 1):
    '''
    Calculate percent of setups in a range of the rows of the database and update database with percentages

    Parameters:
        db (list): a list of rows in the format of a dictionary
        line_start (int): index of the db to start from
        line_end (int): index of the db to go till
        thread_num (int): the number this is (used for printing out messages)

    '''
    # go through all lines for this thread
    for line_num in range(line_start, line_end):
        line = db[line_num]

        # alias the relavent columns
        setup = line["Setup"]
        pieces = line["Pieces"]
        percent = line["Solve %"]

        # check if 2l pc
        clear_line = 4
        if is_pc(setup) and get_height(setup) == 2:
            clear_line = 2

        # continue if the pieces are NULL
        if pieces == 'NULL':
            continue

        # split pieces
        pieces = split_extended_pieces(pieces)
        
        # store the numerator and denominator
        numerator = 0 
        denominator = 0
        error = False

        # run pieces for each page of the setup
        for page, pattern in enumerate(pieces):
            try: 
                # get the queues for this patten
                queues = extendPieces(pattern)


                # put the queues into a patterns file
                pattern_filepath = os.path.join(ROOT, "src", "input", f"patterns_{thread_num}.txt")
                with open(pattern_filepath, "w") as infile:
                    infile.write("\n".join(queues))
    
                # run the percent and get the output
                percent_cmd = f"java -jar {SFINDERPATH} percent -t {setup} -pp {pattern_filepath} -P {page + 1} -d 180 -K {KICKPATH} -c {clear_line}".split()
                percent_out = subprocess.run(
                    percent_cmd, 
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    universal_newlines=True
                ).stdout.split('\n')

            except:
                # print out error message
                print(f"{line_num}: Had issues running percent")
                print(f"extendedPieces '{pattern}' > input/patterns.txt; java -jar sfinder.jar percent -t {setup} -d 180")
                error = True
                break
    
            # line with the percentage
            percent_line = ""
            
            # find the line
            if len(percent_out) > 23:
                # check 33 which is most common
                if len(percent_out) > 33 and percent_out[33].startswith('success'):
                    percent_line = percent_out[33]

                # try finding the line after 23
                else:
                    for lastOutLine in percent_out[23:]:
                        if lastOutLine.startswith('success'):
                            percent_line = lastOutLine
                            break
            else:
                # likely couldn't run percent due to pieces
                print(f'{line_num}: Problem processing pieces {pieces}')
                error = True
                break
    
            # get the fraction
            fraction_match_obj = re.match(r"^success = \d+\.\d\d% \((\d+)/(\d+)\)", percent_line)
            if fraction_match_obj is not None:
                numerator, denominator = list(map(int, fraction_match_obj.groups()))
            else:
                # error in finding percent in the output
                print(f"{line_num}: Couldn't find percent")
                error = True
                break
       
        # if there was an error with this line skip it
        if error:
            continue
       
        # calculate the percent
        calc_percent = f'{numerator / denominator * 100:.2f}%'
        fraction = f'{numerator}/{denominator}'

        # print the percentage found
        print(f'{line_num}: {fraction}')
    
        # check if the calculated percentage differs from what's already there
        if calc_percent != percent:
            # warn the user this is the case
            print(f'{line_num}: percent is calculated to be {calc_percent} instead of {percent}')
            print(f"extendedPieces '{';'.join(pieces)}' > input/patterns.txt; " + f"java -jar sfinder.jar percent -t {setup} -d 180")
        else:
            # write into the db
            line["Solve %"] = calc_percent
            line["Fraction"] = fraction
    
    print(f'Thread {thread_num} finished')
    
def check_percents(db: list[dict], threads: int = 4) -> list[dict]:
    '''
    Calculate the percents for all setups in db

    Parameters:
        db (list): a list of rows in the format of a dictionary
        threads (int): number of threads to use

    Return:
        list[dict]: the db possibly updated with the percents
    '''

    # separate the number of lines by the threads
    thread_lines = len(db) // threads

    # locks for each thread
    thread_locks = []

    # setup the threads
    for index in range(1, threads):
        # calculate the line to start with
        thread_start = index * thread_lines
        thread = threading.Thread(target=calculate_percent_in_range, args=(db, thread_start, thread_start + thread_lines, index))

        thread_locks.append(thread)
        thread.start()

    # main thread
    thread_start = 0
    calculate_percent_in_range(db, thread_start, thread_start + thread_lines, 0)

    # wait for other threads to finish
    for index, thread in enumerate(thread_locks):
        thread.join()

    return db

if __name__ == "__main__":
    import os
    from utils.constants import FILENAMES
    from utils.fileReader import openFile, queryWhere

    db = openFile(FILENAMES[6])

    check_percents(db, threads=1)
