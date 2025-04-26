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
        self.moveFunctions = {"p": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                              "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = ()  # tọa độ empassant có thể thực hiện
        self.enpassant_possible_log = [self.enpassantPossible]
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs)]
        self.last_positions = []

    def makeMove(self, move):
        """
        Thực hiện một nước đi trên bàn cờ, bao gồm các loại nước đi đặc biệt như phong cấp, bắt tốt qua đường,
        và nhập thành.
        """
        # Di chuyển quân cờ
        self.board[move.startRow][move.startCol] = "--"  # Xóa quân cờ ở ô ban đầu
        self.board[move.endRow][move.endCol] = move.pieceMoved  # Đặt quân cờ ở ô đích
        self.moveLog.append(move)  # Ghi log nước đi
        self.whiteToMove = not self.whiteToMove  # Đổi lượt chơi

        # Cập nhật vị trí vua
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
            self.whiteKingMoved = True  # Đánh dấu vua trắng đã di chuyển
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
            self.blackKingMoved = True  # Đánh dấu vua đen đã di chuyển

        # Phong cấp
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        # Bắt tốt qua đường (En passant)
        if move.isEnpassantMove:
            # print("Is Enpassant Move:", move.isEnpassantMove)
            self.board[move.startRow][move.endCol] = "--"  # Xóa quân tốt bị bắt (ô phía sau)

        # Cập nhật trạng thái bắt tốt qua đường (en passant)
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)  # Lưu vị trí bắt tốt qua đường
        else:
            self.enpassantPossible = ()

        # Xử lý nhập thành (castle)
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # Nhập thành cánh vua
                # Di chuyển Xe (Rook) từ h1/h8 tới f1/f8
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"  # Xóa Xe ở vị trí ban đầu
            else:  # Nhập thành cánh hậu
                # Di chuyển Xe (Rook) từ a1/a8 tới d1/d8
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"  # Xóa Xe ở vị trí ban đầu

        self.enpassant_possible_log.append(self.enpassantPossible)

        # cap nhat nhap thanh
        self.updateCastleRights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                   self.current_castling_rights.wqs, self.current_castling_rights.bqs))

    def undoMove(self):
        """
        Hoàn tác nước đi cuối cùng. Khôi phục trạng thái bàn cờ và các biến liên quan
        như trạng thái nhập thành, bắt tốt qua đường, vị trí của vua, v.v.
        """
        if len(self.moveLog) != 0:  # Chỉ hoàn tác nếu có nước đi đã được thực hiện
            move = self.moveLog.pop()  # Lấy nước đi cuối cùng trong log

            # Khôi phục trạng thái bàn cờ
            self.board[move.startRow][move.startCol] = move.pieceMoved  # Quay lại vị trí cũ
            self.board[move.endRow][move.endCol] = move.pieceCaptured  # Khôi phục quân bị bắt (nếu có)

            # Đổi lượt lại
            self.whiteToMove = not self.whiteToMove

            # Hoàn tác trạng thái vị trí của vua nếu vua di chuyển
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassant_possible_log.pop()
            self.enpassantPossible = self.enpassant_possible_log[-1]

            # undo castle rights
            self.castle_rights_log.pop()
            self.current_castling_rights = self.castle_rights_log[-1]
            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'
            self.checkmate = False
            self.stalemate = False

    def updateCastleRights(self, move):

        if move.pieceCaptured == "wR":
            if move.endCol == 0:
                self.current_castling_rights.wqs = False
            elif move.endCol == 7:
                self.current_castling_rights.wks = False
        elif move.pieceCaptured == "bR":
            if move.endCol == 0:
                self.current_castling_rights.bqs = False
            elif move.endCol == 7:
                self.current_castling_rights.bks = False

        if move.pieceMoved == 'wK':
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False
        elif move.pieceMoved == 'bK':
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.current_castling_rights.wqs = False
                elif move.startCol == 7:
                    self.current_castling_rights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.current_castling_rights.bqs = False
                elif move.startCol == 7:
                    self.current_castling_rights.bks = False

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Các hướng di chuyển: lên, xuống, trái, phải
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # Kiểm tra nếu quân cờ không ra ngoài bàn cờ
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]
        allyColor = "w" if self.whiteToMove else "b"
        for move in knightMoves:
            x, y = r + move[0], c + move[1]
            if 0 <= x < 8 and 0 <= y < 8:  # Kiểm tra nếu di chuyển trong bàn cờ
                if not piecePinned:
                    endPiece = self.board[x][y]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (x, y), self.board))

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = [(-1, -1), (-1, 1), (1, -1),
                      (1, 1)]  # Các hướng di chuyển: chéo lên trái, chéo lên phải, chéo xuống trái, chéo xuống phải
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                x = r + d[0] * i
                y = c + d[1] * i
                if 0 <= x < 8 and 0 <= y < 8:  # Kiểm tra nếu quân cờ không ra ngoài bàn cờ
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[x][y]
                        if endPiece == "--":
                            moves.append(Move((r, c), (x, y), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (x, y), self.board))
                            break
                        else:
                            break
                    else:
                        break

    def getQueenMoves(self, r, c, moves):
        # Hậu có thể di chuyển như Tượng hoặc Xe, nên kết hợp cả hai
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, row, col, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    if ally_color == "w":
                        self.whiteKingLocation = (end_row, end_col)
                    else:
                        self.blackKingLocation = (end_row, end_col)
                    in_check, pins, checks = self.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    if ally_color == "w":
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)

    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return
        if (self.whiteToMove and self.current_castling_rights.wks) or (
                not self.whiteToMove and self.current_castling_rights.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.whiteToMove and self.current_castling_rights.wqs) or (
                not self.whiteToMove and self.current_castling_rights.bqs):
            self.getQueensideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(self, row, col, moves):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove=True))

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

    def getAllValidMoves(self):
        """
        Lấy tất cả các nước đi hợp lệ cho bên đang di chuyển, bao gồm cả nước nhập thành (có di chuyển Xe).
        """
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()  # Kiểm tra chiếu, ghim và các nước chiếu khác

        if self.whiteToMove:
            kingRow, kingCol = self.whiteKingLocation
        else:
            kingRow, kingCol = self.blackKingLocation

        if self.inCheck:
            if len(self.checks) == 1:  # Một chiếu, cần xử lý nước hợp lệ để gỡ chiếu.
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == 'N':  # Quân chiếu là Mã, chỉ có ô của Mã là hợp lệ
                    validSquares = [(checkRow, checkCol)]
                else:  # Các quân khác (Hậu, Xe, Tượng): tất cả các ô trên đường chiếu là hợp lệ
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:  # Tới ô của quân chiếu
                            break
                # Loại bỏ các nước không đi vào ô hợp lệ
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':  # Không phải nước đi của Vua
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:  # Nếu có nhiều hơn 1 nước chiếu, chỉ có Vua được phép di chuyển
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()

            # Kiểm tra và thêm nước nhập thành nếu không bị chiếu
            if self.whiteToMove:
                # Nhập thành cánh vua (King-side castling)
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                # Nhập thành cánh vua (King-side castling)
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        # Xử lý loại bỏ nước đi vào các ô phía sau vua bị chiếu
        if self.inCheck and len(self.checks) == 1:  # Nếu có một quân đang chiếu Vua
            check = self.checks[0]
            checkRow, checkCol = check[0], check[1]
            pieceChecking = self.board[checkRow][checkCol]

            # Chỉ xử lý cho quân Hậu, Xe, Tượng
            if pieceChecking[1] in ['Q', 'R', 'B']:
                # Tính hướng chiếu
                direction = (check[2], check[3])

                # Loại bỏ nước đi vào ô phía sau Vua trên hướng này
                squares_to_remove = []
                for i in range(1, 8):
                    endRow = kingRow - direction[0] * i
                    endCol = kingCol - direction[1] * i
                    if 0 <= endRow < 8 and 0 <= endCol < 8:  # Vẫn nằm trong bàn cờ
                        if self.board[endRow][endCol] != "--":  # Gặp một quân cờ
                            break
                        squares_to_remove.append((endRow, endCol))
                    else:
                        break

                # Loại bỏ các nước đi đến các ô trong `squares_to_remove`
                for i in range(len(moves) - 1, -1, -1):
                    if (moves[i].endRow, moves[i].endCol) in squares_to_remove:
                        moves.remove(moves[i])

        # Kiểm tra trạng thái kết thúc trò chơi
        if len(moves) == 0:
            if self.isInCheck():  # Nếu không có nước nào và vua đang bị chiếu -> chiếu hết
                self.checkmate = True
            else:  # Nếu không bị chiếu -> hòa cờ
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        # Khôi phục trạng thái castle rights
        self.current_castling_rights = temp_castle_rights
        return moves

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    def isInCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        opponentMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in opponentMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False
    
    def updateLastPositions(self):
        fen = self.boardToString()
        self.last_positions.append(fen)
        if len(self.last_positions) > 9:
            self.last_positions.pop(0)

    def isThreefoldRepetitionConsecutive(self):
        if len(self.last_positions) < 9:
            return False
        return (self.last_positions[8] == self.last_positions[4] == self.last_positions[0])
    
    def boardToString(self):
        board_str = ''.join([''.join(row) for row in self.board])
        turn_str = 'w' if self.whiteToMove else 'b'
        return board_str + turn_str

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:
            move_amount = -1
            start_row = 6
            enemy_color = "b"
            king_row, king_col = self.whiteKingLocation
        else:
            move_amount = 1
            start_row = 1
            enemy_color = "w"
            king_row, king_col = self.blackKingLocation
        if self.board[r + move_amount][c] == "--":
            if not piecePinned or pinDirection == (move_amount, 0):
                moves.append(Move((r, c), (r + move_amount, c), self.board))
                if r == start_row and self.board[r + 2 * move_amount][c] == "--":
                    moves.append(Move((r, c), (r + 2 * move_amount, c), self.board))
        if c - 1 >= 0:
            if not piecePinned or pinDirection == (move_amount, -1):
                if self.board[r + move_amount][c - 1][0] == enemy_color:
                    moves.append(Move((r, c), (r + move_amount, c - 1), self.board))
                if (r + move_amount, c - 1) == self.enpassantPossible:
                    attacking_piece = blocking_piece = False
                    if king_row == r:
                        if king_col < c:
                            inside_range = range(king_col + 1, c - 1)
                            outside_range = range(c + 1, 8)
                        else:
                            inside_range = range(king_col - 1, c, -1)
                            outside_range = range(c - 2, -1, -1)
                        for i in inside_range:
                            if self.board[r][i] != "--":
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[r][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((r, c), (r + move_amount, c - 1), self.board, isEnpassantMove=True))
        if c + 1 <= 7:
            if not piecePinned or pinDirection == (move_amount, +1):
                if self.board[r + move_amount][c + 1][0] == enemy_color:
                    moves.append(Move((r, c), (r + move_amount, c + 1), self.board))
                if (r + move_amount, c + 1) == self.enpassantPossible:
                    attacking_piece = blocking_piece = False
                    if king_row == r:
                        if king_col < c:
                            inside_range = range(king_col + 1, c)
                            outside_range = range(c + 2, 8)
                        else:
                            inside_range = range(king_col - 1, c + 1, -1)
                            outside_range = range(c - 1, -1, -1)
                        for i in inside_range:
                            if self.board[r][i] != "--":
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[r][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((r, c), (r + move_amount, c + 1), self.board, isEnpassantMove=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        """
        Khởi tạo một nước đi trong trò chơi.
        Args:
        - startSq (tuple): Tọa độ ô bắt đầu (hàng, cột).
        - endSq (tuple): Tọa độ ô kết thúc (hàng, cột).
        - board (list): Trạng thái bàn cờ hiện tại.
        - promotionChoice (str): Lựa chọn phong Hậu (Q, R, B, N), mặc định là None.
        - isEnpassantMove (bool): True nếu là nước bắt tốt qua đường, mặc định False.
        - isCastleMove (bool): True nếu là nước nhập thành, mặc định False.
        - enpassantPossible (bool): Trạng thái `enpassantPossible` trước khi thực hiện nước đi.
        """
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # pawn promotion
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (
                self.pieceMoved == "bp" and self.endRow == 7)
        # en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        # castle move
        self.isCastleMove = isCastleMove
        self.isCaptured = self.pieceCaptured != "--"
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def getChessNotation(self):
        if self.isPawnPromotion:
            return self.getRankFile(self.endRow, self.endCol) + "Q"
        if self.isCastleMove:
            if self.endCol == 1:
                return "0-0-0"
            else:
                return "0-0"
        if self.isEnpassantMove:
            return self.getRankFile(self.startRow, self.startCol)[0] + "x" + self.getRankFile(self.endRow,
                                                                                              self.endCol) + " e.p."
        if self.pieceCaptured != "--":
            if self.pieceMoved[1] == "p":
                return self.getRankFile(self.startRow, self.startCol)[0] + "x" + self.getRankFile(self.endRow,
                                                                                                  self.endCol)
            else:
                return self.pieceMoved[1] + "x" + self.getRankFile(self.endRow, self.endCol)
        else:
            if self.pieceMoved[1] == "p":
                return self.getRankFile(self.endRow, self.endCol)
            else:
                return self.pieceMoved[1] + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def __str__(self):
        if self.isCastleMove:
            return "0-0" if self.endCol == 6 else "0-0-0"

        end_square = self.getRankFile(self.endRow, self.endCol)

        if self.pieceMoved[1] == "p":
            if self.isCaptured:
                return self.colsToFiles[self.startCol] + "x" + end_square
            else:
                return end_square + "Q" if self.isPawnPromotion else end_square

        move_string = self.pieceMoved[1]
        if self.isCaptured:
            move_string += "x"
        return move_string + end_square
