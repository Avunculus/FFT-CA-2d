import pygame as pg

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

class ToggleBox(pg.Rect):
    def __init__(self, origin:tuple, font:pg.font.Font, options:tuple[str,str]):
        ...

class TextField(pg.Rect):
    def __init__(self, origin:tuple, ):
        ...

class Menu(pg.Rect): # contains, draws label-field pairs. Field = textRect|binary boxes
    def __init__(self, origin:tuple, font:pg.font.Font, colors:tuple[pg.Color]):
        ...

class TextInput(pg.Rect):
    def __init__(self, origin:tuple, font:pg.font.Font, colors:tuple[pg.Color], *fields:tuple[str,str,str]):
        """constructs / contains / manages sub-rects.
        colors: [0] label text, [1] label bg, [2] value text, [3] value bg
        fields: [0] label text, [1] default txt, [2] min (val or length), [3] max"""

        ...
m = Menu(('Game code', TextField()))