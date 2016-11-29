import random, sys, pygame
from pygame.locals import *

"""
Set variaveis globais
"""

BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
GREEN   = (  0, 204,   0)
GRAY    = ( 60,  60,  60)
BLUE    = (  0,  50, 255)
RED  = (255,   0,   0)
DARKGRAY =( 40,  40,  40)

windowWidth = 800
windowHeight = 600
displayWidth = 200
tamanhoTile = 40
tamanhoMarcador = 40
buttonHeight = 20
buttonWidht = 40
textoHeight = 25
texoPosit = 10
tabuleiroWidth = 10
tabuleiroHeight = 10
revelarSpeed = 10
explodirSpeed = 10

BGCOLOR = GRAY
BUTTONCOLOR = GREEN
TEXTCOLOR = WHITE
TILECOLOR = WHITE
BORDERCOLOR = GRAY
TEXTSHADOWCOLOR = BLUE
SHIPCOLOR = RED
HIGHLIGHTCOLOR = BLUE

margemX = int((windowWidth - (tabuleiroWidth * tamanhoTile) - displayWidth - tamanhoMarcador) / 2)
margemY = int((windowHeight - (tabuleiroHeight * tamanhoTile) - tamanhoMarcador) / 2)

def main():
    global DISPLAYSURF, FPS, Font, FontBig, HELP_SURF, HELP_RECT, NEW_SURF, \
           NEW_RECT, SHOTS_SURF, SHOTS_RECT, COUNTER_SURF, \
           COUNTER_RECT, HBUTTON_SURF, EXPLOSION_IMAGES
    pygame.init()
    FPS = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((windowWidth, windowHeight))
    Font = pygame.font.SysFont("arial", 30)
    FontBig = pygame.font.SysFont("arial", 60)
    
    # create buttons
    HELP_SURF = Font.render("SOBRE", True, WHITE)
    HELP_RECT = HELP_SURF.get_rect()
    HELP_RECT.topleft = (windowWidth - 180, windowHeight - 350)
    NEW_SURF = Font.render("NOVO JOGO", True, WHITE)
    NEW_RECT = NEW_SURF.get_rect()
    NEW_RECT.topleft = (windowWidth - 200, windowHeight - 200)

    SHOTS_SURF = Font.render("Disparos: ", True, WHITE)
    SHOTS_RECT = SHOTS_SURF.get_rect()
    SHOTS_RECT.topleft = (windowWidth - 790, windowHeight - 570)
    
    # imagens da animacao de explosao
    EXPLOSION_IMAGES = [
        pygame.image.load("img/explodir1.png"), pygame.image.load("img/explodir2.png"), pygame.image.load("img/explodir3.png")]
    
    pygame.display.set_caption('BATALHA NAVAL - LP1')

    while True:
        shots_taken = run_game()
        show_gameover_screen(shots_taken)
        
        
