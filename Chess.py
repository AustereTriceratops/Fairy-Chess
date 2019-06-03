# TODO:
# castling
# have the game switch between white and black to move
# code check and checkmate

common_pieces = {
                'knight': 'h12',
                'bishop': 'X8',
                'rook': '+8',
                'queen': 'Q8',
                'king': 'Q1',
                'pawn': 'p',
                'threeleaper': 'h03',
                'nightrider': 'r12',
}

game_layout = {
                7: ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook'],
                6: ['pawn' for _ in range(0,8)],
                1: ['pawn' for _ in range(0,8)],
                0: ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook'],
                'white': [0,1],
                'black': [6, 7]
}

# ====================Classes=========================


class game():
    def __init__(self):
        self.layout = self.fill(game_layout)
        self.turns = 0
        self.color_to_move = 'white'

        self.board = board(self.layout)   # creates the board
        self.all_legal_moves()

    def fill(self, gl):
        for i in range(0,8,1):
            m = list(gl.keys())
            if i in m:
                pass
            else:
                gl[i] = [0 for _ in range(0,8)]
        return gl

    def unique_pieces(self, x):  # not used
        result = []
        for i in range(0, len(x)):
            if x[i] not in result:
                result.append(x[i])
        return result

    def enumerate_pieces(self, gl):  # also not used
        uniques = self.unique_pieces(gl)
        for i in range(0,1):
            pass

    def move(self, start, end):
        if type(start) == list:
            self.board.move_by_location(start,end)
        elif type(start) == int:
            self.board.move_by_index(start, end)
        self.turns += 1
        self.all_legal_moves()   # updates all legal moves with new board configuration
        self.board.show()

    def all_legal_moves(self):
        max = self.board.num_pieces
        for i in range(0, max):
            self.board.find_legal_moves(i)

    def show_legal_moves(self):   # for seeing, debugging
        max = self.board.num_pieces
        for i in range(0, max):
            # self.board.find_legal_moves(i)
            print([self.board.pieces[i].identity, self.board.pieces[i].legal_moves])


