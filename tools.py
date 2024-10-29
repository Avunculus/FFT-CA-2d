import pygame as pg
import numpy as np
from string import ascii_letters

# 0. get D.w, D.h
# 1. choose sq|hex_ft|hex_pt
# 2. choose scale
# 3. choose dimsizes
# 4. [choose hood style, scope: for now locked at Moore-1 / VN-1 for sq / hex]
# 5. choose/decode rule

# # encoding: similar to HROT (higher rule outer totalistic) notation from wiki: https://conwaylife.com/wiki/Larger_than_Life
#  'GNBS' rule encoding: grid, ngbhd, birth, survival
#  constant: outer-totalistic, binary values
#  GX -> hex grid  /  GQ
#  NV1 -> Von Neuman ngbhd of range 1 / NM3 -> Moore ngbhd of range 3
#  B2,3 = B2-3 -> birth on 2 or 3  / S0,3-5,7,9 -> survive on 0,3,4,5,7,9
#  EX: GX, NV1, B2,4, S3,5 

# so, need from menu: GAME: GNBS / VIEW: orientation (ft|pt), viewscale (cell px width, px height), gridsize (cols, rows)

# #UI
# Menu: input CA code string, or input individual game params, or load from file.
# Game: autoflip on|off, increment 1 turn, click-toggle cell (single, shapes + rotations), save game as, randomize/reset

# menu functionality:
# field nav: tab-thru, click-focus
# accept Game args (GNBS) -> accept view args (orientation, gridsize, viewscale) -> GO 
# field types: 
#   text in: alphanum + ',-' | decimal only
#   binary boxes (visible toggle, no text in)
# flow: 2 screens?
#   init: view/size fileds INACTIVE (can't interact or nav to) until game declared
#       can interact with: game_code (input code directly)
#                          individual code fields (input by field)
#       Two options for declare: by code (if valid, updates fields to reflect code)
#                                by fields (if valid, updates code to reflect fields)
#       [third option, from file, to be added]
#   declare game: game dec INACTIVE; view/size fileds ACTIVE

# 0: display shape
# 1: 'grid type'
# 2: -> 'hood type', -> 'hood range'
# 3: -> b_rule, -> s_rule

# 2 menus: 'game', then 'view'
# mthods: cycle (seq), receive char (int, seq), set_focus, lose_focus, __repr__ 
# class ChoiceField(pg.Rect):
#     def __init__(self, choices:tuple[str]):
#         ...

# class TextField(pg.Rect):
#     def __init__(self, origin:tuple, allowed:str):
#         ...

# class Menu(pg.Rect): # contains, draws label-field pairs. Field = textRect|binary boxes
#     def __init__(self, origin:tuple, font:pg.font.Font, colors:tuple[pg.Color]):
#         ...

# class TextInput(pg.Rect):
#     def __init__(self, origin:tuple, font:pg.font.Font, colors:tuple[pg.Color], *fields:tuple[str,str,str]):
#         """constructs / contains / manages sub-rects.
#         colors: [0] label text, [1] label bg, [2] value text, [3] value bg
#         fields: [0] label text, [1] default txt, [2] min (val or length), [3] max"""

#         ...

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
            if ngbhd == 'm': # moore ngbhd: adj + diag
                rule = np.zeros((2, kernel.size))
            elif ngbhd == 'v':
                rule = np.zeros((2, 2 * scope * (scope + 1) + 1))
                with np.nditer(kernel, flags=['multi_index'], op_flags=['readwrite']) as it:
                    for _ in it:
                        if abs(scope - it.multi_index[0]) + abs(scope - it.multi_index[1]) > scope:
                            kernel[it.multi_index] = 0 
            else: return False
        case 'x':
            if ngbhd == 'v': 
                kernel = np.zeros((3 + 2 * (scope - 1),
                                   5 + 4 * (scope - 1))) # default flat-top hexes. For pt, use k.T
                center = (kernel.shape[0] // 2, kernel.shape[1] // 2)
                ... # ??? kernel for n>1-degree neighbors ???
                rule = np.zeros((2, 3 * scope * (scope + 1) + 1))
            elif ngbhd == 'm':
                print('error: \'m\' (Moore) neighborhood requested for hex grid')
                return False
            else: return False
        case _: print('error: invalid grid type'); return False
    # rule.values
    for i, vals in enumerate(b_s[1:].split(',s')):
        for ix in vals.split(','):
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

# k, r = decode_game_string('gq,nm5,b5,s2,3')
# print(k)
# print(r)
