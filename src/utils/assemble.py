# All credits to OctopusTea 
# https://github.com/OctupusTea/py-fumen-util/blob/main/src/py_fumen_util/assemble.py
# -*- coding: utf-8 -*-

from py_fumen_py import *

def cleared_offset(rows_cleared, y):
    for row in rows_cleared:
        if y >= row:
            y += 1
    return y

def assemble(fumen_codes, print_error=True, keep_invalid=True):
    # if fumen codes is just one fumen
    if isinstance(fumen_codes, str):
        fumen_codes = [fumen_codes]

    results = []

    for code in fumen_codes:
        try:
            rows_cleared = set()
            input_pages = decode(code)
            field = input_pages[0].field.copy()

            for page in input_pages:
                operation = page.operation
                if operation is None:
                    if print_error:
                        print('warning: skipped a page with no operation')
                    continue

                for dx, dy in Operation.shape_at(operation.mino,
                                                 operation.rotation):
                    x = operation.x + dx
                    y = cleared_offset(rows_cleared, operation.y+dy)
                    if print_error and field.at(x, y) != Mino._:
                        print('error: operation overlaps with current field')
                    field.fill(x, y, operation.mino)

                new_rows_cleared = set()
                for dy in range(-2, 3):
                    y = cleared_offset(rows_cleared, operation.y+dy)
                    if y >= 0 and field.is_lineclear_at(y):
                        new_rows_cleared.add(y)
                rows_cleared |= new_rows_cleared

            results.append(encode([Page(field=field)]))
        except Exception as e:
            if keep_invalid:
                results.append('')
            if print_error:
                print(e)

    return results

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        for line in assemble(' '.join(sys.argv[1:]).split()):
            print(line)
