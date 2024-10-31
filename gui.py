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

HELP_TEXT = ['MENU: Input game code, choose from saved games, or input game attributes, then press [enter] to proceed.',
             '      Use mouse or keys [up/down/left/right/tab] to navigate. Press [del] to clear field, [esc] for default.',
             'GAME: [ctrl + q]: quit || [ctrl + r]: randomize || [ctrl + c]: clear || [ctrl + n]: new game',
             '      [spc]: (un)pause || [right]: advance one turn || [left click]: toggle cell']

class Menu(pg.Rect):
    # container for filedrects, determines total sfc size, navigates focus, manages draws
    def __init__(self, *fields:TextField|ChoiceField, break_before:tuple[int]=()):
        column_div  = max([r.label.get_width() for r in fields]) + BF
        w = column_div + max([r.w for r in fields]) + BF
        h = 2 * BF + sum([r.h for r in fields]) + BF * (len(fields) - 1) + \
            (len(HELP_TEXT) + len(break_before)) * (fields[0].h + BF) # 2 rows for feedback + 1 per break_ix
        super().__init__(0, 0, w, h)
        # reposition & get label offset (rt align)
        k = 0
        for i, rect in enumerate(fields):
            rect.left = column_div
            if i in break_before: k += 1
            rect.top = BF + (i + k) * (rect.h + BF)
            rect.label_pos = (column_div - rect.label.get_width(), rect.top)
        self.fields = fields
        self.field_h = fields[0].height
        self.breaks = [((self.left, dy), (self.right, dy)) for dy in \
                       [BF + self.field_h / 2 + (ix + j) * (BF + self.field_h) for ix, j in enumerate(break_before)]]
        self.focus = self.fields[0]
        self.feedback = HELP_TEXT.copy()
        self.msg_area = pg.Rect(self.fields[-1].bottomleft, self.bottomright)
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
        [pg.draw.line(self.win, 'red', p0, p1) for p0, p1 in self.breaks]
        self.report()
    def update_fields(self) -> None:
        [self.win.fill(COLORS[5] if r==self.focus else COLORS[4], r) for r in self.fields]
        self.win.blits([(FONT.render(r.text, 1, COLORS[3]), r) for r in self.fields])
        self.report()
    def report(self, line:str='') -> None:
        if line: self.feedback = [line, self.feedback[1]]
        self.win.fill('black', self.msg_area)
        self.win.blits([(FONT_SMALL.render(line, 1, 'green', 'black'), (BF, self.bottom - (i + 1) * (BF + self.field_h))) \
                        for i, line in enumerate(reversed(self.feedback))])
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