class board():
    def __init__(self, layout):
        grid = [[piece(0)]*8 for _ in range(0, 8)]
        self.grid = grid              # Grid stores things as [x][y]
        self.num_pieces = 0
        self.pieces = []
        self.layout = layout

        self.instantiate_pieces()
        self.show()

    def instantiate_pieces(self):
        for i in range(0,8):
            for n in range(0, 8):
                entry = self.layout[i][n]   # [y][x]
                m = piece(entry)
                m.location = [n, i]      # [x][y]
                if i in self.layout['white']:
                    m.side = 'white'
                else:
                    m.side = 'black'
                self.grid[n][i] = m
                if entry != 0:
                    self.grid[n][i].index = self.num_pieces
                    self.num_pieces += 1
                    self.pieces.append(m)

    def show(self):
        for i in range(7,-1,-1):
            print([self.grid[j][i].identity for j in range(0,8)])
        print('\n')

    def move_by_index(self, index, end_pos):  # requires selected.legal_moves to already be generated
        selected = self.pieces[index]
        start_pos = selected.location

        if end_pos in selected.legal_moves:
            selected.turn += 1
            selected.location = end_pos

            captured_index = self.grid[end_pos[0]][end_pos[1]].index
            if captured_index is not None:  # finds a captured piece and removes it from active play
                self.pieces[captured_index].active = False
                self.pieces[captured_index].location = None
            self.grid[end_pos[0]][end_pos[1]] = self.grid[start_pos[0]][start_pos[1]]
            self.grid[start_pos[0]][start_pos[1]] = piece(0)

            if selected.moverule[0] == 'p':
                disp = end_pos[1] - start_pos[1]
                if disp == 2 or disp == -2:  # Change later?
                    selected.ep = True  # only pawns which move 2 forward are eligible for ep capture
                    print(selected.ep)
        elif end_pos in selected.special_moves:
            selected.turn += 1
            selected.location = end_pos

            if selected.identity[0] == 'p':
                captured_index = self.grid[end_pos[0]][end_pos[1]-1].index
                self.pieces[captured_index].active = False
                self.pieces[captured_index].location = None
                self.grid[end_pos[0]][end_pos[1]] = self.grid[start_pos[0]][start_pos[1]]
                self.grid[end_pos[0]][end_pos[1] - 1] = piece(0)
                self.grid[start_pos[0]][start_pos[1]] = piece(0)
            print('something special')
        else:
            print("not legal")

        # self.show()

    def clear_en_passant(self, index):  # broken very broken
        selected = self.pieces[index]
        if selected.ep:  # en passant must be done immediately after or else it can't be used
            selected.ep = False

    def index_from_location(self, loc):  # [x,y]
        assert type(loc) is list
        return self.grid[loc[0]][loc[1]].index

    def identity_from_location(self, loc):
        assert type(loc) is list
        return self.grid[loc[0]][loc[1]].identity

    def move_by_location(self, start_pos, end_pos):
        index = self.index_from_location(start_pos)
        self.move_by_index(index, end_pos)

    def is_vacant(self, pos):  # will require a reference side (black/white) for captures
        if self.grid[pos[0]][pos[1]].identity == '__':
            return True
        else:
            return False

    def is_capturable(self, pos, side):   # side is the capturing side. Assumes square is not vacant
        selected = self.grid[pos[0]][pos[1]]
        if side == selected.side:
            return False
        else:
            return True

    def find_legal_moves(self, index):
        selected = self.pieces[index]
        side = selected.side
        activity = selected.active
        r = selected.moverule[0]
        l = []  # legal moves
        s = []  # special moves (promotion, en passant, castling)

        if activity is False:    # returns [] for captured pieces
            selected.legal_moves = l
            return

        if r == 'p':    # seems like spaghetti code, I'll have to figure out how to simplify
            if selected.side == 'white':
                ref = [[0, 1], [0, 2], [-1, 1], [1, 1]]
            else:
                ref = [[0, -1], [0, -2], [-1, -1], [1, -1]]
            promotion = ['promote_Q', 'promote_kn']
            spots = [[ref[i][n] + selected.location[n] for n in range(0, 2)] for i in range(0, len(ref))]
            en_passant = [[selected.location[0]-1,selected.location[1]], [selected.location[0]+1,selected.location[1]]]
            if 0 <= spots[0][0] < 8 and 0 <= spots[0][1] < 8:
                if self.is_vacant(spots[0]):
                    l.append(spots[0])
                    if 0 <= spots[1][0] < 8 and 0 <= spots[1][1] < 8:
                        if self.is_vacant(spots[1]) and selected.turn == 0:
                            l.append(spots[1])
            for i in range(2,4):
                if 0 <= spots[i][0] < 8 and 0 <= spots[i][1] < 8:
                    if not self.is_vacant(spots[i]) and self.is_capturable(spots[i], side):
                        l.append(spots[i])
            for i in range(0,2):  # adds en passant to special moves
                ep = en_passant[i]
                if 0 <= ep[0] < 8 and 0 <= ep[1] < 8:
                    cap = self.grid[ep[0]][ep[1]]
                    if cap.identity[0] == 'p' and cap.ep and self.is_capturable(ep, side):
                        s.append(spots[i+2])



        if r == 'h':
            ref = selected.moves
            spots = [[ref[i][n] + selected.location[n] for n in range(0, 2)] for i in range(0, len(ref))]
            for i in spots:
                if 0 <= i[0] < 8 and 0 <= i[1] < 8:
                    if self.is_vacant(i):
                        l.append(i)
                    elif self.is_capturable(i, side):
                        l.append(i)

        if r == '+' or r == 'Q':
            limit = int(selected.moverule[1])
            basis = [[0, 1], [1, 0], [0, -1], [-1, 0]]
            for i in basis:
                for j in range(0,limit):
                    spot = [selected.location[n] + (j+1)*i[n] for n in range(0, 2)]
                    if 0 > spot[0] or spot[0] >= 8 or 0 > spot[1] or spot[1] >= 8:
                        break
                    if self.is_vacant(spot):
                        l.append(spot)
                    elif self.is_capturable(spot, side):
                        l.append(spot)
                        break
                    else:
                        break

        if r == 'X' or r == 'Q':
            limit = int(selected.moverule[1])
            basis = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
            for i in basis:
                for j in range(0,limit):
                    spot = [selected.location[n] + (j+1)*i[n] for n in range(0, 2)]
                    if 0 > spot[0] or spot[0] >= 8 or 0 > spot[1] or spot[1] >= 8:
                        break
                    if self.is_vacant(spot):
                        l.append(spot)
                    elif self.is_capturable(spot, side):
                        l.append(spot)
                        break
                    else:
                        break
        if r == 'r':
            limit = 8   # arbitrary
            basis = selected.moves
            for i in basis:
                for j in range(0,limit):
                    spot = [selected.location[n] + (j+1)*i[n] for n in range(0, 2)]
                    if 0 > spot[0] or spot[0] >= 8 or 0 > spot[1] or spot[1] >= 8:
                        break
                    if self.is_vacant(spot):
                        l.append(spot)
                    elif self.is_capturable(spot, side):
                        l.append(spot)
                        break
                    else:
                        break

        selected.legal_moves = l
        selected.special_moves = s


