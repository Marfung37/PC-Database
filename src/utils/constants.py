from py_fumen_py import Mino

MINOVALS = {
    Mino.T: 1,
    Mino.I: 2,
    Mino.L: 3,
    Mino.J: 4,
    Mino.S: 5,
    Mino.Z: 6,
    Mino.O: 7,
}

PIECEVALS = {
    'T': 1,
    'I': 2,
    'L': 3,
    'J': 4,
    'S': 5,
    'Z': 6,
    'O': 7,
}

MIRRORPIECES = {
    'L': 'J',
    'J': 'L',
    'S': 'Z',
    'Z': 'S',
}
