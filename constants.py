import hexonia as hx
import pygame as pg
import numpy as np
pg.font.init()
pg.display.init()
MAX_W, MAX_H = pg.display.get_desktop_sizes()[0]
BF = 4
FH = 24
FPS = 60
FONT = font=pg.font.SysFont('couriernew', FH, bold=True)

COLORS = (pg.Color( 53,  53,  53), # cell @ 0
          pg.Color(219,  31, 187), # cell @ 1
          pg.Color(2,  31, 247), # font fg 1
          pg.Color(75,  130, 227), # font fg 2
          pg.Color(111,  0, 34), # font bg 1
          pg.Color(180,  180, 187)) # font bg 2

RULE_CLASSIC = np.array([[0, 0, 0, 1, 0, 0, 0, 0, 0],
                         [0, 0, 1, 1, 0, 0, 0, 0, 0]])

STD_MASK = np.array([[1, 1, 1], # 'Moore' ngbhd
                     [1, 0, 1],
                     [1, 1, 1]])

# DBL_MASK_PT = np.array([[0, 1, 0],
#                         [1, 0, 1],
#                         [0, 0, 0],
#                         [1, 0, 1],
#                         [0, 1, 0]])
DBL_MASK_FT = np.array([[0, 1, 0, 1, 0], # = pt_mask.T
                        [1, 0, 0, 0, 1],
                        [0, 1, 0, 1, 0]])
DBL_MASK_PT = DBL_MASK_FT.T

def get_ngb_mask(shape:tuple, doubled:bool, ft:bool=True) -> np.ndarray:
    m, n = shape
    ngbs = np.zeros(shape)
    if doubled:
        if ft:
            ngbs[m // 2 - 1 : m // 2 + 2, 
                 n // 2 - 2 : n // 2 + 3] = DBL_MASK_FT
        else:
            ...
    else:
        ngbs[m // 2 - 1 : m // 2 + 2, 
             n // 2 - 1 : n // 2 + 2] = STD_MASK
    return ngbs

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

class ArgField(pg.Rect):
    def __init__(self, xy_ofset:tuple[int,int], init_val:str, font:pg.font.Font, arg_name:str, colors:tuple[pg.Color,pg.Color]):
        fg, bg = colors
        name = f'{arg_name:>18}: '
        label = font.render(name, 1, fg, bg)
        super().__init__(xy_ofset[0], xy_ofset[1], 2 * label.get_width(), label.get_height())
        self.label = label
        self.font = font
        self.name = arg_name
        self.default_val = init_val
        self.arg_val = init_val
        self.fg = fg
        self.bg = bg
        self.field = pg.Rect(self.centerx, self.top, self.width / 2, self.height)
    def collidepoint(self, x_y:tuple) -> bool:
        if self.field.collidepoint(x_y):
            return True
        return False
    def reset_val(self) -> None:
        self.arg_val = self.default_val
    def add_char(self, num_char:str):
        self.arg_val += num_char
        self.arg_val = repr(int(self.arg_val)) # clear leading zeros
    def del_char(self):
        self.arg_val = '0' if len(self.arg_val) == 1 else self.arg_val[: -1]
    def draw(self, sfc:pg.Surface, target:bool) -> None:
        sfc.fill(self.bg, self)
        sfc.fill('purple', self.field) if not target else sfc.fill('yellow', self.field)
        sfc.blits([(self.label, self.topleft), (self.font.render(self.arg_val, 1, self.fg), self.field.topleft)])