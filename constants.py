import hexonia as hx
import pygame as pg
import numpy as np
from random import shuffle
pg.font.init()
pg.display.init()
MAX_W, MAX_H = pg.display.get_desktop_sizes()[0]
BF = 4
FH = 24
FPS = 60
pg.colordict
FONT = pg.font.SysFont('couriernew', FH, bold=True)
FONT_SMALL = pg.font.SysFont('couriernew', 12, bold=True)
COLORS = (pg.Color( 53,  53,  53), # cell @ 0
          pg.Color(178, 34, 34), #219,  31, 187), # cell @ 1
          pg.Color(2,  31, 247), # font fg 1
          pg.Color(75,  130, 227), # font fg 2
          pg.Color(111,  0, 34), # font bg 1
          pg.Color(180,  180, 187)) # font bg 2

RULE_CLASSIC = np.array([[0, 0, 0, 1, 0, 0, 0, 0, 0],
                         [0, 0, 1, 1, 0, 0, 0, 0, 0]])

STD_MASK = np.array([[1, 1, 1], # 'Moore' ngbhd
                     [1, 0, 1],
                     [1, 1, 1]])

PSEUDO_HEX = np.array([[0, 1, 1],
                       [1, 0, 1],
                       [1, 1, 0]])

def sprinkle(seed_count:int, area:tuple[int,int]) -> np.ndarray:
    if area[0] * area[1] < seed_count:
        print(f'error: seed count too big ({seed_count= } // {area= }')
        return False
    kernel = [1] * seed_count + [0] * (area[0] * area[1] - seed_count)
    shuffle(kernel)
    kernel = np.array(kernel).reshape(area)
    return kernel

HEXTEST = {'HexTest' : PSEUDO_HEX}

SEEDS = {'Blocks'    : sprinkle(81, (200, 200)),
         'Contained Chaos' : np.concatenate([sprinkle(12, (8, 8)), np.zeros((96, 8)), sprinkle(12, (8, 8))], axis=0),
         'H-Trees'   : np.array([[1, 0, 1],
                                 [0, 1, 0],
                                 [1, 0, 1]]),
         'Hexamoeba' : np.array([[0, 1, 0, 1, 0],
                                 [1, 0, 1, 0, 1],
                                 [0, 1, 0, 1, 0]])}

# Hex neighborhoods (flat-top)
# range=2
# [0, 0, 1, 0, 1, 0, 1, 0, 0]
# [0, 1, 0, 1, 0, 1, 0, 1, 0]
# [1, 0, 1, 0, X, 0, 1, 0, 1]
# [0, 1, 0, 1, 0, 1, 0, 1, 0]
# [0, 0, 1, 0, 1, 0, 1, 0, 0]
# range=3
# [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0]
# [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0]
# [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
# [1, 0, 1, 0, 1, 0, X, 0, 1, 0, 1, 0, 1]
# [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
# [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0]
# [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0]

DBL_MASK_FT = np.array([[0, 1, 0, 1, 0], # = pt_mask.T
                        [1, 0, 0, 0, 1],
                        [0, 1, 0, 1, 0]])
DBL_MASK_PT = DBL_MASK_FT.T

def make_bg(shape:tuple, scale:tuple) -> pg.Surface:
    m, n = shape
    arr = np.zeros(shape)
    bg = pg.Surface(shape)
    color = bg.map_rgb(0, 0, 0)
    inviz = bg.map_rgb(11, 22, 63)
    bg.set_colorkey(inviz)
    rows = (np.array([inviz, color] * (m // 2)),
            np.array([color, inviz] * (m // 2)))
    for i in range(n):
        arr[:, i] = rows[i % 2]
    pg.surfarray.blit_array(bg, arr)
    bg = pg.transform.scale(bg, (m * scale[0], n * scale[1]))
    return bg

def parts_to_code(text:list[str]) -> str:
    code = 'G'
    code += 'x,N' if text[0] == 'hexagon' else 'q,N'
    code += 'v' if text[1] =='VonNeuman' else 'm'
    code += text[2] + ',B' + text[3] + ',S' + text[4]
    return code


def decode_game_string(code:str) -> tuple[np.ndarray,np.ndarray]:
    """Returns: 2-tuple of arrays:: [0]: kernel/ngb mask (c, r); [1]: rule array (2, n)"""
    # in: key is decimal or in 'xqvm,-gnbs'
    code = code.casefold().replace(' ', '')
    # each key once
    for key in 'gnbs':
        if code.count(key) != 1:
            print(f'game string code error: \'{key}\' present {code.count(key)} times') 
            return False
    # keys in order
    if not code.index('g') < code.index('n') < code.index('b') < code.index('s'):
        print(f'error: game code string args out of order: \'{code})\'')
        return False
    # EX: 'gx,nv2,b1,2,4-8,s10-11,13'
    grid, ngbhd, b_s = code.split(',', maxsplit=2)
    ngbhd, scope = (ngbhd[1], int(ngbhd[2:])) # ngbhd='v' or 'm'
    # kernel.shape, kernel.values, rule.shape
    match grid[-1]:
        case 'q':
            kernel = np.ones((2 * scope + 1,
                              2 * scope + 1))
            kernel[scope, scope] = 0
            if ngbhd == 'm': # square moore ngbhd: adj + diag
                rule = np.zeros((2, kernel.size))
            elif ngbhd == 'v': # square vn 
                rule = np.zeros((2, 2 * scope * (scope + 1) + 1))
                with np.nditer(kernel, flags=['multi_index'], op_flags=['readwrite']) as it:
                    for _ in it:
                        if abs(scope - it.multi_index[0]) + abs(scope - it.multi_index[1]) > scope:
                            kernel[it.multi_index] = 0 
            else: return False
        case 'x':
            if ngbhd == 'v': # hex vn 
                shape = (1 + 2 * scope, 1 + 4 * scope)
                kernel = np.zeros(shape) # default flat-top hexes. For pt, use k.T
                origin = shape[0] // 2
                for q in range(scope): # center line: omit target (center cell)
                    kernel[origin, 2 * q] = 1
                    kernel[origin, -1 - 2 * q] = 1
                for ofst in range(1, scope + 1): # lines above & below
                    line = np.array([1, 0] * (shape[0]-ofst))
                    kernel[origin - ofst, ofst: ofst + line.size] = line
                    kernel[origin + ofst, ofst: ofst + line.size] = line
                rule = np.zeros((2, 3 * scope * (scope + 1) + 1))
            elif ngbhd == 'm':
                print('error: \'m\' (Moore) neighborhood requested for hex grid')
                return False
            else: return False
        case _: print('error: invalid grid type'); return False
    # rule.values
    for i, line in enumerate(b_s[1:].split(',s')):
        for ix in line.split(',') if ',' in line else [line]:
            if ix:
                if '-' not in ix:
                    ix = int(ix)
                    if ix > rule.shape[1] - 1:
                        print(f'error: rule out of bounds: index = {ix}, {rule.shape[1]= }')
                        return False
                    else:
                        rule[i, ix] = 1
                else:
                    lo, hi = [int(j) for j in ix.split('-')]
                    if int(hi) > rule.shape[1] - 1:
                        print(f'error: rule out of bounds: index = {hi}, {rule.shape[1]= }')
                        return False
                    else:
                        rule[i, int(lo) : int(hi) + 1] = 1
    return (kernel, rule)
