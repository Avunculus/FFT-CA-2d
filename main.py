from constants import *

def convolve2d(arr0:np.ndarray, arr1:np.ndarray) -> np.ndarray:
    func1 = np.fft.fft2(arr0)
    func2 = np.fft.fft2(np.flipud(np.fliplr(arr1)))
    m, n = func1.shape
    convolved = np.real(np.fft.ifft2(func1 * func2))
    convolved = np.roll(convolved, (- int(m / 2) + 1, - int(n / 2) + 1), axis=(0, 1))
    return convolved

def fft_flip(cells:np.ndarray, ngb_mask:np.ndarray, rule:np.ndarray) -> np.ndarray:
    ngb_sum = convolve2d(cells, ngb_mask).round()
    new_cells = np.zeros(ngb_sum.shape)
    for i in np.nonzero(rule[0, :]):
        for j in i:
            new_cells[np.where((ngb_sum == j) & (cells == 0))] = 1
    for i in np.nonzero(rule[1, :]):
        for j in i:
            new_cells[np.where((ngb_sum == j) & (cells == 1))] = 1
    # new_cells[np.where((ngb_sum == 2) & (cells == 1))] = 1
    # new_cells[np.where((ngb_sum == 3) & (cells == 1))] = 1
    # new_cells[np.where((ngb_sum == 3) & (cells == 0))] = 1
    return new_cells

def show(sfc:pg.Surface, cells:np.ndarray, bg_image:pg.Surface=None) -> None:
    img = pg.Surface(cells.shape)
    color = img.map_rgb(COLORS[1])
    bg_color = img.map_rgb(COLORS[0])
    pg.surfarray.blit_array(img, cells * (color - bg_color) + bg_color)
    img = pg.transform.scale(img, sfc.get_size())
    sfc.blit(img, (0, 0))
    if bg_image:
        sfc.blit(bg_image, (0, 0))

def get_user_args():
    """
    From: system (display dimensions) & user text input 
    Returns: (cols: int, rows: int, scale_x: int, scale_y: int, doubled: bool)
    """
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
    
    win  = pg.display.set_mode((960, 540), flags=pg.NOFRAME)
    font = pg.font.SysFont('couriernew', FH, bold=True)
    names    = ['cols', 'rows', 'scale_x', 'scale_y', 'doubled']
    types =    [ int     ,  int     ,  int  ,  int  ,  int    ]
    defaults = [str(1920 // 5), str(1080 // 3), '5', '3', '1']
    ui = {arg_name: ArgField((12, 12 + i * FH), defaults[i], font, arg_name, COLORS[-2 :]) for i, arg_name in enumerate(names)}
    target = 'scale_x'
    [r.draw(win, n==target) for n, r in ui.items()]
    clock = pg.time.Clock()
    running = True
    while running :
        clock.tick(FPS)
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    return False
                case pg.TEXTINPUT:
                    if event.text.isnumeric() and target:
                        ui[target].add_char(event.text)
                        [r.draw(win, n==target) for n, r in ui.items()]
                case pg.MOUSEBUTTONDOWN:
                    target = ''
                    for key in [n for n, r in ui.items() if r.collidepoint(event.pos)]:
                        target = key
                    [r.draw(win, n==target) for n, r in ui.items()]
                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_UP:
                            target = names[names.index(target) - 1]
                            [r.draw(win, n==target) for n, r in ui.items()]
                        case pg.K_DOWN:
                            target = names[(names.index(target) + 1) % len(names)]
                            [r.draw(win, n==target) for n, r in ui.items()]
                        case pg.K_ESCAPE:
                            if target:
                                ui[target].arg_val = '0'
                                [r.draw(win, n==target) for n, r in ui.items()]
                        case pg.K_BACKSPACE:
                            if target:
                                ui[target].del_char()
                                [r.draw(win, n==target) for n, r in ui.items()]
                        case pg.K_q:
                            if event.mod & pg.KMOD_CTRL:
                                return False
                        case pg.K_RETURN | pg.K_KP_ENTER:
                            cols, rows, scale_x, scale_y, doubled = [types[names.index(n)](r.arg_val) for n, r in ui.items()]
                            doubled = bool(doubled)
                            disp_w, disp_h = pg.display.get_desktop_sizes()[0]  # check fit to display max
                            if cols >= 6 and cols * scale_x <= disp_w and rows >= 6 and rows * scale_y <= disp_h: # min 6x6
                                if doubled:
                                    cols -= cols % 2 # chck even #s?
                                    rows -= rows % 2
                                pg.display.quit()
                                return (cols, rows, scale_x, scale_y, doubled)
        pg.display.update()

def main(args):
    cols, rows, scale_x, scale_y, doubled = args
    shape = (cols, rows)
    rez = (cols * scale_x, rows * scale_y)

    grid = np.random.random(shape).round()
    ngbs = get_ngb_mask(shape, doubled) # set ngbs from doubled + MASK + shape
    rule = RULE_CLASSIC # now @ constant; space for input rule_key/ui for toggle rects

    bg_img = make_bg(shape, (scale_x, scale_y)) if doubled else None
    win = pg.display.set_mode(rez, flags=pg.NOFRAME)
    show(win, grid.astype(np.int64), bg_img)
    clock = pg.time.Clock()
    autoflip = False
    running = True

    while running:
        clock.tick(FPS)
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    return False
                case pg.KEYDOWN:
                    match event.key:                
                        case pg.K_q: # quit
                            if event.mod & pg.KMOD_CTRL:
                                return False
                        case pg.K_n: # new grid
                            if event.mod & pg.KMOD_CTRL:
                                pg.display.quit()
                                return True
                        case pg.K_r: # re-set, randomize
                            if event.mod & pg.KMOD_CTRL: 
                                autoflip = False
                                grid = np.random.random(shape).round()
                                show(win, grid.astype(np.int64), bg_img)
                        case pg.K_SPACE:
                            autoflip = not autoflip
                        case pg.K_RIGHT:
                            grid = fft_flip(grid, ngbs, rule)
                            show(win, grid.astype(np.int64), bg_img)
        if autoflip: # advance 1 gen 
            grid = fft_flip(grid, ngbs, rule) 
            show(win, grid.astype(np.int64), bg_img)
        pg.display.update()

if __name__ == '__main__':
    args = get_user_args()
    repeat = main(args) if args else False
    while repeat:
        args = get_user_args()
        repeat = main(args) if args else False
    pg.quit()
    quit()
