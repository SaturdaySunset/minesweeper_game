import random, pygame, sys
from pygame.locals import *

FPS = 60
WINDOWWIDTH = 800
WINDOWHEIGHT = 900
BOXSIZE = 30
GAPSIZE = 5
FIELDWIDTH = 20
FIELDHEIGHT = 20
XMARGIN = int((WINDOWWIDTH-(FIELDWIDTH*(BOXSIZE+GAPSIZE)))/2)
YMARGIN = XMARGIN
MINESTOTAL = 60

assert MINESTOTAL < FIELDHEIGHT*FIELDWIDTH
assert BOXSIZE^2 * (FIELDHEIGHT*FIELDWIDTH) < WINDOWHEIGHT*WINDOWWIDTH
assert BOXSIZE/2 > 5

LIGHTGRAY = (225, 225, 225)
DARKGRAY = (160, 160, 160)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)

BGCOLOR = WHITE
FIELDCOLOR = BLACK
BOXCOLOR_COV = DARKGRAY
BOXCOLOR_REV = LIGHTGRAY
MINECOLOR = BLACK
TEXTCOLOR_1 = BLUE
TEXTCOLOR_2 = RED
TEXTCOLOR_3 = BLACK
HILITECOLOR = GREEN
RESETBGCOLOR = LIGHTGRAY
MINEMARK_COV = RED

FONTTYPE = 'Courier New'
FONTSIZE = 20

def main():

    global FPSCLOCK, DISPLAYSURFACE, BASICFONT, RESET_SURF, RESET_RECT, SHOW_SURF, SHOW_RECT
    pygame.init()
    pygame.display.set_caption('Minesweeper')
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURFACE = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.SysFont(FONTTYPE, FONTSIZE)

    RESET_SURF, RESET_RECT = drawButton('RESET', TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH/2, WINDOWHEIGHT-120)
    SHOW_SURF, SHOW_RECT = drawButton('SHOW ALL', TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH/2, WINDOWHEIGHT-95)

    mouse_x = 0
    mouse_y = 0

    mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()

    DISPLAYSURFACE.fill(BGCOLOR)

    while True:

        checkForKeyPress()

        mouseClicked = False
        spacePressed = False

        DISPLAYSURFACE.fill(BGCOLOR)
        pygame.draw.rect(DISPLAYSURFACE, FIELDCOLOR, (XMARGIN-5, YMARGIN-5, (BOXSIZE+GAPSIZE)*FIELDWIDTH+5, (BOXSIZE+GAPSIZE)*FIELDHEIGHT+5))
        drawField()
        drawMinesNumbers(mineField)        

        for event in pygame.event.get(): 
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                terminate()
            elif event.type == MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                mouseClicked = True
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    spacePressed = True
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    spacePressed = False

        drawCovers(revealedBoxes, markedMines)

        tipFont = pygame.font.SysFont(FONTTYPE, 16)
        drawText('Tip: Press "Space"', tipFont, TEXTCOLOR_3, DISPLAYSURFACE, WINDOWWIDTH/2, WINDOWHEIGHT-60)
        drawText('to mark the field with bomb.', tipFont, TEXTCOLOR_3, DISPLAYSURFACE, WINDOWWIDTH/2, WINDOWHEIGHT-40)

        box_x, box_y = getBoxAtPixel(mouse_x, mouse_y)

        if (box_x, box_y) == (None, None):

            if RESET_RECT.collidepoint(mouse_x, mouse_y):
                highlightButton(RESET_RECT)
                if mouseClicked: 
                    mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()

            if SHOW_RECT.collidepoint(mouse_x, mouse_y):
                highlightButton(SHOW_RECT)
                if mouseClicked:
                    revealedBoxes = blankRevealedBoxData(True)

        else:

            if not revealedBoxes[box_x][box_y]: 
                highlightBox(box_x, box_y)

                if spacePressed:
                    markedMines.append([box_x, box_y])

                if mouseClicked:
                    revealedBoxes[box_x][box_y] = True

                    if mineField[box_x][box_y] == '[0]':
                        showNumbers(revealedBoxes, mineField, box_x, box_y, zeroListXY)

                    if mineField[box_x][box_y] == '[X]':
                        showMines(revealedBoxes, mineField, box_x, box_y)
                        gameOverAnimation(mineField, revealedBoxes, markedMines, 'LOSS')
                        mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()

        if gameWon(revealedBoxes, mineField):
            gameOverAnimation(mineField, revealedBoxes, markedMines, 'WIN')
            mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def blankField():
    field = []
    for x in range(FIELDWIDTH):
        field.append([]) 
        for y in range(FIELDHEIGHT):
            field[x].append('[ ]')
    return field

def placeMines(field):
    mineCount = 0
    xy = [] 
    while mineCount < MINESTOTAL: 
        x = random.randint(0,FIELDWIDTH-1)
        y = random.randint(0,FIELDHEIGHT-1)
        xy.append([x,y]) 
        if xy.count([x,y]) > 1: 
            xy.remove([x,y]) 
        else: 
            field[x][y] = '[X]' 
            mineCount += 1

