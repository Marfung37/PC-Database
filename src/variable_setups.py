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

from utils.disassemble import disassemble
from utils.assemble import assemble
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
    required_page, optional_page = pages

    # glue the required page
    required_pieces_pages = pf.decode(
        disassemble(field_to_fumen(required_page.field))[0][0]
    )

    # clear line clears in each of the pages
    required_field_cleared = required_page.field.copy()
    required_field_cleared.clear_line()
    optional_field_cleared = optional_page.field.copy()
    optional_field_cleared.clear_line()
    
    # get the optional_pieces
    optional_pieces = get_pieces(field_to_fumen(
        field_diff(optional_field_cleared, required_field_cleared)
    ))[0]

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

        # make copy of the required pieces as the start of the new pages
        new_pages = required_pieces_pages[:]
        
        # add the operations as new page 
        for piece in chosen_pieces:
            new_pages.append(pf.Page(operation=piece))

        # combine all the pieces into one page
        assembled_fumen = assemble(pf.encode(new_pages), print_error=False)[0]
        variable_page = pf.decode(assembled_fumen)[0]
        
        # add to rest of the variable pages
        variable_pages.append(variable_page)
        
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



