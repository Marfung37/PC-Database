# imports
from sys import argv
from itertools import product, permutations, chain
from string import whitespace
from functools import partial
from typing import Iterable
import re

# bag constant
BAG = "TILJSZO"


# sort queues
def sort_queues(queues: Iterable[str]) -> list[str]:
    """
    Sort the queue with TILJSZO ordering

    Parameters:
        queues: list of queues to sort

    Returns:
        list of sorted queues
    """

    piece_values: dict[str, str] = {
        "T": "1",
        "I": "2",
        "L": "3",
        "J": "4",
        "S": "5",
        "Z": "6",
        "O": "7",
    }

    queue_set_values = lambda q: int("".join(piece_values[p] for p in q))

    return sorted(queues, key=queue_set_values)


# get the pieces from the normal sfinder format
def parse_input(input_pattern: str, bsort_queues: bool = True):
    """
    Get the pieces from the normal sfinder format or inputted files

    Parameters:
        input: string input for queues
        bsort_queues: whether it should sort the outputed queues

    Returns:
        a generator or list of the queues
    """

    # two sections with prefix of pieces and suffix of permutate
    prefix_pattern = r"([*TILJSZO]|\[\^?[TILJSZO]+\]|<.*>)"
    suffix_pattern = r"(p[1-7]|!)?"

    # regex find all the parts
    pattern_parts: list[tuple[str, str]] = re.findall(
        prefix_pattern + suffix_pattern, input_pattern
    )

    # check if there wasn't a mistake in the finding of parts
    if "".join(map("".join, pattern_parts)) != input_pattern:
        # doesn't match
        raise RuntimeError("Failed to separate input into parts")

    # generate the queues
    queues = []
    for pieces_format, permutate_format in pattern_parts:
        # generate the actual pieces

        # just a wildcard or a piece
        if len(pieces_format) == 1:
            if pieces_format == "*":
                actual_pieces = BAG
            else:
                actual_pieces = pieces_format  # a piece

        # is a set of pieces
        elif (
            tmp_match_obj := re.match(r"\[\^?([TILJSZO]+)\]", pieces_format)
        ) is not None:
            actual_pieces = tmp_match_obj.group(1)

            if pieces_format[1] == "^":
                actual_pieces = "".join(set(BAG) - set(actual_pieces))
                if actual_pieces == "":
                    raise RuntimeError(f"Empty actual pieces from {pieces_format}")

        # is a file
        elif tmp_match_obj := re.match("<.*>", pieces_format) is not None:
            filename = pieces_format[1:-1]

            queue_lines = []
            with open(filename, "r") as infile:

                for line in infile:
                    # ignore comments or whitespace
                    line = line.strip()
                    if line.startswith("#") or not line:
                        continue

                    queue_lines.append(line)

            queues.append(extendPieces(queue_lines))

            continue
        else:
            # invalid pieces format
            raise RuntimeError(f"The pieces {pieces_format} could not be parsed!")

        # actual pieces is generated

        # determine the permutate for the pieces
        if permutate_format != "":

            # ! ending meaning permutation of the pieces
            if permutate_format == "!":
                queues.append(set(map("".join, permutations(actual_pieces))))

            # some permute n ending
            else:
                # get the number at the end after p
                permutate_num = int(permutate_format[-1])

                # as long as the number is at most the length of the pieces
                if permutate_num <= len(actual_pieces):
                    queues.append(
                        set(map("".join, permutations(actual_pieces, permutate_num)))
                    )
                else:
                    # error
                    raise RuntimeError(
                        f"{input_pattern} has {permutate_format}"
                        f" even though {pieces_format} has length {len(actual_pieces)}"
                    )
        else:
            # 1 piece queues
            queues.append(set(actual_pieces))

    # do the product of each part for one long queue
    queues = map("".join, product(*queues))

    # sort the queues
    if bsort_queues:
        queues = sort_queues(queues)

    # return the queues
    return queues