def isThereMine(field, x, y):
    return field[x][y] == '[X]'  

def placeNumbers(field):
    for x in range(FIELDWIDTH):
        for y in range(FIELDHEIGHT):
            if not isThereMine(field, x, y):
                count = 0
                if x != 0: 
                    if isThereMine(field, x-1, y):
                        count += 1
                    if y != 0: 
                        if isThereMine(field, x-1, y-1):
                            count += 1
                    if y != FIELDHEIGHT-1: 
                        if isThereMine(field, x-1, y+1):
                            count += 1
                if x != FIELDWIDTH-1: 
                    if isThereMine(field, x+1, y):
                        count += 1
                    if y != 0: 
                        if isThereMine(field, x+1, y-1):
                            count += 1
                    if y != FIELDHEIGHT-1: 
                        if isThereMine(field, x+1, y+1):
                            count += 1
                if y != 0: 
                    if isThereMine(field, x, y-1):
                        count += 1
                if y != FIELDHEIGHT-1: 
                    if isThereMine(field, x, y+1):
                        count += 1
                field[x][y] = '[%s]' %(count)

def blankRevealedBoxData(val):
    revealedBoxes = []
    for i in range(FIELDWIDTH):
        revealedBoxes.append([val] * FIELDHEIGHT)
    return revealedBoxes

def gameSetup():
    mineField = blankField()
    placeMines(mineField)
    placeNumbers(mineField)
    zeroListXY = []
    markedMines = []
    revealedBoxes = blankRevealedBoxData(False)

    return mineField, zeroListXY, revealedBoxes, markedMines

def drawField():
    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            pygame.draw.rect(DISPLAYSURFACE, BOXCOLOR_REV, (left, top, BOXSIZE, BOXSIZE))

    DISPLAYSURFACE.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURFACE.blit(SHOW_SURF, SHOW_RECT)

def drawMinesNumbers(field):
    half = int(BOXSIZE*0.5) 
    quarter = int(BOXSIZE*0.25)
    eighth = int(BOXSIZE*0.125)
    
    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            center_x, center_y = getCenterXY(box_x, box_y)
            if field[box_x][box_y] == '[X]':
                pygame.draw.circle(DISPLAYSURFACE, MINECOLOR, (left+half, top+half), quarter)
                pygame.draw.circle(DISPLAYSURFACE, WHITE, (left+half, top+half), eighth)
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+eighth, top+half), (left+half+quarter+eighth, top+half))
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+half, top+eighth), (left+half, top+half+quarter+eighth))
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+quarter, top+quarter), (left+half+quarter, top+half+quarter))
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+quarter, top+half+quarter), (left+half+quarter, top+quarter))
            else: 
                for i in range(1,9):
                    if field[box_x][box_y] == '[' + str(i) + ']':
                        if i in range(1,3):
                            textColor = TEXTCOLOR_1
                        else:
                            textColor = TEXTCOLOR_2
                        drawText(str(i), BASICFONT, textColor, DISPLAYSURFACE, center_x, center_y)

def showNumbers(revealedBoxes, mineField, box_x, box_y, zeroListXY):
    revealedBoxes[box_x][box_y] = True
    revealBoxes(revealedBoxes, box_x, box_y)
    for i,j in getAdjacentBoxesXY(mineField, box_x, box_y):
        if mineField[i][j] == '[0]' and [i,j] not in zeroListXY:
            zeroListXY.append([i,j])
            showNumbers(revealedBoxes, mineField, i, j, zeroListXY)

def showMines(revealedBoxes, mineField, box_x, box_y):
    for i in range(FIELDWIDTH):
        for j in range(FIELDHEIGHT):
            if mineField[i][j] == '[X]':
                revealedBoxes[i][j] = True
    
def revealBoxes(revealedBoxes, box_x, box_y):
    if box_x != 0: 
        revealedBoxes[box_x-1][box_y] = True
        if box_y != 0: 
            revealedBoxes[box_x-1][box_y-1] = True
        if box_y != FIELDHEIGHT-1: 
            revealedBoxes[box_x-1][box_y+1] = True
    if box_x != FIELDWIDTH-1:
        revealedBoxes[box_x+1][box_y] = True
        if box_y != 0: 
            revealedBoxes[box_x+1][box_y-1] = True
        if box_y != FIELDHEIGHT-1: 
            revealedBoxes[box_x+1][box_y+1] = True
    if box_y != 0: 
        revealedBoxes[box_x][box_y-1] = True
    if box_y != FIELDHEIGHT-1: 
        revealedBoxes[box_x][box_y+1] = True

