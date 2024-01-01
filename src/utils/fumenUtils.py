# Several fumen related functions

import py_fumen_py as py_fumen

def getField(fumen: str, pageNum: int = 0) -> str:
    '''
    Decodes and returns the field of the fumen without the garbage

    Parameter:
        fumen (str): a fumen code
        pageNum (int): a page of the fumen

    Return:
        str: the field represented as a string

    '''

    pages = py_fumen.decode(fumen)
    field = (pages[pageNum].field).string(with_garbage=False)

    return field

if __name__ == "__main__":
    print(getField(input("Enter a fumen: ")))