# make tree of the modifier to allow for easier parsing
def make_modifier_tree(modifier: str, index: int = 0, depth: int = 0, return_length: bool = False) -> list | tuple[list, int]:
    """
        Make tree of the modifier

        Parameters:
            modifier: modifier string
            index: index of the modifier been parsed
            depth: depth of the recursion

        Returns:
            tree of the parsed modifier
    """

    # holds the tree
    modifier_tree = []

    # string to hold the current string before appending to tree
    parsing_modifier_ele = ""

    # run through each character of the modifier
    while index < len(modifier):
        # get the character at that index
        char = modifier[index]

        # check if the char is the start of a regex expression
        if char == "/":
            try:
                # get the index of closing regex /
                closingSlashIndex = modifier.index("/", index + 1)

                # get the text in the regex and add to the parsing_modifier_ele
                parsing_modifier_ele += modifier[index : closingSlashIndex + 1]

                # move index to end of the regex
                index = closingSlashIndex

            # the closing slash wasn't found
            except ValueError:
                raise RuntimeError(f"No closing slash for regex at '{modifier[index:]}'")

        # opening parentheses
        elif char == "(":
            # handle the subtree with recursion
            subTree, i = make_modifier_tree(modifier, index + 1, depth + 1)

            # add any prefixes
            subTree.insert(0, parsing_modifier_ele)
            parsing_modifier_ele = ""

            # add the sub tree to the tree
            modifier_tree.append(subTree)

            # move index to the end of the parentheses section
            index = i

        # closing parentheses
        elif char == ")":
            # if on a sub tree
            if depth != 0:
                # add the current string to the subtree
                if parsing_modifier_ele:
                    modifier_tree.append(parsing_modifier_ele)

                # return the sub tree
                return modifier_tree, index
            # on the main tree and error
            else:
                raise Exception(
                    f"Missing opening parentheses with '{modifier[: index + 1]}'"
                )

        # boolean operator
        elif char == "&" or char == "|":
            if parsing_modifier_ele:
                # append the current string to tree
                modifier_tree.append(parsing_modifier_ele)
                parsing_modifier_ele = ""

            # if there's two & or |
            if modifier[index + 1] == char:
                # append the operator the tree
                modifier_tree.append(char * 2)
                index += 1
            # there's only one & or |
            else:
                raise RuntimeError(f"Missing second character of '{char}'")

        # end of modifier
        elif char == "}":
            # append the final current string if on the main tree
            if depth == 0:
                if parsing_modifier_ele:
                    modifier_tree.append(parsing_modifier_ele)
            # on a sub tree meaning no closing parentheses
            else:
                raise Exception(f"Missing closing parentheses")

            # return the main tree
            if return_length:
                return modifier_tree, index
            else:
                return modifier_tree

        # some other character
        # ignore whitespace
        elif char not in whitespace:
            parsing_modifier_ele += char

        # increment the index
        index += 1

    # append the final current string if on the main tree
    if depth == 0:
        if parsing_modifier_ele:
            modifier_tree.append(parsing_modifier_ele)
    # on a sub tree meaning no closing parentheses
    else:
        raise Exception(f"Missing closing parentheses")

    # return the main tree
    if return_length:
        return modifier_tree, index
    else:
        return modifier_tree


# handle operator in the modifier
def handleOperatorInModifier(currBool, newBool, operator, modifierType):
    """Handle the operator in the modifier"""

    # and operator
    match operator:
        case "&&":
            return currBool and newBool
        case "||":
            return currBool or newBool
        case _:
            # something went wrong
            errorPrefix = "Something went wrong when parsing leading to not catching no operator before a "
            raise RuntimeError(errorPrefix + modifierType)


# handle prefixes in modifier
def handlePrefixesInModifier(modifierPart, queue):
    hasPrefixes = bool(modifierPart)  # if modifier part is empty or not
    subQueue = queue
    negate = False
    while hasPrefixes:
        # handle if there's an indexing or length
        if sliceMatchObj := re.match(r"^(\d*-?\d+):(.*)$", modifierPart):
            # get the prefix and the modifier part
            piecesSliceIndex, modifierPart = sliceMatchObj.groups()

            # get the indicies
            sliceIndicies = piecesSliceIndex.split("-")

            # check if it's a length or two indices
            if len(sliceIndicies) == 2:
                # start and end indicies
                subQueue = queue[int(sliceIndicies[0]) : int(sliceIndicies[1])]
            else:
                # end index or ie length
                subQueue = queue[: int(sliceIndicies[0])]

            hasPrefixes = bool(modifierPart)  # if modifier part is empty or not

        # handle not modifier
        elif modifierPart[0] == "!":
            # flip not modifier
            negate = not negate
            modifierPart = modifierPart[1:]

            hasPrefixes = bool(modifierPart)  # if modifier part is empty or not

        else:
            hasPrefixes = False

    return modifierPart, subQueue, negate


