from constants import *

class ChoiceField(pg.Rect):
    def __init__(self, name:str, choices:list[str], font:pg.font.Font=FONT):
        label = font.render(name + ': ', 1, COLORS[2])
        super().__init__((0, 0), (font.size('W' * max([len(c) for c in choices]))[0] + 2 * BF, font.get_height() + BF)) # defined as ui rect (not incl label)
        self.label = label
        self.label_pos = (0, 0) # blit label here
        self.choices = choices
        self.text = choices[0]
    def cycle(self, step:int) -> None:
        self.text = self.choices[(self.choices.index(self.text) + step) % len(self.choices)]
    def reset(self):
        self.text = self.choices[0]
    def clear(self):
        self.reset()

class TextField(pg.Rect):
    def __init__(self, name:str, allowed:str, default:str, max_chars:int, font:pg.font.Font=FONT):
        label = font.render(name + ': ', 1, COLORS[2])
        super().__init__((0, 0), (font.size('W' * max_chars)[0] + 2 * BF, font.get_height() + BF)) # defined as ui rect (not incl label)
        self.label = label
        self.label_pos = (0, 0) # blit label here
        self.allowed = allowed
        self.default = default
        self.max_chars = max_chars
        self.text = default
    def reset(self):
        self.text = self.default
    def clear(self): 
        self.text = ''
    def add_char(self, char):
        if char in self.allowed and len(self.text) < self.max_chars:
            self.text += char

class Menu(pg.Rect):
    # container for filedrects, determines total sfc size, navigates focus, manages draws
    def __init__(self, *fields:TextField|ChoiceField):
        column_div  = max([r.label.get_width() for r in fields]) + BF
        w = column_div + max([r.w for r in fields]) + BF
        h = 2 * BF + sum([r.h for r in fields]) + BF * (len(fields) - 1) + 2 * (fields[0].h + BF)
        super().__init__(0, 0, w, h)
        # reposition & get label offset (rt align)
        for i, rect in enumerate(fields):
            rect.left = column_div
            rect.top = BF + i * (rect.h + BF)
            rect.label_pos = (column_div - rect.label.get_width(), rect.top)
        self.fields = fields
        self.field_h = fields[0].height
        self.focus = self.fields[0]
        self.feedback = ['', '']
        self.msg_area = pg.Rect(self.fields[-1].bottomleft, (self.w, self.h - self.fields[-1].bottom))
        self.win:pg.Surface = None
    
    def reset_field(self) -> None:
        self.focus.reset()
        self.update_fields()
    def clear_field(self) -> None:
        self.focus.clear()
        self.update_fields()
    def draw_all(self):
        self.win.fill('black')
        [self.win.fill(COLORS[5] if r==self.focus else COLORS[4], r) for r in self.fields]
        self.win.blits([(r.label, r.label_pos) for r in self.fields] + \
                       [(FONT.render(r.text, 1, COLORS[3]), r) for r in self.fields])  
    def update_fields(self) -> None:
        [self.win.fill(COLORS[5] if r==self.focus else COLORS[4], r) for r in self.fields]
        self.win.blits([(FONT.render(r.text, 1, COLORS[3]), r) for r in self.fields])
        self.report()
    def report(self, line:str='') -> None:
        if line: self.feedback = self.feedback.insert(0, line)[:2]
        self.win.fill('black', self.msg_area)
        self.win.blits([(FONT.render(line, 1, 'green'), (BF, self.bottom + BF + i * self.field_h)) \
                        for i, line in enumerate(self.feedback)])
    def click(self, pos:tuple):
        for rect in [r for r in self.fields if r.collidepoint(pos)]:
            self.focus = rect
            self.update_fields()
    def cycle_choice(self, step:int) -> None:
        step = -1 if step == 0 else 1
        if isinstance(self.focus, ChoiceField):
            self.focus.cycle(step)
            self.update_fields()
        self.update_fields()
    def cycle_fields(self, step:int) -> None:
        self.focus = self.fields[(self.fields.index(self.focus) + step) % len(self.fields)]
        self.update_fields()
    def add_char(self, char):
        if isinstance(self.focus, TextField):
            self.focus.add_char(char)
        self.update_fields()


