# -*- coding: utf-8 -*-

import sys

from dataclasses import dataclass
from py_fumen_py import *

PIECE_MAPPINGS = {
    Mino.I: [
        [[1, 0], [0, 0], [2, 0], [3, 0]],
        [[0, 1], [0, 0], [0, 2], [0, 3]],
    ],
    Mino.L: [
        [[1, 0], [0, 0], [2, 0], [2, 1]],
        [[0, 1], [0, 0], [0, 2], [-1, 2]],
        [[1, 1], [0, 0], [0, 1], [2, 1]],
        [[0, 1], [0, 0], [1, 0], [0, 2]],
    ],
    Mino.O: [
        [[0, 0], [1, 0], [0, 1], [1, 1]]
    ],
    Mino.Z: [
        [[0, 0], [1, 0], [-1, 1], [0, 1]],
        [[1, 1], [0, 0], [0, 1], [1, 2]]
    ],
    Mino.T: [
        [[1, 0], [0, 0], [1, 1], [2, 0]],
        [[0, 1], [0, 0], [-1, 1], [0, 2]],
        [[0, 1], [0, 0], [-1, 1], [1, 1]],
        [[0, 1], [0, 0], [1, 1], [0, 2]],
    ],
    Mino.J: [
        [[1, 0], [0, 0], [0, 1], [2, 0]],
        [[1, 1], [0, 0], [1, 0], [1, 2]],
        [[-1, 1], [0, 0], [-2, 1], [0, 1]],
        [[0, 1], [0, 0], [0, 2], [1, 2]],
    ],
    Mino.S: [
        [[1, 0], [0, 0], [1, 1], [2, 1]],
        [[0, 1], [0, 0], [-1, 1], [-1, 2]]
    ],
}

@dataclass
class AbsoluteOperation(Operation):
    abs_y: int

def is_inside(field, x, y):
    return 0 <= x < FieldConstants.WIDTH and 0 <= y < field.height()

def is_floating(field, mino_positions):
    # if there's a 'X' under any of the minos or on floor
    for x, y in mino_positions:
        if(y == 0 or field.at(x, y - 1) == Mino.X):
            return False;
    return True

def center_mino(mino_positions):
    return mino_positions[0];

def place_piece(field, mino_positions):
    for x, y in mino_positions:
        field.fill(x, y, Mino.X)

def remove_line_clears(field):
    lines = []
    lines_cleared = []
    for i, line in enumerate(field):
        if all(mino is Mino.X for mino in line):
            lines_cleared.append(i)
        else:
            lines.append(line)
    return Field(field=lines, garbage=field[:0]), lines_cleared

def make_empty_field(field):
    field = field.copy()
    for line in field:
        for i, mino in enumerate(line):
            if mino.is_colored():
                line[i] = Mino._
    return field

def any_remaining_pieces(field):
    for line in field:
        for mino in line:
            if mino.is_colored():
                return True
    return False

# encode operations for faster comparisons
def encode_operation(operation):
    # encode into 20 bits
    # type has 9 possible (4 bits)
    # rotation has 4 possible (2 bits)
    # x has WIDTH (10) possible (4 bits)
    # absY has height (20) possible (5 bits)
    # y has height (20) possible (5 bits)
    ct = operation.mino;
    ct = (ct << 2) + operation.rotation;
    ct = (ct << 4) + operation.x;
    ct = (ct << 5) + operation.abs_y;
    ct = (ct << 5) + operation.y;
    return ct

def decode_operation(ct):
    y = ct & 0x1F; ct >>= 5;
    ct >>= 5; # remove the absolute Y position
    x = ct & 0xF; ct >>= 4;
    rotation = Rotation(ct & 0x3); ct >>= 2;
    mino = Mino(ct)

    return Operation(mino=mino, rotation=rotation, x=x, y=y)