# handle the different operators for the count modifier
def handleCountModifier(countPieces, queue, relationalOperator, num, setNotation=False):
    """Handle the different operators for count modifier"""

    # check each piece
    for piece in countPieces:
        # count the number of occurrences of that piece
        pieceCount = queue.count(piece)

        # handle all the possible operators
        if relationalOperator == "=" or relationalOperator == "==":
            if pieceCount != num:
                if not setNotation:
                    return False
            elif setNotation:
                return True
        elif relationalOperator == "!=":
            if pieceCount == num:
                if not setNotation:
                    return False
            elif setNotation:
                return True
        elif relationalOperator == "<":
            if pieceCount >= num:
                if not setNotation:
                    return False
            elif setNotation:
                return True
        elif relationalOperator == ">":
            if pieceCount <= num:
                if not setNotation:
                    return False
            elif setNotation:
                return True
        elif relationalOperator == "<=":
            if pieceCount > num:
                if not setNotation:
                    return False
            elif setNotation:
                return True
        elif relationalOperator == ">=":
            if pieceCount < num:
                if not setNotation:
                    return False
            elif setNotation:
                return True

    return not setNotation


# handle the before operator
def handleBeforeOperator(beforePieces, afterPieces, queue):
    """Handle the before operator"""
    beforePieces = list(beforePieces)
    afterPieces = list(afterPieces)

    # set notation
    beforeSetNotation = False
    if beforePieces[0] == "[" and beforePieces[-1] == "]":
        beforeSetNotation = True
        beforePieces = beforePieces[1:-1]

    afterSetNotation = False
    if afterPieces[0] == "[" and afterPieces[-1] == "]":
        afterSetNotation = True
        afterPieces = afterPieces[1:-1]

    # tries to match all the pieces in beforePieces before seeing any of the after pieces
    for piece in queue:
        # check if it's an after piece
        if piece in afterPieces:
            if afterSetNotation:
                # remove this piece from the after pieces
                afterPieces.remove(piece)

                if not afterPieces:
                    return False
            else:
                # hit a after piece before getting through all the before pieces
                return False

        # check if it's a before piece
        elif piece in beforePieces:
            # if setNotation then any piece is fine as long as it's before
            if beforeSetNotation:
                return True

            # remove this piece from the before pieces
            beforePieces.remove(piece)

            # if beforePieces is empty
            if not beforePieces:
                return True

    # if gone through the whole queue and still not sure, then assume False
    return False


