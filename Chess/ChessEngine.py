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
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()  # tọa độ empassant có thể thực hiện
        self.whiteKingMoved = False
        self.blackKingMoved = False
        self.whiteRookMoved = {'k_side': False, 'q_side': False}  # Xe Trắng
        self.blackRookMoved = {'k_side': False, 'q_side': False}

    def canCastle(self, kingSide: bool) -> bool:
        """
        Kiểm tra xem nước nhập thành có hợp lệ hay không.
        Args:
        - kingSide: (bool) True nếu nhập thành cánh vua, False nếu nhập thành cánh hậu.

        Returns:
        - (bool): True nếu có thể nhập thành, False nếu không hợp lệ.
        """
        # Nếu vua hiện đang bị chiếu, không thể nhập thành
        if self.inCheck:
            return False

        # Kiểm tra điều kiện của quân trắng
        if self.whiteToMove:
            kingRow, kingCol = 7, 4  # Vị trí mặc định của Vua trắng
            rookCol = 7 if kingSide else 0  # Cột của Xe (h1 hoặc a1)

            # Kiểm tra trạng thái đã di chuyển của Vua và Xe
            if self.whiteKingMoved or self.whiteRookMoved['k_side' if kingSide else 'q_side']:
                return False

        # Kiểm tra điều kiện của quân đen
        else:
            kingRow, kingCol = 0, 4  # Vị trí mặc định của Vua đen
            rookCol = 7 if kingSide else 0  # Cột của Xe (h8 hoặc a8)

            # Kiểm tra trạng thái đã di chuyển của Vua và Xe
            if self.blackKingMoved or self.blackRookMoved['k_side' if kingSide else 'q_side']:
                return False

        # Kiểm tra các ô giữa Vua và Xe có trống không
        step = 1 if rookCol > kingCol else -1
        for col in range(kingCol + step, rookCol, step):
            if self.board[kingRow][col] != '--':  # Nếu bất kỳ ô nào không trống
                return False

        # Kiểm tra các ô Vua sẽ đi qua hoặc đích đến có bị tấn công không
        for col in (kingCol, kingCol + step, kingCol + 2 * step):
            if self.squareUnderAttack(kingRow, col):  # Nếu ô đó bị tấn công
                return False

        return True

    def castleMove(self, kingSide: bool):
        """
        Thực hiện nước nhập thành cho bên đang di chuyển.
        Args:
        - kingSide: (bool) True nếu nhập thành cánh vua, False nếu nhập thành cánh hậu.
        """
        # Xác định các tham số theo lượt
        kingRow = 7 if self.whiteToMove else 0  # Vua trắng ở hàng 7, vua đen ở hàng 0
        kingCol = 4  # Vị trí mặc định của vua
        rookCol = 7 if kingSide else 0  # Vị trí của xe (h1/h8 cho cánh vua, a1/a8 cho cánh hậu)
        step = 1 if kingSide else -1  # Hướng di chuyển (phải +1, trái -1)
        king = 'wK' if self.whiteToMove else 'bK'
        rook = 'wR' if self.whiteToMove else 'bR'

        # Di chuyển vua và xe trên bàn cờ
        self.board[kingRow][kingCol] = '--'  # Xóa vua khỏi vị trí cũ
        self.board[kingRow][kingCol + 2 * step] = king  # Đưa vua đến vị trí mới
        self.board[kingRow][rookCol] = '--'  # Xóa xe khỏi vị trí cũ
        self.board[kingRow][kingCol + step] = rook  # Đưa xe đến vị trí mới

        # Cập nhật vị trí vua và trạng thái đã di chuyển
        if self.whiteToMove:
            self.whiteKingLocation = (kingRow, kingCol + 2 * step)
            self.whiteKingMoved = True
            self.whiteRookMoved['k_side' if kingSide else 'q_side'] = True
        else:
            self.blackKingLocation = (kingRow, kingCol + 2 * step)
            self.blackKingMoved = True
            self.blackRookMoved['k_side' if kingSide else 'q_side'] = True

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
        if move.isPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[
                                                       0] + move.promotionChoice  # Thay thế bằng quân cờ mới

        # Bắt tốt qua đường (En passant)
        if move.isEnpassantMove:
            print("Is Enpassant Move:", move.isEnpassantMove)
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
            elif move.endCol - move.startCol == -2:  # Nhập thành cánh hậu
                # Di chuyển Xe (Rook) từ a1/a8 tới d1/d8
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"  # Xóa Xe ở vị trí ban đầu

        # Đánh dấu rằng Xe đã di chuyển (cho cánh vua/hậu)
        if move.pieceMoved == 'wR':
            if move.startRow == 7 and move.startCol == 0:  # Xe cánh hậu trắng
                self.whiteRookMoved['q_side'] = True
            elif move.startRow == 7 and move.startCol == 7:  # Xe cánh vua trắng
                self.whiteRookMoved['k_side'] = True
        elif move.pieceMoved == 'bR':
            if move.startRow == 0 and move.startCol == 0:  # Xe cánh hậu đen
                self.blackRookMoved['q_side'] = True
            elif move.startRow == 0 and move.startCol == 7:  # Xe cánh vua đen
                self.blackRookMoved['k_side'] = True

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
                self.whiteKingMoved = False  # Hoàn tác trạng thái vua trắng đã di chuyển
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
                self.blackKingMoved = False  # Hoàn tác trạng thái vua đen đã di chuyển

            # Hoàn tác nước nhập thành (nếu nước đi là nhập thành)
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # Nhập thành cánh vua
                    # Di chuyển Xe về vị trí cũ
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                elif move.endCol - move.startCol == -2:  # Nhập thành cánh hậu
                    # Di chuyển Xe về vị trí cũ
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

            # Hoàn tác trạng thái đã di chuyển của Xe
            if move.pieceMoved == 'wR':
                if move.startRow == 7 and move.startCol == 0:  # Xe cánh hậu trắng
                    self.whiteRookMoved['q_side'] = False
                elif move.startRow == 7 and move.startCol == 7:  # Xe cánh vua trắng
                    self.whiteRookMoved['k_side'] = False
            elif move.pieceMoved == 'bR':
                if move.startRow == 0 and move.startCol == 0:  # Xe cánh hậu đen
                    self.blackRookMoved['q_side'] = False
                elif move.startRow == 0 and move.startCol == 7:  # Xe cánh vua đen
                    self.blackRookMoved['k_side'] = False

            # Hoàn tác trạng thái phong cấp (nếu có)
            if move.isPromotion:
                self.board[move.startRow][move.startCol] = move.pieceMoved  # Đưa tốt quay lại
                self.board[move.endRow][move.endCol] = move.pieceCaptured  # Khôi phục tốt bị thay thế

            # Hoàn tác nước bắt tốt qua đường (en passant)
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"  # Xóa quân tốt của đối phương ở ô mục tiêu
                self.board[move.startRow][move.endCol] = move.pieceCaptured  # Khôi phục quân tốt bị bắt

            # Khôi phục trạng thái bắt tốt qua đường (en passant)
            self.enpassantPossible = move.enpassantPossibleBeforeMove

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
        tempEnpassantPossible = self.enpassantPossible  # Lưu trạng thái en passant ban đầu
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()  # Kiểm tra chiếu, ghim và các nước chiếu khác
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

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
                if not self.whiteKingMoved and not self.whiteRookMoved['k_side']:
                    if self.board[7][5] == '--' and self.board[7][6] == '--':  # Ô giữa trống
                        if not self.squareUnderAttack(7, 4) and not self.squareUnderAttack(7,
                                                                                           5) and not self.squareUnderAttack(
                            7, 6):
                            moves.append(Move((7, 4), (7, 6), self.board, isCastleMove=True))
                # Nhập thành cánh hậu (Queen-side castling)
                if not self.whiteKingMoved and not self.whiteRookMoved['q_side']:
                    if self.board[7][1] == '--' and self.board[7][2] == '--' and self.board[7][
                        3] == '--':  # Ô giữa trống
                        if not self.squareUnderAttack(7, 4) and not self.squareUnderAttack(7,
                                                                                           3) and not self.squareUnderAttack(
                            7, 2):
                            moves.append(Move((7, 4), (7, 2), self.board, isCastleMove=True))
            else:
                # Nhập thành cánh vua (King-side castling)
                if not self.blackKingMoved and not self.blackRookMoved['k_side']:
                    if self.board[0][5] == '--' and self.board[0][6] == '--':  # Ô giữa trống
                        if not self.squareUnderAttack(0, 4) and not self.squareUnderAttack(0,
                                                                                           5) and not self.squareUnderAttack(
                            0, 6):
                            moves.append(Move((0, 4), (0, 6), self.board, isCastleMove=True))
                # Nhập thành cánh hậu (Queen-side castling)
                if not self.blackKingMoved and not self.blackRookMoved['q_side']:
                    if self.board[0][1] == '--' and self.board[0][2] == '--' and self.board[0][
                        3] == '--':  # Ô giữa trống
                        if not self.squareUnderAttack(0, 4) and not self.squareUnderAttack(0,
                                                                                           3) and not self.squareUnderAttack(
                            0, 2):
                            moves.append(Move((0, 4), (0, 2), self.board, isCastleMove=True))

        # Kiểm tra trạng thái kết thúc trò chơi
        if len(moves) == 0:
            if self.isInCheck():  # Nếu không có nước nào và vua đang bị chiếu -> chiếu hết
                self.checkmate = True
            else:  # Nếu không bị chiếu -> hòa cờ
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        # Khôi phục trạng thái en passant
        self.enpassantPossible = tempEnpassantPossible
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
            # di chuyen
            if self.board[r - 1][c] == '--':
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == '--':
                        moves.append(Move((r, c), (r - 2, c), self.board))
            # bat trai
            if c - 1 >= 0 and self.board[r - 1][c - 1][0] == 'b':
                if not piecePinned or pinDirection == (-1, -1):
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c - 1 >= 0 and (r - 1, c - 1) == self.enpassantPossible:
                if not piecePinned or pinDirection == (-1, -1):
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            # bat phai
            if c + 1 <= 7 and self.board[r - 1][c + 1][0] == 'b':
                if not piecePinned or pinDirection == (-1, 1):
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
            if c + 1 <= 7 and (r - 1, c + 1) == self.enpassantPossible:
                if not piecePinned or pinDirection == (-1, 1):
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))
        else:
            # di chuyen
            if self.board[r + 1][c] == '--':
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == '--':
                        moves.append(Move((r, c), (r + 2, c), self.board))
            # bat trai
            if c - 1 >= 0 and self.board[r + 1][c - 1][0] == 'w':
                if not piecePinned or pinDirection == (1, -1):
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c - 1 >= 0 and (r + 1, c - 1) == self.enpassantPossible:
                if not piecePinned or pinDirection == (1, -1):
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            # bat phai
            if c + 1 <= 7 and self.board[r + 1][c + 1][0] == 'w':
                if not piecePinned or pinDirection == (1, 1):
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
            if c + 1 <= 7 and (r + 1, c + 1) == self.enpassantPossible:
                if not piecePinned or pinDirection == (1, 1):
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, promotionChoice=None, isEnpassantMove=False, isCastleMove=False):
        """
        Khởi tạo một nước đi trong trò chơi.
        Args:
        - startSq (tuple): Tọa độ ô bắt đầu (hàng, cột).
        - endSq (tuple): Tọa độ ô kết thúc (hàng, cột).
        - board (list): Trạng thái bàn cờ hiện tại.
        - promotionChoice (str): Lựa chọn phong Hậu (Q, R, B, N), mặc định là None.
        - isEnpassantMove (bool): True nếu là nước bắt tốt qua đường, mặc định False.
        - isCastleMove (bool): True nếu là nước nhập thành, mặc định False.
        """
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # Kiểm tra bắt tốt qua đường (en passant)
        self.isEnpassantMove = isEnpassantMove

        # Kiểm tra phong cấp
        self.isPromotion = False
        self.promotionChoice = promotionChoice
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7):
            self.isPromotion = True

        # Kiểm tra nhập thành
        self.isCastleMove = isCastleMove

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
