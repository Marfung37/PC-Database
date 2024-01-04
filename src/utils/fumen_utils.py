# Several fumen related functions

import py_fumen_py as pf
from typing import Callable
from .disassemble import disassemble

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

def get_pieces(fumen: str, operations: bool = True) -> list:
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
    glue_fumens = disassemble(fumen)[0]

    # for each fumen output
    for glue_fumen in glue_fumens:
        fumen_result = []
        
        # decode the fumen for the pages
        pages = _decode_wrapper(glue_fumen)

        for page in pages:
            if operations:
                fumen_result.append(page.operation)
            else:
                fumen_result.append(page.operation.mino)

        result.append(fumen_result)
            
    return result

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

def clear_flags(fumen: str) -> str:
    '''
    Remove all other configs for each page of the fumen other than the field

    Parameter:
        fumen (str): a fumen code

    Return:
        str: fumen with all other configs removed
    '''
    
    removed_configs = lambda page: pf.Page(field=page.field)

    return _base_fumen_util(fumen, removed_configs)

def mirror_fumen(fumen: str) -> str:
    '''
    Mirror the fumen

    Parameter:
        fumen (str): a fumen code

    Return:
        str: mirrored fumen
    '''

    mirror_page = lambda page: pf.Page(field=page.field.mirror(mirror_colors=True))

    return _base_fumen_util(fumen, mirror_page)

if __name__ == "__main__":
    print(get_pieces(input("Enter a fumen: ")))
