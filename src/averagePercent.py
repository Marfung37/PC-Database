from utils.pieces import sortQueues, extendPieces

def addQueueToTree(covering_tree: dict, queue: str, percent: float):
    '''
    Adds a queue with its percent to a tree for each queue

    Parameters:


    '''
        
    node = coveringTree
    queueIndex = 0
    piece = queue[queueIndex]
    while node.get(piece) is not None:
        node = node[piece]
        queueIndex += 1

        if queueIndex < len(queue):
            piece = queue[queueIndex]
        else:
            break
    
    # check if already covered
    if node.get('end') is not None:
        # only keep highest
        if node['end'] < percent:
            node['end'] = percent
        return False
    
    # not covered then add it
    while queueIndex < len(queue):
        piece = queue[queueIndex]
        node[piece] = {}
        node = node[piece]
        queueIndex += 1
    
    # add the end add it's the end
    node['end'] = percent

    return True

filename = sys.argv[1]
generalPieces = sys.argv[2]
sqlInput = open(filename, "r")
sqlInput = csv.DictReader(sqlInput, delimiter='\t')
coveringTree = {}

for line in sqlInput:
    pieces = [line["Cover Dependence"]]
    setups = []
    
    # if line["Previous Setup"]:
        # setups.extend(line["Previous Setup"].split(","))
    setups.append(line["Setup"])

    if line["Solve %"] != "NULL":
        percent = float(line["Solve %"][:-1])
    else:
        continue

    queues = extendPieces(pieces)
    if line["Cover Data"] == '1':
        for queue in queues:
            addQueueToTree(queue, percent)
    else:
        # read the bit string for if covered
        bitStr = line["Cover Data"]
        
        for queue, bit in zip(queues, bitStr):
            if bit == '1':
                addQueueToTree(queue, percent)

notCovered = []
worstQueues = []
worstChance = 100
bestSum = 0
coverCount = 0
totalCount = 0

for queue in extendPieces([generalPieces]):
    node = coveringTree
    queueIndex = 0
    piece = queue[queueIndex]
    allPercents = []
    while node.get(piece) is not None:
        node = node[piece]
        queueIndex += 1
        if node.get('end') is not None:
            allPercents.append(node.get('end'))

        if queueIndex < len(queue):
            piece = queue[queueIndex]
        else:
            break
    
    # check if already covered
    if not allPercents:
        notCovered.append(queue)
    else:
        if max(allPercents) < worstChance:
            worstChance = max(allPercents)
            worstQueues = [queue]
        elif max(allPercents) == worstChance:
            worstQueues.append(queue)
        bestSum += max(allPercents)
        coverCount += 1
    
    totalCount += 1
print("Not Covered")
print("\n".join(sortQueues(notCovered)))
print("Worst Queues")
print("\n".join(worstQueues))
print(f"Worst Chance: {worstChance:.2f}%")
print(f'Cover: {coverCount / totalCount * 100:.2f}% [{coverCount}/{totalCount}]')
print(f'Average Percent: {bestSum / totalCount:.2f}% [N/A]')