# check if a queue is allowed by the modifier
def checkModifier(queue, modifierTree):
    """Check if a queue is allowed by the modifier"""
    # holds the current boolean as parse through the modifier tree
    currBool = True

    # operator starts with and
    operator = "&&"

    # for each modifier part in the tree
    for modifierPart in modifierTree:
        if isinstance(modifierPart, list):

            # get the info from prefixes
            subQueue, negate = handlePrefixesInModifier(modifierPart[0], queue)[1:]
            modifierPart = modifierPart[1:]

            # get the boolean from the submodifier
            subModifierCheck = negate ^ checkModifier(subQueue, modifierPart)

            # get new current boolean
            currBool = handleOperatorInModifier(
                currBool, subModifierCheck, operator, "sub modifier"
            )

            # if currBool is False and the rest of the tree are and (which should be common), then return False directly
            if not currBool:
                # try to find any or operators
                if "||" not in modifierTree:
                    # don't find any other '||', therefore all ands or near the end and can simply return False
                    return False

            # clear the operator
            operator = ""

        # handle the modifiers
        elif isinstance(modifierPart, str):
            # handle prefixes
            modifierPart, subQueue, negate = handlePrefixesInModifier(
                modifierPart, queue
            )

            # count modifier
            if countModifierMatchObj := re.match(
                r"^([\[\]TILJSZO*]+)([<>]|[<>=!]?=)(\d+)$", modifierPart
            ):
                # get the different sections of the count modifier
                countPieces, relationalOperator, num = countModifierMatchObj.groups()

                # separate any set notation
                countPiecesParts = filter(
                    None, re.split(r"(\[[TILJSZO*]+\])", countPieces)
                )

                # handle each part
                countBool = True
                for part in countPiecesParts:
                    # set notation
                    setNotation = False
                    if part[0] == "[" and part[-1] == "]":
                        setNotation = True
                        part = part[1:-1]

                    # allow for wildcard
                    if part == "*":
                        part = BAG

                    # get the boolean for the count modifier
                    countBool = handleCountModifier(
                        part,
                        subQueue,
                        relationalOperator,
                        int(num),
                        setNotation=setNotation,
                    )

                    # if any part is False then entire thing is False
                    if not countBool:
                        break

                # get new current boolean
                currBool = handleOperatorInModifier(
                    currBool, negate ^ countBool, operator, "count modifier"
                )

                # if currBool is False and the rest of the tree are and (which should be common), then return False directly
                if not currBool:
                    # try to find any or operators
                    if "||" not in modifierTree:
                        # don't find any other '||', therefore all ands or near the end and can simply return False
                        return False

                # clear the operator
                operator = ""

            # before modifier
            elif beforeModifierMatchObj := re.match(
                r"^([\[\]TILJSZO*]+)<([\[\]TILJSZO*]+)$", modifierPart
            ):
                # get the before and after pieces
                beforePieces, afterPieces = beforeModifierMatchObj.groups()

                # separate any set notation
                beforePiecesParts = filter(
                    None, re.split(r"(\[[TILJSZO*]+\])", beforePieces)
                )
                afterPiecesParts = filter(
                    None, re.split(r"(\[[TILJSZO*]+\])", afterPieces)
                )

                beforeBool = True
                for bPart in beforePiecesParts:
                    for aPart in afterPiecesParts:

                        # get the boolean for if the queue does match the before modifier
                        beforeBool = handleBeforeOperator(bPart, aPart, subQueue)

                        # if any part is False then entire thing is False
                        if not beforeBool:
                            break

                # get new current boolean
                currBool = handleOperatorInModifier(
                    currBool, negate ^ beforeBool, operator, "before modifier"
                )

                # if currBool is False and the rest of the tree are and (which should be common), then return False directly
                if not currBool:
                    # try to find any or operators
                    if "||" not in modifierTree:
                        # don't find any other '||', therefore all ands or near the end and can simply return False
                        return False

                # clear the operator
                operator = ""

            # regex modifier
            elif regexModifierMatchObj := re.match("/(.+)/", modifierPart):
                # get the negate and regex pattern
                regexPattern = regexModifierMatchObj.group(1)

                # get the boolean for if the queue matches the regex pattern
                regexBool = negate ^ bool(re.search(regexPattern, subQueue))

                # get new current boolean
                currBool = handleOperatorInModifier(
                    currBool, regexBool, operator, "regex modifier"
                )

                # if currBool is False and the rest of the tree are and (which should be common), then return False directly
                if not currBool:
                    # try to find any or operators
                    if "||" not in modifierTree:
                        # don't find any other '||', therefore all ands or near the end and can simply return False
                        return False

                # clear the operator
                operator = ""

            # handle operator
            elif modifierPart == "&&" or modifierPart == "||":
                operator = modifierPart

            else:
                # something went wrong
                raise Exception(
                    "Something went wrong when parsing leading to no match to modifiers or operator"
                )

        else:
            # something went wrong
            raise Exception(
                "Something went wrong leading to some modifier that isn't a string or list in the modifier tree"
            )

    # return the boolean
    return currBool