def run_game():
    revealed_tiles = generate_default_tiles(False) 
    main_board = generate_default_tiles(None)
    ship_objs = ['battleship','cruiser1','cruiser2','destroyer1','destroyer2',
                 'destroyer3','submarine1','submarine2','submarine3','submarine4']
    main_board = add_ships_to_board(main_board, ship_objs)
    mousex, mousey = 0, 0
    counter = [] # contador de disparos
    xmarkers, ymarkers = set_markers(main_board)
        
    while True:
        COUNTER_SURF = Font.render(str(len(counter)), True, WHITE)
        COUNTER_RECT = SHOTS_SURF.get_rect()
        COUNTER_RECT.topleft = (windowWidth - 680, windowHeight - 570)
        
        DISPLAYSURF.fill(BGCOLOR)
        DISPLAYSURF.blit(HELP_SURF, HELP_RECT)
        DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
        DISPLAYSURF.blit(SHOTS_SURF, SHOTS_RECT)
        DISPLAYSURF.blit(COUNTER_SURF, COUNTER_RECT)
        
        draw_board(main_board, revealed_tiles)
        draw_markers(xmarkers, ymarkers)
        mouse_clicked = False     

        check_for_quit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if HELP_RECT.collidepoint(event.pos):
                    DISPLAYSURF.fill(BGCOLOR)
                    show_help_screen()
                elif NEW_RECT.collidepoint(event.pos):
                    main()
                else:
                    mousex, mousey = event.pos
                    mouse_clicked = True
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
                    
        tilex, tiley = get_tile_at_pixel(mousex, mousey)
        if tilex != None and tiley != None:
            if not revealed_tiles[tilex][tiley]:
                draw_highlight_tile(tilex, tiley)
            if not revealed_tiles[tilex][tiley] and mouse_clicked:
                reveal_tile_animation(main_board, [(tilex, tiley)])
                revealed_tiles[tilex][tiley] = True
                if check_revealed_tile(main_board, [(tilex, tiley)]):
                    left, top = left_top_coords_tile(tilex, tiley)
                    aimaExplosao((left, top))
                    if check_for_win(main_board, revealed_tiles):
                        counter.append((tilex, tiley))
                        return len(counter)
                counter.append((tilex, tiley))
                
        pygame.display.update()
        FPS.tick(30)


def generate_default_tiles(default_value):
    '''
    returns list of 10 x 10 tiles with tuples ('shipName',boolShot) set to 
    (default_value)
    '''
    default_tiles = [[default_value]*tabuleiroHeight for i in xrange(tabuleiroWidth)]
    
    return default_tiles

    
def aimaExplosao(coord):
    for image in EXPLOSION_IMAGES:
        image = pygame.transform.scale(image, (tamanhoTile+10, tamanhoTile+10))
        DISPLAYSURF.blit(image, coord)
        pygame.display.flip()
        FPS.tick(explodirSpeed)


def check_revealed_tile(board, tile):
    # retorna TRUES se parte de uma embarcacao existir na Tile
    return board[tile[0][0]][tile[0][1]] != None


def reveal_tile_animation(board, tile_to_reveal):
    for coverage in xrange(tamanhoTile, (-revelarSpeed) - 1, -revelarSpeed):
        draw_tile_covers(board, tile_to_reveal, coverage)

        
def draw_tile_covers(board, tile, coverage):
    left, top = left_top_coords_tile(tile[0][0], tile[0][1])
    if check_revealed_tile(board, tile):
        pygame.draw.rect(DISPLAYSURF, SHIPCOLOR, (left, top, tamanhoTile,
                                                  tamanhoTile))
    else:
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, tamanhoTile,
                                                tamanhoTile))
    if coverage > 0:
        pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left, top, coverage,
                                                  tamanhoTile))
            
    pygame.display.update()
    FPS.tick(30)    


def check_for_quit():
    for event in pygame.event.get(QUIT):
        pygame.quit()
        sys.exit()


def check_for_win(board, revealed):
    # retorna True se revelar todas as embarcacoes
    for tilex in xrange(tabuleiroWidth):
        for tiley in xrange(tabuleiroHeight):
            if board[tilex][tiley] != None and not revealed[tilex][tiley]:
                return False
    return True


def draw_board(board, revealed):
    for tilex in xrange(tabuleiroWidth):
        for tiley in xrange(tabuleiroHeight):
            left, top = left_top_coords_tile(tilex, tiley)
            if not revealed[tilex][tiley]:
                pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left, top, tamanhoTile,
                                                          tamanhoTile))
            else:
                if board[tilex][tiley] != None:
                    pygame.draw.rect(DISPLAYSURF, SHIPCOLOR, (left, top, 
                                     tamanhoTile, tamanhoTile))
                else:
                    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, 
                                     tamanhoTile, tamanhoTile))
                
    for x in xrange(0, (tabuleiroWidth + 1) * tamanhoTile, tamanhoTile):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x + margemX + tamanhoMarcador,
            margemY + tamanhoMarcador), (x + margemX + tamanhoMarcador, 
            windowHeight - margemY))
    for y in xrange(0, (tabuleiroHeight + 1) * tamanhoTile, tamanhoTile):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (margemX + tamanhoMarcador, y + 
            margemY + tamanhoMarcador), (windowWidth - (displayWidth + tamanhoMarcador *
            2), y + margemY + tamanhoMarcador))