def getAdjacentBoxesXY(mineField, box_x, box_y):
    adjacentBoxesXY = []

    if box_x != 0:
        adjacentBoxesXY.append([box_x-1,box_y])
        if box_y != 0:
            adjacentBoxesXY.append([box_x-1,box_y-1])
        if box_y != FIELDHEIGHT-1:
            adjacentBoxesXY.append([box_x-1,box_y+1])
    if box_x != FIELDWIDTH-1: 
        adjacentBoxesXY.append([box_x+1,box_y])
        if box_y != 0:
            adjacentBoxesXY.append([box_x+1,box_y-1])
        if box_y != FIELDHEIGHT-1:
            adjacentBoxesXY.append([box_x+1,box_y+1])
    if box_y != 0:
        adjacentBoxesXY.append([box_x,box_y-1])
    if box_y != FIELDHEIGHT-1:
        adjacentBoxesXY.append([box_x,box_y+1])

    return adjacentBoxesXY
    
def drawCovers(revealedBoxes, markedMines):
    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            if not revealedBoxes[box_x][box_y]:
                left, top = getLeftTopXY(box_x, box_y)
                if [box_x, box_y] in markedMines:
                    pygame.draw.rect(DISPLAYSURFACE, MINEMARK_COV, (left, top, BOXSIZE, BOXSIZE))
                else:
                    pygame.draw.rect(DISPLAYSURFACE, BOXCOLOR_COV, (left, top, BOXSIZE, BOXSIZE))

def drawText(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.centerx = x
    textrect.centery = y
    surface.blit(textobj, textrect)

def drawButton(text, color, bgcolor, center_x, center_y):
    butSurf = BASICFONT.render(text, True, color, bgcolor)
    butRect = butSurf.get_rect()
    butRect.centerx = center_x
    butRect.centery = center_y
    return (butSurf, butRect)

def getLeftTopXY(box_x, box_y):
    left = XMARGIN + box_x*(BOXSIZE+GAPSIZE)
    top = YMARGIN + box_y*(BOXSIZE+GAPSIZE)
    return left, top

def getCenterXY(box_x, box_y):
    center_x = XMARGIN + BOXSIZE/2 + box_x*(BOXSIZE+GAPSIZE)
    center_y = YMARGIN + BOXSIZE/2 + box_y*(BOXSIZE+GAPSIZE)
    return center_x, center_y

def getBoxAtPixel(x, y):
    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (box_x, box_y)
    return (None, None)

def highlightBox(box_x, box_y):
    left, top = getLeftTopXY(box_x, box_y)
    pygame.draw.rect(DISPLAYSURFACE, HILITECOLOR, (left, top, BOXSIZE, BOXSIZE), 4)

def highlightButton(butRect):
    linewidth = 4
    pygame.draw.rect(DISPLAYSURFACE, HILITECOLOR, (butRect.left-linewidth, butRect.top-linewidth, butRect.width+2*linewidth, butRect.height+2*linewidth), linewidth)

def gameWon(revealedBoxes, mineField):
    notMineCount = 0

    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            if revealedBoxes[box_x][box_y] == True:
                if mineField[box_x][box_y] != '[X]':
                    notMineCount += 1

    if notMineCount >= (FIELDWIDTH*FIELDHEIGHT)-MINESTOTAL:
        return True
    else:
        return False

def gameOverAnimation(mineField, revealedBoxes, markedMines, result):
    origSurf = DISPLAYSURFACE.copy()
    flashSurf = pygame.Surface(DISPLAYSURFACE.get_size())
    flashSurf = flashSurf.convert_alpha()
    animationSpeed = 20

    if result == 'WIN':
        r, g, b = BLUE
    else:
        r, g, b = RED

    for i in range(5):
        for start, end, step in ((0, 255, 1), (255, 0, -1)):
            for alpha in range(start, end, animationSpeed*step):
                checkForKeyPress()
                flashSurf.fill((r, g, b, alpha))
                DISPLAYSURFACE.blit(origSurf, (0, 0))
                DISPLAYSURFACE.blit(flashSurf, (0, 0))
                pygame.draw.rect(DISPLAYSURFACE, FIELDCOLOR, (XMARGIN-5, YMARGIN-5, (BOXSIZE+GAPSIZE)*FIELDWIDTH+5, (BOXSIZE+GAPSIZE)*FIELDHEIGHT+5))
                drawField()
                drawMinesNumbers(mineField)
                tipFont = pygame.font.SysFont(FONTTYPE, 16)
                drawText('Tip: Press "Space"', tipFont, TEXTCOLOR_3, DISPLAYSURFACE, WINDOWWIDTH/2, WINDOWHEIGHT-60)
                drawText('to mark the field with bomb.', tipFont, TEXTCOLOR_3, DISPLAYSURFACE, WINDOWWIDTH/2, WINDOWHEIGHT-40)
                RESET_SURF, RESET_RECT = drawButton('RESET', TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH/2, WINDOWHEIGHT-120)
                SHOW_SURF, SHOW_RECT = drawButton('SHOW ALL', TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH/2, WINDOWHEIGHT-95)
                drawCovers(revealedBoxes, markedMines)
                pygame.display.update()
                FPSCLOCK.tick(FPS)
  
def terminate():
    pygame.quit()
    sys.exit()

def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()
        
    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

if __name__ == '__main__':
    main()
