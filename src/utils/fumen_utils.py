# Several fumen related functions

import py_fumen_py as pf
from typing import Callable, Optional
from .disassemble import disassemble
from .queue_utils import MINO2PIECE

def _decode_wrapper(fumen: str) -> list[pf.Page]:
    '''
    Decode the fumen with error handling

    Parameter:
        fumen (str): a fumen code

    Return:
        list[Page]: decoded fumen
    '''

    try:
        pages = pf.decode(fumen)
    except:
        raise RuntimeError(f"Fumen {fumen} could not be decoded")

    return pages

def get_field(fumen: str, height: int = 4) -> list[str]:
    '''
    Decodes and returns the field of the fumen without the garbage

    Parameters:
        fumen (str): a fumen code
        height (int): the height of field to return

    Return:
        str: the field represented as a string

    '''

    fields = []

    pages = _decode_wrapper(fumen)
    
    for page in pages:
        # get field object
        field = page.field

        # if there's no field skip this page
        if field is None:
            continue

        # get the string
        field = field.string(truncated=False, with_garbage=False)

        # truncate to the specified height
        field = "\n".join(field.split("\n")[-height:])

        fields.append(field)

    return fields

def field_to_fumen(field: pf.Field) -> str:
    '''
    Convert a field object to a fumen

    Parameter:
        field (Field): field object

    Return:
        str: a fumen of the field
    '''

    return pf.encode([pf.Page(field=field)])

def get_pieces(fumen: str, operations: bool = False) -> list[list[pf.Operation] | str]:
    '''
    Get the pieces from the field

    Parameters:
        fumen (str): fumen to get pieces from
        operations (bool): if true, output is list of operations otherwise pieces

    Return:
        list: a list of operations or pieces
    '''

    # list to contain the output
    result = []

    # disassemble the fumen
    glue_fumens = disassemble(fumen, keep_duplicates=False, print_error=False)

    # for each fumen output
    for glue_fumen in glue_fumens:
        for gf in glue_fumen:
            fumen_result_ops: list[pf.Operation] = []
            fumen_result_pieces: str = ""

            pages = _decode_wrapper(gf)

            for page in pages:
                page_op: pf.Operation | None = page.operation

                # if there's a page with no operations
                if page_op is None:
                    continue

                if operations:
                    fumen_result_ops.append(page_op)
                else:
                    fumen_result_pieces += MINO2PIECE(page_op.mino)

            if operations:
                result.append(fumen_result_ops)
            else:
                result.append(fumen_result_pieces)

    return result

def is_pc(fumen: str) -> bool:
    '''
    Check if the fumen is a pc and non-empty

    If a page is None, then considered a pc

    Parameter:
        fumen (str): a fumen code

    Return:
        bool: whether the fumen is a pc
    '''

    # decode the fumen
    pages = _decode_wrapper(fumen)

    # go through the pages
    for page in pages:
        # if the page has a field
        if page.field is not None:
            # clear all lines
            if page.field.clear_line() == 0:
                return False

            # check if the height is 0
            if page.field.height() != 0:
                return False

    return True

def get_height(fumen: str) -> int:
    '''
    Get max height of all pages of a fumen

    Parameter:
        fumen (str): a fumen code

    Return:
        int: the maximum height of all pages
    '''

    # get pages
    pages = _decode_wrapper(fumen)
    
    # get the max height all of the pages
    height = 0
    for page in pages:
        if page.field is not None:
            if height < page.field.height():
                height = page.field.height()

    return height


def field_equals(field1: Optional[pf.Field], field2: Optional[pf.Field]) -> bool:
    '''
    field1 == field2
    '''

    if field1 is None or field2 is None:
        return False

    return field1.string() == field2.string()

def permutated_equals(fumen1: str, fumen2: str) -> bool:
    '''
    Fumens are equal even if the pages are in a different order (only considering fields)

    Parameters:
        fumen1 (str): a fumen code
        fumen2 (str): a fumen code

    Return:
        bool: whether the two fumens are the same
    '''

    # if the fumens are the same
    if fumen1 == fumen2:
        return True

    # decode the fumens
    pages1 = _decode_wrapper(fumen1)
    pages2 = _decode_wrapper(fumen2)

    # quick check if the lengths are the same
    if len(pages1) != len(pages2):
        return False

    # check if there's any page in pages1 not in pages2
    for page1 in pages1:
        
        # try to find the same field in pages2
        found = False
        for page2 in pages2:
            if field_equals(page1.field, page2.field):
                found = True
                break

        if not found:
            return False

    return True

def _base_fumen_util(fumen: str, func: Callable[[pf.Page], pf.Page]) -> str:
    '''
    A base fumen where apply a function on each of its pages

    Parameter:
        fumen (str): a fumen code

    Return:
        str: fumen with the function applied to each page
    '''
    # new pages
    new_pages = []

    # get the pages
    pages = _decode_wrapper(fumen)

    # go through page
    for page in pages:
        # apply the function on the page and add to the new pages
        new_pages.append(func(page))

    # encode the new pages into a fumen
    result = pf.encode(new_pages)

    return result

def clear_configs(fumen: str, field: bool = True, operation: bool = False, comment: bool = False) -> str:
    '''
    Remove configs for each page of the fumen

    Parameter:
        fumen (str):        a fumen code
        field (bool):       whether field should be kept
        operation (bool):   whether operation should be kept
        comment (bool):     whether field should be kept

    Return:
        str: fumen with all other configs removed
    '''
    
    removed_configs = lambda page: pf.Page(
                        field=page.field            if field else None, 
                        operation=page.operation    if operation else None, 
                        comment=page.comment        if comment else None
                        )

    return _base_fumen_util(fumen, removed_configs)

def mirror_fumen(fumen: str) -> str:
    '''
    Mirror the fumen

    Parameter:
        fumen (str): a fumen code

    Return:
        str: mirrored fumen
    '''

    def mirror_page(page):
        field = page.field
        field.mirror(mirror_color=True)
        return pf.Page(field=field)

    return _base_fumen_util(fumen, mirror_page)
