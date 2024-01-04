# Several fumen related functions

import py_fumen_py as pf
from .disassemble import disassemble

def getField(fumen: str, height: int = 4) -> list[str]:
    '''
    Decodes and returns the field of the fumen without the garbage

    Parameters:
        fumen (str): a fumen code
        height (int): the height of field to return

    Return:
        str: the field represented as a string

    '''

    fields = []

    pages = pf.decode(fumen)
    
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

    # disassemble the fuemn
    glue_fumens = disassemble(fumen)[0]

    # for each fumen output
    for glue_fumen in glue_fumens:
        fumen_result = []
        
        # decode the fumen for the pages
        pages = pf.decode(glue_fumen)

        for page in pages:
            if operations:
                fumen_result.append(page.operation)
            else:
                fumen_result.append(page.operation.mino)

        result.append(fumen_result)
            
    return result
    
if __name__ == "__main__":
    print(get_pieces(input("Enter a fumen: ")))