# handle the whole extended sfinder pieces
def handleExtendedSfinderFormatPieces(
    extendedSfinderFormatPieces, sortQueuesBool=True, index=0, depth=0
):
    """Handle the whole extended sfinder pieces"""

    # delimiter between parts
    delimiter = ","

    # holds a list of the queues for each part
    queues = []

    # holds a stack of queues as parsing through the expression
    queueStack: list = []

    # go through each character
    sfinderPieces: str = ""
    while index < len(extendedSfinderFormatPieces):
        char = extendedSfinderFormatPieces[index]

        # delimiter
        if char == delimiter:
            # all the sfinder pieces so far
            if sfinderPieces:
                queueStack.append(parse_input(sfinderPieces))
                sfinderPieces = ""

            # do the product of each part for one long queue
            if len(queueStack) == 1:
                queuesPart = queueStack[0]
            else:
                queuesPart = map("".join, product(*queueStack))

            queues.append(queuesPart)

            # empty stack
            queueStack = []

        # sub expression
        elif char == "(":
            # add the sfinder pieces so far
            if sfinderPieces:
                queueStack.append(parse_input(sfinderPieces))
                sfinderPieces = ""

            # run recursive for expressions in parentheses
            subQueue, index = handleExtendedSfinderFormatPieces(
                extendedSfinderFormatPieces,
                sortQueuesBool=False,
                index=index + 1,
                depth=depth + 1,
            )

            # add this sub queue to the stack
            queueStack.append(subQueue)

        elif char == ")":
            # all the sfinder pieces so far
            if sfinderPieces:
                queueStack.append(parse_input(sfinderPieces))

            # combine everything in the stack
            queues.append(map("".join, product(*queueStack)))

            # combine all the queues so far
            queues = map("".join, product(*queues))

            # return the queues and index
            return queues, index

        # handle modifier
        elif char == "{":
            # all the sfinder pieces so far
            if sfinderPieces:
                queueStack.append(parse_input(sfinderPieces))
                sfinderPieces = ""

            # make the modifier tree
            modifierTree, modifierLength = make_modifier_tree(
                extendedSfinderFormatPieces[index + 1 :], return_length=True
            )

            # if the length makes it the entire string
            if index + modifierLength + 1 == len(extendedSfinderFormatPieces):
                raise Exception(
                    f"Modifier didn't close '{extendedSfinderFormatPieces[index:]}'"
                )

            # get the queues from combining the stack
            queuesPart = map("".join, product(*queueStack))

            # filter the queues with the modifier tree
            queuesPart = filter(
                partial(checkModifier, modifierTree=modifierTree), queuesPart
            )

            # set the stack with just this part
            queueStack = [queuesPart]

            # more index
            index += modifierLength + 1

        # normal sfinder pieces
        elif char not in whitespace:
            sfinderPieces += char

        # increment index
        index += 1

    # if there's any more sfinder pieces at the end
    if sfinderPieces:
        queues.append(parse_input(sfinderPieces))

    # do the product of each part for one long queue
    queuesPart = map("".join, product(*queueStack))

    # add this last part to the queues
    queues.append(queuesPart)

    # do the product of each part for one long queue
    queues = map("".join, product(*queues))

    # sort the queues
    if sortQueuesBool:
        queues = sort_queues(queues)

    # return the queues as a generator object
    return queues


# handle user input and runs the program
def extendPieces(customInput: str | list[str] = argv[1:], printOut=False):
    """Main function for handling user input and program"""

    if not isinstance(customInput, list):
       customInput = [customInput] 

    # get the user input
    userInput = customInput

    # spliting to get the extended sfinder format pieces
    allExtendedSfinderPieces = []
    for argument in userInput:
        allExtendedSfinderPieces.extend(re.split("\n|;", argument))

    # hold all the queues parts
    queues = []

    # go through part of the user input that's a extended sfinder format pieces
    for extendedSfinderPieces in allExtendedSfinderPieces:
        # get the queues from this format
        queuesPart = handleExtendedSfinderFormatPieces(
            extendedSfinderPieces, sortQueuesBool=False
        )
        queues.append(queuesPart)

    # sort the queues
    queues = sort_queues(set(chain(*queues)))

    # return the queues generator obj
    return queues


if __name__ == "__main__":
    # run the main function
    queues = extendPieces()

    print("\n".join(queues))
