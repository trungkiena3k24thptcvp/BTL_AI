import pygame as p
import ChessEngine
import sys
import Ch_AI
from multiprocessing import Process, Queue
WIDTH = HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 200
MOVE_LOG_PANEL_HEIGHT = HEIGHT
DIMENSION = 8
SQSIZE = HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}


def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQSIZE, SQSIZE))


def main():
    print("SELECT PLAYER 1 (WHITE)")
    player_select_one = input("TYPE 1 IF HUMAN ELSE PRESS ANY KEY TO CONTINUE: ")
    print("SELECT PLAYER 2 (BLACK)")
    player_select_two = input("TYPE 1 IF HUMAN ELSE PRESS ANY KEY TO CONTINUE: ")
    playerOne = (player_select_one == "1") 
    playerTwo = (player_select_two == "1")
    p.init()
    screen = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getAllValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    gameOver = False
    ai_thinking = False
    move_undone = False
    move_finder_process = None
    move_log_font = p.font.SysFont("Arial", 14, False, False)
    sqSelected = ()
    playerClicks = []


    while running:
        isHumanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()

            elif e.type == p.MOUSEBUTTONDOWN: 
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0] // SQSIZE
                    row = location[1] // SQSIZE
                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 and isHumanTurn:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print("Selected move:", move.getChessNotation())
                        print("Valid moves:", [m.getChessNotation() for m in validMoves])
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == p.K_r: #reset game
                    gs = ChessEngine.GameState()
                    validMoves = gs.getAllValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True


        # AI thực hiện nước đi nếu là lượt AI
        if not gameOver and not isHumanTurn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue() 
                move_finder_process = Process(target=Ch_AI.findBestMove, args=(gs, validMoves, return_queue))
                move_finder_process.start()
            if not move_finder_process.is_alive():
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = Ch_AI.findRandomMove(validMoves)
                gs.makeMove(ai_move)
                moveMade = True
                animate = True
                ai_thinking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getAllValidMoves()
            gs.updateLastPositions()
            print(gs.last_positions)
            if gs.isThreefoldRepetitionConsecutive():
                gameOver = True
                gs.stalemate = True
            moveMade = False
            animate = False
            move_undone = False

        drawGameState(screen, gs, validMoves, sqSelected)
        if not gameOver:
            drawMoveLog(screen, gs, move_log_font)
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


def drawMoveLog(screen, gs, font):

    move_log_rect = p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), move_log_rect)
    move_log = gs.moveLog
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, p.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing

def animateMove(move, screen, board, clock):
    global colors
    d_row = move.endRow - move.startRow
    d_col = move.endCol - move.startCol
    frames_per_square = 5 
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.startRow + d_row * frame / frame_count, move.startCol + d_col * frame / frame_count)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        end_square = p.Rect(move.endCol * SQSIZE, move.endRow * SQSIZE, SQSIZE, SQSIZE)
        p.draw.rect(screen, color, end_square)
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enpassant_row = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                end_square = p.Rect(move.endCol * SQSIZE, enpassant_row * SQSIZE, SQSIZE, SQSIZE)
            screen.blit(IMAGES[move.pieceCaptured], end_square)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE))
        p.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