class piece():
    def __init__(self, move):
        self.location = None
        self.index = None
        self.turn = 0
        self.identity = move
        self.basis = None
        self.side = None
        self.legal_moves = None
        self.special_moves = None
        self.active = True
        self.ep = False

        if move in common_pieces:
            moverule = common_pieces[move]
            self.moverule = moverule
            self.identity = move[0:2]
            self.generate_moves()
        elif move == 0:
            self.identity = '__'
        else:
            self.moverule = move

    def generate_moves(self):  # not really useful to be called except for knights in board.find_legsl_moves()
        style = self.moverule[0]
        moves = []
        mirrors = [[1, 1], [-1, 1], [1, -1], [-1, -1]]

        if style == 'h' or style == 'r':
            assert len(self.moverule) == 3
            horizontalSpeed = int(self.moverule[1])
            verticalspeed = int(self.moverule[2])
            basis = [horizontalSpeed, verticalspeed]
            rbasis = [verticalspeed, horizontalSpeed]
            for i in range(0,4):
                m = [basis[0]*mirrors[i][0], basis[1]*mirrors[i][1]]
                m2 = [rbasis[0]*mirrors[i][0], rbasis[1]*mirrors[i][1]]
                moves.append(m)
                moves.append(m2)
            self.basis = basis
            self.moves = moves

        if style == 'x':
            limit = int(self.moverule[1])
            basis = [1,1]

            for i in range(1,limit+1):
                m = [[basis[n]*i*mirrors[j][n] for n in range(0,2)] for j in range(0,4)]
                for j in range(0,4):
                    moves.append(m[j])
            self.basis = basis
            self.moves = moves

        if style == '+':
            limit = int(self.moverule[1])
            basis = [[1, 0], [0, 1]]
            for i in range(1, limit + 1):
                for j in range(0, 2):
                    m = [basis[j][n] * i for n in range(0, 2)]
                    m2 = [-m[n] for n in range(0, 2)]
                    moves.append(m)
                    moves.append(m2)
            self.moves = moves
            self.basis = basis[0]

        if style == 'Q':
            limit = int(self.moverule[1])
            rbasis = [[1, 0], [0, 1]]
            dbasis = [1,1]

            for i in range(1, limit + 1):
                for j in range(0, 2):
                    m = [rbasis[j][n] * i for n in range(0, 2)]
                    m2 = [-m[n] for n in range(0, 2)]
                    moves.append(m)
                    moves.append(m2)
            for i in range(1,limit+1):
                m = [[dbasis[n]*i*mirrors[j][n] for n in range(0,2)] for j in range(0,4)]
                for j in range(0,4):
                    moves.append(m[j])
            self.moves = moves
            self.basis = [rbasis[0], dbasis]

        if style == 'p':
            self.moves = [[-1, 1], [0, 1], [1, 1], [0, 2], ['promote_Q'], ['promote_kn']]

    def show_location(self):
        print(self.location)

    def show_moves(self):
        print(self.moves)

    def is_possible_move(self,startPos, newPos):  # outdated and not used
        assert type(newPos) == list
        assert newPos[0] >=0 and newPos[1] >=0
        assert newPos[0] <8 and newPos[1] < 8
        displacement = [newPos[i] - startPos[i] for i in range(0,2)]
        if displacement in self.moves:
            return True
        else:
            return False


# =================Calls & debugging======================











