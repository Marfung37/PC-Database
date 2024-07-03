# -*- coding: utf-8 -*-

# Generate all variable setups
#
# These setups are ones where there's some number of pieces required and
# a number of optional pieces can be placed elsewhere to place the required pieces
#
# Ex: first page is required pieces for the setup while 
# subsequent pages are optional pieces to gain enough coverage
# v115@GhwhDeR4CewhBewwR4wwBtAewhAe1wBtwhJeAgH9gw?hIewhIewhIewhSeAgHEhhlwhQaCeR4BeglAeQaAewwQ4Aeg?WBtglAeQawwAehWAewhAeAtKeAgHAhR4BehWCeR4DegWIeg?WUeAgHAhxDBtEexDBeBtfeAgH

import py_fumen_py as pf
from itertools import combinations

from utils.queue_utils import MINOVALS
from utils.fumen_utils import get_pieces, field_to_fumen

def field_diff(field_base: pf.Field, field_diff: pf.Field) -> pf.Field:
    '''
    field_base - field_diff

    The minos removed are replaced with empty space
    '''

    # copy the base
    new_field = field_base.copy()

    # only need to go up to the lower of the two heights
    height = min(field_base.height(), field_diff.height())

    # go through the field
    for x in range(pf.FieldConstants.WIDTH):
        for y in range(height):

            # if the mino in field diff is filled
            if not field_diff.is_placeable_at(x, y):
                # remove the mino in base
                new_field.fill(x, y, pf.Mino._)
    
    return new_field

def variable_setups(fumen: str, choice: int = 1) -> str:
    '''
    Generate variable setups 

    These setups are ones where there's some number of pieces required and
    a number of optional pieces can be placed elsewhere to place the required pieces

    Parameters:
        fumen (str): a two page fumen where first page is required pieces and 
                     second page have the optional pieces added
        choice (int): the number of combinations (counting term) of these 
                      optional pieces

    Return:
        str: a multipage fumen with first page is required pieces and 
             subsequent pages contain up to <choice> optional pieces
    '''
    
    # verify pages two pages
    pages = pf.decode(fumen)
    if len(pages) != 2:
        raise ValueError(f"Fumen passed to 'variable_setups' has {len(pages)} pages instead of 2 pages")

    # get the required and optional pages
    required_page: pf.Page
    optional_page: pf.Page
    required_page, optional_page = pages

    if required_page.field is None or optional_page.field is None:
        raise ValueError("Page fields are not defined")

    optional_pieces_page = field_to_fumen(
        field_diff(optional_page.field, required_page.field),
    )

    # get the optional_pieces
    optional_pieces: list[pf.Operation] | str 
    optional_pieces = get_pieces(optional_pieces_page, operations = True)[0]

    # shouldn't happen
    if isinstance(optional_pieces, str):
        raise RuntimeError("Optional pieces were able to be type of string")

    # sort the pieces
    optional_pieces.sort(key=lambda x: MINOVALS[x.mino])

    # get all combinations of indices of passed choice
    piece_combinations = []
    for sub_choice in range(1, choice + 1):
        piece_combinations += list(combinations(range(len(optional_pieces)), sub_choice))

    # add each combo of pieces to the required page with required page being first page
    variable_pages = [required_page]
    for combo in piece_combinations:
        chosen_pieces = (optional_pieces[c] for c in combo)

        # make copy of the required page as the start of the new pages
        page: pf.Page = pf.Page()
        page.field = required_page.field.copy()
        
        # add the operations as new page 
        for piece in chosen_pieces:
            page.field.drop(operation = piece, place = True)

        # add to rest of the variable pages
        variable_pages.append(page)
        
    # encode the variable pages to one fumen
    variable_fumen = pf.encode(variable_pages)        
    
    return variable_fumen


if __name__ == "__main__":
    # for rn basic argv
    from sys import argv

    if len(argv) != 3:
        print(f"python {argv[0]} <fumen> <choice>")
        exit()

    fumen = argv[1]
    choice = int(argv[2])
    print(variable_setups(fumen, choice=choice))



