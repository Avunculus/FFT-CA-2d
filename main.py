from constants import *
from tools import * 
from gui import *
from string import digits

def convolve2d(arr0:np.ndarray, arr1:np.ndarray) -> np.ndarray:
    func1 = np.fft.fft2(arr0)
    func2 = np.fft.fft2(np.flipud(np.fliplr(arr1)))
    m, n = func1.shape
    convolved = np.real(np.fft.ifft2(func1 * func2))
    convolved = np.roll(convolved, (- int(m / 2) + 1, - int(n / 2) + 1), axis=(0, 1))
    return convolved

def fft_flip(cells:np.ndarray, kernel:np.ndarray, rule:np.ndarray) -> np.ndarray:
    ngb_sum = convolve2d(cells, kernel).round()
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
    if bg_image: # top layer to cover dbld
        sfc.blit(bg_image, (0, 0))

def get_user_args():
    # page 1: Game; page 2: View
    ## declare page sfc, populate / draw
    menu = (
        Menu(TextField('game code', digits + 'XxQqVvMm,-GgNnBbSs', 'Gx,Nv1,B3,S2,3', 64),
             ChoiceField('grid', ['hexagon', 'square']),
             ChoiceField('neighborhood', ['VonNeuman', 'Moore']),
             TextField('neighbor range', digits, '1', 1),
             TextField('birth', digits + ',-', '3', 64),
             TextField('survival', digits + ',-', '2,3', 64)),
        Menu(ChoiceField('orientation', ['flat-top', 'pointy-top']),
             TextField('scale view', digits, '1', 2))
        )
    # view scale (int) scales both xy for basis (4,4) [sq], (5,3) [hex-ft], (3,5) [hex-pt]
    page = 0
    win = pg.display.set_mode(menu[page].size)
    menu[page].win = win
    menu[page].draw_all()
    clock = pg.time.Clock()
    running = True
    while running :
        clock.tick(FPS)
        for event in pg.event.get():
            match event.type:
                case pg.TEXTINPUT:
                    menu[page].add_char(event.text)
                case pg.MOUSEBUTTONDOWN:
                    menu[page].click(event.pos)
                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_TAB:
                            menu[page].cycle_fields(-1) if event.mod & pg.KMOD_SHIFT \
                            else menu[page].cycle_fields(1) 
                        case pg.K_UP:
                            menu[page].cycle_fields(-1) 
                        case pg.K_DOWN:
                            menu[page].cycle_fields(1)
                        case pg.K_LEFT | pg.K_RIGHT:
                            menu[page].cycle_choice(event.key % 2)
                        case pg.K_ESCAPE:
                            menu[page].reset_field()
                        case pg.K_DELETE | pg.K_BACKSPACE:
                            menu[page].clear_field()
                        case pg.K_q:
                            if event.mod & pg.KMOD_CTRL:
                                return False
                        case pg.K_RETURN | pg.K_KP_ENTER:
                            if page == 0:
                                if menu[page].fields.index(menu[page].focus) == 0: # full code
                                    result = decode_game_string(menu[page].fields[0].text)
                                else: # part-wise
                                    result = decode_game_string(parts_to_code([r.text for r in menu[page].fields[1:]])) 
                                if isinstance(result, tuple): # accept game args
                                    kernel, rule = result
                                    doubled = kernel.shape[0] != kernel.shape[1] 
                                    page = 1
                                    win = pg.display.set_mode(menu[page].size)
                                    menu[page].win = win
                                    menu[page].draw_all()
                            else: # xc view args: need appoved grid, scale_x and scale_y
                                scale = (5, 3) if doubled else (4, 4)
                                if menu[page].fields[0].text == 'pointy-top': scale = (3, 5)
                                factor = int(menu[page].fields[1].text)
                                scale = (factor * scale[0], factor * scale[1])
                                cols = MAX_W // scale[0]
                                cols -= cols % 2
                                rows = MAX_H // scale[1]
                                rows -= rows % 2
                                if cols >= 6 and rows >= 6:
                                    grid = np.random.random((cols, rows)).round()
                                    pg.display.quit()
                                    return (grid, kernel, rule, scale[0], scale[1])
        pg.display.update()


def main(args:tuple[np.ndarray, np.ndarray, np.ndarray, int, int]):

    grid, kernel, rule, scale_x, scale_y = args

    # adjust kernel so k.shape = g.shape!
    # OLD: ngbs = get_ngb_mask(shape, doubled) # set ngbs from doubled + MASK + shape

    doubled = kernel.shape[0] != kernel.shape[1] 

    rez = (grid.shape[0] * scale_x, grid.shape[1] * scale_y)
    # grid = np.random.random(shape).round()
    bg_img = make_bg(grid.shape, (scale_x, scale_y)) if doubled else None
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
                        case pg.K_n: # new game
                            if event.mod & pg.KMOD_CTRL:
                                pg.display.quit()
                                return True
                        case pg.K_r: # re-set, randomize
                            if event.mod & pg.KMOD_CTRL: 
                                autoflip = False
                                grid = np.random.random(grid.shape).round()
                                show(win, grid.astype(np.int64), bg_img)
                        case pg.K_SPACE:
                            autoflip = not autoflip
                        case pg.K_RIGHT:
                            grid = fft_flip(grid, kernel, rule)
                            show(win, grid.astype(np.int64), bg_img)
        if autoflip: # advance 1 gen 
            grid = fft_flip(grid, kernel, rule) 
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