# def get_user_args():
#     """
#     From: system (display dimensions) & user text input 
#     Returns: (cols: int, rows: int, scale_x: int, scale_y: int, doubled: bool)
#     """
    # for update:
    # FIELD           VAL_RANGE                       DEFAULT                         DEPEND.
    # =============   ==========================      ==========================      =======================================
    # grid_type       square, hex_ft, hex_pt          hex_ft                          --

    # grid_shape      hex: ([6->D.w], [6->D.h])       hex_ft: (D.w//5, D.h//3)        grid_type, D.w, D.h
    #                 sq:  ([3->D.w], [3->D.h])       hex_pt: (D.w//3, D.h//5)    

    # scale           min = (1, 1)                    hex_ft: (5, 3); hex_pt: (3, 5)  grid_shape, grid_type, D.w, D.h 
    #                 max = D.w//cols, D.h//rows      square: (4, 4)

    # hood_type       VonNeuman (adj. ngbs only),     hex: VonNeuman (required)       grid_type
    #                 Moore (adj. and diag. ngbs)     square: Moore (can be either)

    # hood_magnitude  int [1->min([D.w, D.h])//2]     1                               D.w, D.h

    # rule            shape = (2, hood_size + 1)      B3/S23                          hood_mag., hood_type, etc.
    #                 val_range = 0|1
    
    # win  = pg.display.set_mode((960, 540), flags=pg.NOFRAME)
    # font = pg.font.SysFont('couriernew', FH, bold=True)
    # names    = ['cols', 'rows', 'scale_x', 'scale_y', 'doubled']
    # types =    [ int     ,  int     ,  int  ,  int  ,  int    ]
    # defaults = [str(1920 // 5), str(1080 // 3), '5', '3', '1']

    # ui = {arg_name: ArgField((12, 12 + i * FH), defaults[i], font, arg_name, COLORS[-2 :]) for i, arg_name in enumerate(names)}

    # target = 'scale_x'
    # [r.draw(win, n==target) for n, r in ui.items()]
    # clock = pg.time.Clock()
    # running = True
    # while running :
    #     clock.tick(FPS)
    #     for event in pg.event.get():
    #         match event.type:
    #             case pg.QUIT:
    #                 return False
    #             case pg.TEXTINPUT:
    #                 if event.text.isnumeric() and target:
    #                     ui[target].add_char(event.text)
    #                     [r.draw(win, n==target) for n, r in ui.items()]
    #             case pg.MOUSEBUTTONDOWN:
    #                 target = ''
    #                 for key in [n for n, r in ui.items() if r.collidepoint(event.pos)]:
    #                     target = key
    #                 [r.draw(win, n==target) for n, r in ui.items()]
    #             case pg.KEYDOWN:
    #                 match event.key:
    #                     case pg.K_UP:
    #                         target = names[names.index(target) - 1]
    #                         [r.draw(win, n==target) for n, r in ui.items()]
    #                     case pg.K_DOWN:
    #                         target = names[(names.index(target) + 1) % len(names)]
    #                         [r.draw(win, n==target) for n, r in ui.items()]
    #                     case pg.K_ESCAPE:
    #                         if target:
    #                             ui[target].arg_val = '0'
    #                             [r.draw(win, n==target) for n, r in ui.items()]
    #                     case pg.K_BACKSPACE:
    #                         if target:
    #                             ui[target].del_char()
    #                             [r.draw(win, n==target) for n, r in ui.items()]
    #                     case pg.K_q:
    #                         if event.mod & pg.KMOD_CTRL:
    #                             return False
    #                     case pg.K_RETURN | pg.K_KP_ENTER:
    #                         cols, rows, scale_x, scale_y, doubled = [types[names.index(n)](r.arg_val) for n, r in ui.items()]
    #                         doubled = bool(doubled)
    #                         disp_w, disp_h = pg.display.get_desktop_sizes()[0]  # check fit to display max
    #                         if cols >= 6 and cols * scale_x <= disp_w and rows >= 6 and rows * scale_y <= disp_h: # min 6x6
    #                             if doubled:
    #                                 cols -= cols % 2 # chck even #s?
    #                                 rows -= rows % 2
    #                             pg.display.quit()
    #                             return (cols, rows, scale_x, scale_y, doubled)
    #     pg.display.update()


#     clock = pg.time.Clock()
#     autoflip = False
#     running = True

#     while running:
#         clock.tick(FPS)
#         for event in pg.event.get():
#             match event.type:
#                 case pg.QUIT:
#                     return False
#                 case pg.KEYDOWN:
#                     match event.key:                
#                         case pg.K_q: # quit
#                             if event.mod & pg.KMOD_CTRL:
#                                 return False
#                         case pg.K_n: # new grid
#                             if event.mod & pg.KMOD_CTRL:
#                                 pg.display.quit()
#                                 return True
#                         case pg.K_r: # re-set, randomize
#                             if event.mod & pg.KMOD_CTRL: 
#                                 autoflip = False
#                                 grid = np.random.random(shape).round()
#                                 show(win, grid.astype(np.int64), bg_img)
#                         case pg.K_SPACE:
#                             autoflip = not autoflip
#                         case pg.K_RIGHT:
#                             grid = fft_flip(grid, ngbs, rule)
#                             show(win, grid.astype(np.int64), bg_img)
#         if autoflip: # advance 1 gen 
#             grid = fft_flip(grid, ngbs, rule) 
#             show(win, grid.astype(np.int64), bg_img)
#         pg.display.update()