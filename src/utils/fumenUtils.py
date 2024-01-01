# Several fumen related functions

import py_fumen_py as py_fumen

def getField(fumen: str, height: int = 4) -> list[str]:
    '''
z   Decodes and returns the field of the fumen without the garbage

    Parameter:
        fumen (str): a fumen code
        height (int): the height of field to return

    Return:
        str: the field represented as a string

    '''

    fields = []

    pages = py_fumen.decode(fumen)
    
    for page in pages:
        # get field object
        field = page.field

        # get the string
        field = field.string(truncated=False, with_garbage=False)

        # truncate to the specified height
        field = "\n".join(field.split("\n")[-height:])

        fields.append(field)

    return fields

if __name__ == "__main__":
    help(py_fumen.Field)
    print(getField(input("Enter a fumen: ")))