def set_markers(board):
    xmarkers = [0 for i in xrange(tabuleiroWidth)]
    ymarkers = [0 for i in xrange(tabuleiroHeight)]
    for tilex in xrange(tabuleiroWidth):
        for tiley in xrange(tabuleiroHeight):
            if board[tilex][tiley] != None:
                xmarkers[tilex] += 1
                ymarkers[tiley] += 1

    return xmarkers, ymarkers


def draw_markers(xlist, ylist):
    for i in xrange(len(xlist)):
        left = i * tamanhoMarcador + margemX + tamanhoMarcador + (tamanhoTile / 3)
        top = margemY
        marker_surf, marker_rect = make_text_objs(str(xlist[i]),
                                                    Font, TEXTCOLOR)
        marker_rect.topleft = (left, top)
        DISPLAYSURF.blit(marker_surf, marker_rect)
    for i in range(len(ylist)):
        left = margemX
        top = i * tamanhoMarcador + margemY + tamanhoMarcador + (tamanhoTile / 3)
        marker_surf, marker_rect = make_text_objs(str(ylist[i]), 
                                                    Font, TEXTCOLOR)
        marker_rect.topleft = (left, top)
        DISPLAYSURF.blit(marker_surf, marker_rect)



def add_ships_to_board(board, ships):
    new_board = board[:]
    ship_length = 0
    for ship in ships:
        valid_ship_position = False
        while not valid_ship_position:
            xStartpos = random.randint(0, 9)
            yStartpos = random.randint(0, 9)
            isHorizontal = random.randint(0, 1)
            if 'battleship' in ship:
                ship_length = 4
            elif 'cruiser' in ship:
                ship_length = 3
            elif 'destroyer'in ship:
                ship_length = 2
            elif 'submarine' in ship:
                ship_length = 1

            valid_ship_position, ship_coords = make_ship_position(new_board,
                xStartpos, yStartpos, isHorizontal, ship_length, ship)
            if valid_ship_position:
                for coord in ship_coords:
                    new_board[coord[0]][coord[1]] = ship
    return new_board


def make_ship_position(board, xPos, yPos, isHorizontal, length, ship):
    ship_coordinates = []
    if isHorizontal:
        for i in xrange(length):
            if (i+xPos > 9) or (board[i+xPos][yPos] != None) or \
                hasAdjacent(board, i+xPos, yPos, ship):
                return (False, ship_coordinates)
            else:
                ship_coordinates.append((i+xPos, yPos))
    else:
        for i in xrange(length):
            if (i+yPos > 9) or (board[xPos][i+yPos] != None) or \
                hasAdjacent(board, xPos, i+yPos, ship):
                return (False, ship_coordinates)        
            else:
                ship_coordinates.append((xPos, i+yPos))
    return (True, ship_coordinates)


def hasAdjacent(board, xPos, yPos, ship):
    for x in xrange(xPos-1,xPos+2):
        for y in xrange(yPos-1,yPos+2):
            if (x in range (10)) and (y in range (10)) and \
                (board[x][y] not in (ship, None)):
                return True
    return False
    
    
def left_top_coords_tile(tilex, tiley):
    left = tilex * tamanhoTile + margemX + tamanhoMarcador
    top = tiley * tamanhoTile + margemY + tamanhoMarcador
    return (left, top)
    
    
