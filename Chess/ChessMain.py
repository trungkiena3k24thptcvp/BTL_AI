import pygame as p
import ChessEngine

WIDTH = HEIGHT = 480
DIMENSION = 8
SQSIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQSIZE, SQSIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    loadImages()
    validMoves = gs.getAllValidMoves()
    moveMade = False
    running = True
    sqSelected = ()
    playerClicks = []
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQSIZE
                row = location[1] // SQSIZE
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            print("Is Enpassant Move:", validMoves[i].isEnpassantMove)
                            if move.isPromotion:
                                promotedPiece = drawPromotionMenu(screen, move.pieceMoved[0])
                                validMoves[i].promotionChoice = promotedPiece
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            sqSelected = ()
                            playerClicks = []
                            break
                    if not moveMade:
                        playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = True
        if moveMade:
            validMoves = gs.getAllValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    light_color = p.Color("#f0d9b5")
    dark_color = p.Color("#b58863")
    colors = [light_color, dark_color]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQSIZE, r * SQSIZE, SQSIZE, SQSIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQSIZE, r * SQSIZE, SQSIZE, SQSIZE))


def drawPromotionMenu(screen, color):
    width = SQSIZE * 4
    height = SQSIZE
    x = (WIDTH - width) // 2
    y = (HEIGHT - height) // 2
    menu_rect = p.Rect(x, y, width, height)

    pieces = ['Q', 'R', 'B', 'N']
    selected = None
    while selected is None:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                quit()
            elif e.type == p.MOUSEBUTTONDOWN:
                mx, my = p.mouse.get_pos()
                if menu_rect.collidepoint(mx, my):
                    index = (mx - x) // SQSIZE
                    if 0 <= index < 4:
                        selected = pieces[index]
        # Vẽ menu
        p.draw.rect(screen, p.Color("gray"), menu_rect)
        for i, piece in enumerate(pieces):
            img = IMAGES[color + piece]
            rect = p.Rect(x + i * SQSIZE, y, SQSIZE, SQSIZE)
            screen.blit(p.transform.scale(img, (SQSIZE, SQSIZE)), rect)
        p.display.update()
    return selected  # trả về tên quân chọn để phong


if __name__ == "__main__":
    main()