def duplicate_pieces(pieces_arr, all_pieces_arr):
    # discard y value
    pieces_set = set(map(lambda x: x >> 5, pieces_arr))

    for arr in all_pieces_arr:
        if len(pieces_set) != len(arr):
            continue

        # discard y value
        abs_arr = map(lambda x: x >> 5, arr)
        if all([x in pieces_set for x in abs_arr]):
            return True

    return False

def get_pieces(x0, y0, field, pieces_arr, all_pieces_arr, total_lines_cleared):
    for y in range(y0, field.height()):
        for x in range(x0 if y == y0 else 0, FieldConstants.WIDTH):
            if field.at(x, y).is_colored():
                piece = field.at(x, y)
                for state, piece_shape in enumerate(PIECE_MAPPINGS[piece]):
                    mino_positions = [[x+dx, y+dy] for dx, dy in piece_shape]
                    for px, py in mino_positions:
                        if not is_inside(field, px, py) or field.at(px, py) != piece:
                            break
                    else:
                        if is_floating(field, mino_positions):
                            continue 

                        new_field = field.copy()
                        place_piece(new_field, mino_positions)
                        new_field, this_lines_cleared = remove_line_clears(new_field)

                        abs_y = center_mino(mino_positions)[1]
                        i = 0
                        while i < len(total_lines_cleared) and total_lines_cleared[i] <= abs_y:
                            abs_y += 1
                            i += 1

                        x0, y0 = (0, 0) if this_lines_cleared else (max(x - 1, 0), max(y - 1, 0))
                        new_total_lines_cleared = total_lines_cleared[:]
                        for i, line_num in enumerate(this_lines_cleared):
                            if i > 0:
                                line_num -= this_lines_cleared[i - 1] + 1

                            j = 0
                            while j < len(new_total_lines_cleared) and new_total_lines_cleared[j] <= line_num:
                                line_num += 1
                                j += 1
                            new_total_lines_cleared.insert(j, line_num)

                        new_piece_arr = pieces_arr[:]
                        new_piece_arr.append(encode_operation(
                            AbsoluteOperation(
                                mino=piece, 
                                rotation=Rotation(state).shifted(2),
                                x=center_mino(mino_positions)[0],
                                y=center_mino(mino_positions)[1], 
                                abs_y=abs_y
                            )
                        ))

                        get_pieces(x0, y0, new_field, new_piece_arr, all_pieces_arr, new_total_lines_cleared)

    if(not any_remaining_pieces(field) and not duplicate_pieces(pieces_arr, all_pieces_arr)):
        all_pieces_arr.append(pieces_arr)

def disassemble(fumen_codes, print_error=True, keep_invalid=True):
    all_pieces_arr = []
    results = []
    fumen_issues = 0

    for code in fumen_codes:
        try:
            input_pages = decode(code)
            this_disassembles = []
            for page in input_pages:
                field = page.field
                empty_field = make_empty_field(field)
                all_pieces_arr.clear()

                get_pieces(0, 0, field, [], all_pieces_arr, [])

                if print_error and not all_pieces_arr:
                    print(code, "couldn't be disassembled")
                    fumen_issues += 1

                for pieces_arr in all_pieces_arr:
                    pages = [Page(field=empty_field, operation=decode_operation(pieces_arr[0]))]
                    for encoded_op in pieces_arr[1:]:
                        pages.append(Page(operation=decode_operation(encoded_op)))

                    this_disassembles.append(encode(pages))

                if print_error and len(all_pieces_arr) > 1:
                    results.append(
                        'Warning: {} led to {} outputs: {}'.format(
                            code, len(all_pieces_arr), ' '.join(this_disassembles)
                        )
                    )
            results += this_disassembles
        except Exception as e:
            if keep_invalid:
                results.append(Page())
            if print_error:
                print(e)

    if print_error and fumen_issues > 0:
        print("Warning: {} fumen couldn't be disassembled".format(fumen_issues))

    return results

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for line in disassemble(' '.join(sys.argv[1:]).split()):
            print(line)