def get_tile_at_pixel(x, y):
    for tilex in xrange(tabuleiroWidth):
        for tiley in xrange(tabuleiroHeight):
            left, top = left_top_coords_tile(tilex, tiley)
            tile_rect = pygame.Rect(left, top, tamanhoTile, tamanhoTile)
            if tile_rect.collidepoint(x, y):
                return (tilex, tiley)
    return (None, None)
    
    
def draw_highlight_tile(tilex, tiley):
    left, top = left_top_coords_tile(tilex, tiley)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR,
                    (left, top, tamanhoTile, tamanhoTile), 4)


def show_help_screen():
    line1_surf, line1_rect = make_text_objs('PRESSIONE QUALQUER TECLA PARA VOLTAR', 
                                            Font, TEXTCOLOR)
    line1_rect.topleft = (texoPosit, textoHeight)
    DISPLAYSURF.blit(line1_surf, line1_rect)
    
    line2_surf, line2_rect = make_text_objs(
        'bem vindo a Batalha Naval! ' \
        'O objetivo do jogo e afundar', Font, TEXTCOLOR)
    line2_rect.topleft = (texoPosit, textoHeight * 3)
    DISPLAYSURF.blit(line2_surf, line2_rect)

    line3_surf, line3_rect = make_text_objs('todas as embarcacoes no tabuleiro com a', Font, TEXTCOLOR)
    line3_rect.topleft = (texoPosit, textoHeight * 4)
    DISPLAYSURF.blit(line3_surf, line3_rect)

    line4_surf, line4_rect = make_text_objs('menor quantidade de disparos possiveis.', Font, TEXTCOLOR)
    line4_rect.topleft = (texoPosit, textoHeight * 5)
    DISPLAYSURF.blit(line4_surf, line4_rect)

    line5_surf, line5_rect = make_text_objs('Para reiniciar o jogo clique em "Novo Jogo". ' \
        'Boa sorte!', Font, TEXTCOLOR)
    line5_rect.topleft = (texoPosit, textoHeight * 6)
    DISPLAYSURF.blit(line5_surf, line5_rect)

    
    while check_for_keypress() == None:
        pygame.display.update()
        FPS.tick()

    
def make_text_objs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def check_for_keypress():

    for event in pygame.event.get([KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION]):
        if event.type in (KEYDOWN, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEMOTION):
            continue
        return event.key
    return None


def show_gameover_screen(shots_fired):
    '''
    Mensagens de endgame
    '''
    DISPLAYSURF.fill(BGCOLOR)
    titleSurf, titleRect = make_text_objs('Parabens! Voce venceu em:',
                                            FontBig, TEXTSHADOWCOLOR)
    titleRect.center = (int(windowWidth / 2), int(windowHeight / 2))
    DISPLAYSURF.blit(titleSurf, titleRect)
    
    titleSurf, titleRect = make_text_objs('Parabens! Voce venceu em:', 
                                            FontBig, TEXTCOLOR)
    titleRect.center = (int(windowWidth / 2) - 3, int(windowHeight / 2) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)
    
    titleSurf, titleRect = make_text_objs(str(shots_fired) + ' disparos', 
                                            FontBig, TEXTSHADOWCOLOR)
    titleRect.center = (int(windowWidth / 2), int(windowHeight / 2 + 50))
    DISPLAYSURF.blit(titleSurf, titleRect)
    
    titleSurf, titleRect = make_text_objs(str(shots_fired) + ' disparos', 
                                            FontBig, TEXTCOLOR)
    titleRect.center = (int(windowWidth / 2) - 3, int(windowHeight / 2 + 50) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    pressKeySurf, pressKeyRect = make_text_objs(
        'Pressione qualquer tecla para tentar novamente.', Font, TEXTCOLOR)
    pressKeyRect.center = (int(windowWidth / 2), int(windowHeight / 2) + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)
    
    while check_for_keypress() == None:
        pygame.display.update()
        FPS.tick()    
        
    
if __name__ == "__main__": #Loop do jogo
    main()
