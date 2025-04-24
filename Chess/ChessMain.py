import pygame as p
import ChessEngine
from Ch_AI import *
WIDTH = HEIGHT = 480
DIMENSION = 8
SQSIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQSIZE, SQSIZE))


import multiprocessing
from Ch_AI import findBestMove


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
    gameOver = False
    sqSelected = ()
    playerClicks = []

    # Thiết lập cho người chơi và AI: True nếu là người chơi (Human), False nếu là AI
    playerOne = True  # Human is white
    playerTwo = False  # AI is black

    while running:
        isHumanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN and not gameOver and isHumanTurn and not gs.undoMode:
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
                            print("Is Promotion:", validMoves[i].isPromotion)
                            if validMoves[i].isPromotion:
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
                if e.key == p.K_z:  # Phím undo
                    if not gs.undoMode:  # Lần đầu nhấn z
                        gs.undoMode = True
                        print("Chế độ undo - Bấm 'z' để undo tiếp, SPACE để kết thúc")

                    # Thực hiện undo dù là lần đầu hay tiếp theo
                    if len(gs.moveLog) > 0:
                        gs.undoMove()
                        sqSelected = ()
                        playerClicks = []
                        moveMade = True
                        validMoves = gs.getAllValidMoves()
                        print(f"Đã undo, còn {len(gs.moveLog)} nước đi")
                    else:
                        print("Không thể undo tiếp!")
                        gs.undoMode = False

                elif e.key == p.K_SPACE and gs.undoMode:  # Thoát chế độ undo
                    gs.undoMode = False
                    print("Kết thúc chế độ undo")
                    moveMade = True  # Đảm bảo bàn cờ được vẽ lại  # Tắt chế độ undo từ GameState

        # AI thực hiện nước đi nếu là lượt AI
        if not gameOver and not isHumanTurn and not gs.undoMode:
            return_queue = multiprocessing.Queue()  # Tạo hàng đợi để nhận kết quả từ AI
            # Gọi hàm AI để tìm nước đi tốt nhất
            findBestMove(gs, validMoves, return_queue)
            aiMove = return_queue.get()  # Lấy kết quả từ hàng đợi
            if aiMove is None:  # Trong trường hợp AI không đưa ra được nước đi
                aiMove = findRandomMove(validMoves)  # Dùng nước đi ngẫu nhiên
            print(f"AI chose move: {aiMove.getChessNotation()}")
            gs.makeMove(aiMove)
            moveMade = True

        if moveMade:
            validMoves = gs.getAllValidMoves()
            moveMade = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.stalemate:
            gameOver = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()



def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQSIZE, SQSIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQSIZE, r * SQSIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQSIZE * move.endCol, SQSIZE * move.endRow))


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    global colors
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


def drawText(screen, text):
    font = p.font.SysFont("Arial", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Red"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
