class GameState(): 
    def __init__(self): 
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved 
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    def undoMove(self):
        if len(self.moveLog) != 0: 
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

    def getRookMoves(self, r, c, moves):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Các hướng di chuyển: lên, xuống, trái, phải
        for direction in directions:
            x, y = r, c
            while True:
                x += direction[0]
                y += direction[1]
                if 0 <= x < 8 and 0 <= y < 8:  # Kiểm tra nếu quân cờ không ra ngoài bàn cờ
                    if self.board[x][y] == '--':  # Vị trí trống
                        moves.append(Move((r, c), (x, y), self.board))
                    elif self.board[x][y][0] != self.board[r][c][0]:  # Quân cờ đối phương
                        moves.append(Move((r, c), (x, y), self.board))
                        break  # Quân đối phương có thể bị ăn, nhưng không thể đi tiếp
                    else:
                        break  # Quân cùng màu, không thể đi qua
                else:
                    break  # Ra ngoài bàn cờ, dừng

    def getKnightMoves(self, r, c, moves):
        knightMoves = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]
        for move in knightMoves:
            x, y = r + move[0], c + move[1]
            if 0 <= x < 8 and 0 <= y < 8:  # Kiểm tra nếu di chuyển trong bàn cờ
                if self.board[x][y] == '--' or self.board[x][y][0] != self.board[r][c][
                    0]:  # Vị trí trống hoặc quân đối phương
                    moves.append(Move((r, c), (x, y), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = [(-1, -1), (-1, 1), (1, -1),
                      (1, 1)]  # Các hướng di chuyển: chéo lên trái, chéo lên phải, chéo xuống trái, chéo xuống phải
        for direction in directions:
            x, y = r, c
            while True:
                x += direction[0]
                y += direction[1]
                if 0 <= x < 8 and 0 <= y < 8:  # Kiểm tra nếu quân cờ không ra ngoài bàn cờ
                    if self.board[x][y] == '--':  # Vị trí trống
                        moves.append(Move((r, c), (x, y), self.board))
                    elif self.board[x][y][0] != self.board[r][c][0]:  # Quân cờ đối phương
                        moves.append(Move((r, c), (x, y), self.board))
                        break  # Quân đối phương có thể bị ăn, nhưng không thể đi tiếp
                    else:
                        break  # Quân cùng màu, không thể đi qua
                else:
                    break  # Ra ngoài bàn cờ, dừng

    def getQueenMoves(self, r, c, moves):
        # Hậu có thể di chuyển như Tượng hoặc Xe, nên kết hợp cả hai
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1),
                     (1, 1)]  # Tất cả các hướng di chuyển của vua
        for move in kingMoves:
            x, y = r + move[0], c + move[1]
            if 0 <= x < 8 and 0 <= y < 8:  # Kiểm tra nếu di chuyển trong bàn cờ
                if self.board[x][y] == '--' or self.board[x][y][0] != self.board[r][c][
                    0]:  # Vị trí trống hoặc quân đối phương
                    moves.append(Move((r, c), (x, y), self.board))

    def getAllPossibleMoves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == '--':
                    continue
                color = piece[0]
                if (color == 'w' and self.whiteToMove) or (color == 'b' and not self.whiteToMove):
                    pieceType = piece[1]
                    if pieceType == 'p':
                        self.getPawnMoves(r, c, moves)
                    elif pieceType == 'R':
                        self.getRookMoves(r, c, moves)
                    elif pieceType == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif pieceType == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif pieceType == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif pieceType == 'K':
                        self.getKingMoves(r, c, moves)
        return moves

    def isCheck(self, kingPos, opponent_pieces):
        # Kiểm tra tất cả các quân cờ đối phương để xem có quân nào có thể tấn công quân vua
        for piece in opponent_pieces:
            # Kiểm tra xem quân đối phương có thể di chuyển đến vị trí của quân vua không
            possibleMoves = self.getAllPossibleMoves()  # chuyen thah ham getAllPossibleMoveIfChecked
            for move in possibleMoves:
                if move.endRow == kingPos[0] and move.endCol == kingPos[1]:
                    return True
        return False

    def getAllValidMoves(self):
        validMoves = []
        possibleMoves = self.getAllPossibleMoves()

        # Lấy vị trí quân vua của người chơi
        kingPos = self.getKingPosition()  # Cần thêm hàm getKingPosition() để lấy vị trí quân vua

        # Kiểm tra nếu quân vua đang bị chiếu
        if self.isCheck(kingPos, self.getOpponentPieces()):
            # Nếu quân vua bị chiếu, chỉ chấp nhận những nước đi giúp giải quyết tình trạng chiếu
            for move in possibleMoves:
                # Tạm thời thực hiện nước đi
                self.makeMove(move)

                # Kiểm tra nếu quân vua vẫn bị chiếu sau khi thực hiện nước đi
                if not self.isCheck(kingPos, self.getOpponentPieces()):
                    validMoves.append(move)

                # Quay lại trạng thái ban đầu (undo move)
                self.undoMove()
        else:
            # Nếu quân vua không bị chiếu, tất cả các nước đi hợp lệ được chấp nhận
            validMoves = possibleMoves

        return validMoves


    def getKingPosition(self):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if self.whiteToMove and piece == 'wK':
                    return (r, c)
                elif not self.whiteToMove and piece == 'bK':
                    return (r, c)
        return (-1, -1)

    def getOpponentPieces(self):
        opponentPieces = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                if piece != '--' and (piece[0] == 'b' and self.whiteToMove or piece[0] == 'w' and not self.whiteToMove):
                    opponentPieces.append(piece)
        return opponentPieces

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r - 1][c] == '--':
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == '--':
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0 and self.board[r - 1][c - 1][0] == 'b':
                moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c + 1 <= 7 and self.board[r - 1][c + 1][0] == 'b':
                moves.append(Move((r, c), (r - 1, c + 1), self.board))
        else:
            if self.board[r + 1][c] == '--':
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == '--':
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0 and self.board[r + 1][c - 1][0] == 'w':
                moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7 and self.board[r + 1][c + 1][0] == 'w':
                moves.append(Move((r, c), (r + 1, c + 1), self.board))
                
            
class Move():

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    
    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    def __eq__(self, other):
        return (self.startRow == other.startRow and
                self.startCol == other.startCol and
                self.endRow == other.endRow and
                self.endCol == other.endCol and
                self.pieceMoved == other.pieceMoved and
                self.pieceCaptured == other.pieceCaptured)