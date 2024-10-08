import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Charger les images des pièces
def load_images():
    pieces = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']
    images = {}
    for piece in pieces:
        images[piece] = pygame.transform.scale(pygame.image.load(f'images/{piece}.png'), (SQUARE_SIZE, SQUARE_SIZE))
    return images

# Dessiner l'échiquier
def draw_board(win):
    win.fill(WHITE)
    for row in range(ROWS):
        for col in range(row % 2, COLS, 2):
            pygame.draw.rect(win, BLACK, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Dessiner les pièces sur l'échiquier
def draw_pieces(win, board, images):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != '--':
                win.blit(images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Initialiser le plateau avec les pièces
def create_board():
    return [
        ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
        ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
        ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
    ]

# Vérification si le chemin est libre (pour les tours, fous, et dames)
def is_path_clear(board, start_pos, end_pos):
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    if start_row == end_row:  # Déplacement horizontal
        step = 1 if end_col > start_col else -1
        for col in range(start_col + step, end_col, step):
            if board[start_row][col] != '--':
                return False
    elif start_col == end_col:  # Déplacement vertical
        step = 1 if end_row > start_row else -1
        for row in range(start_row + step, end_row, step):
            if board[row][start_col] != '--':
                return False
    elif abs(start_row - end_row) == abs(start_col - end_col):  # Déplacement diagonal
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1
        for row, col in zip(range(start_row + row_step, end_row, row_step), range(start_col + col_step, end_col, col_step)):
            if board[row][col] != '--':
                return False
    return True

# Vérification si le chemin est libre pour le roque
def is_path_clear_for_castling(board, start_pos, end_pos):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    step = 1 if end_col > start_col else -1
    for col in range(start_col + step, end_col, step):
        if board[start_row][col] != '--':
            return False
    return True

# Simuler un mouvement sur le plateau
def simulate_move(board, start_pos, end_pos):
    board_copy = [row[:] for row in board]
    board_copy[end_pos[0]][end_pos[1]] = board_copy[start_pos[0]][start_pos[1]]
    board_copy[start_pos[0]][start_pos[1]] = '--'
    return board_copy

# Trouver la position du roi
def find_king(board, turn):
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] == f'{turn}K':
                return (row, col)
    return None

# Vérifier si un roi est en échec
def is_in_check(board, king_pos, turn):
    opponent = 'b' if turn == 'w' else 'w'
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece[0] == opponent:
                if is_valid_move(board, (row, col), king_pos, opponent, None, None):
                    return True
    return False

# Vérification si un mouvement met le roi en échec
def is_in_check_after_move(board, start_pos, end_pos, turn):
    simulated_board = simulate_move(board, start_pos, end_pos)
    king_pos = find_king(simulated_board, turn)
    return is_in_check(simulated_board, king_pos, turn)

# Vérifier si les deux rois sont adjacents
def are_kings_adjacent(board, start_pos, end_pos, turn):
    opponent = 'b' if turn == 'w' else 'w'
    opponent_king_pos = find_king(board, opponent)

    # Vérifier si la case cible du roi est adjacente à l'autre roi
    if opponent_king_pos:
        row_diff = abs(end_pos[0] - opponent_king_pos[0])
        col_diff = abs(end_pos[1] - opponent_king_pos[1])
        if row_diff <= 1 and col_diff <= 1:
            return True
    return False

# Vérifier si un roque est possible
def can_castle(board, king_pos, end_pos, turn, castling_rights):
    start_row, start_col = king_pos
    end_row, end_col = end_pos
    if turn == 'w':
        if end_col == 6 and castling_rights['wK']:  # Roque petit
            if is_path_clear_for_castling(board, (7, 4), (7, 7)):
                return True
        if end_col == 2 and castling_rights['wQ']:  # Roque grand
            if is_path_clear_for_castling(board, (7, 4), (7, 0)):
                return True
    elif turn == 'b':
        if end_col == 6 and castling_rights['bK']:  # Roque petit
            if is_path_clear_for_castling(board, (0, 4), (0, 7)):
                return True
        if end_col == 2 and castling_rights['bQ']:  # Roque grand
            if is_path_clear_for_castling(board, (0, 4), (0, 0)):
                return True
    return False

# Vérification de la validité des mouvements des pièces
def is_valid_move(board, start_pos, end_pos, turn, en_passant_possible, castling_rights):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    piece = board[start_row][start_col]
    target = board[end_row][end_col]

    if piece == '--' or piece[0] != turn or piece[0] == target[0]:
        return False  # Si aucune pièce n'est sélectionnée, ou si on essaie de capturer sa propre pièce

    # Récupération du type de pièce (P, R, N, B, Q, K)
    piece_type = piece[1]

    # Validation des règles de déplacement pour chaque pièce
    if piece_type == 'P':  # Pion
        direction = -1 if turn == 'w' else 1  # Blancs avancent vers le haut, noirs vers le bas
        if start_col == end_col:
            if end_row == start_row + direction and board[end_row][end_col] == '--':
                return True
            if (start_row == 1 or start_row == 6) and end_row == start_row + 2 * direction and board[start_row + direction][end_col] == '--' and board[end_row][end_col] == '--':
                return True
        elif abs(start_col - end_col) == 1 and end_row == start_row + direction:
            if target != '--' and target[0] != turn:
                return True
            if en_passant_possible and (end_row, end_col) == en_passant_possible:
                return True
    elif piece_type == 'R':  # Tour
        if start_row == end_row or start_col == end_col:
            return is_path_clear(board, start_pos, end_pos)
    elif piece_type == 'B':  # Fou
        if abs(start_row - end_row) == abs(start_col - end_col):
            return is_path_clear(board, start_pos, end_pos)
    elif piece_type == 'Q':  # Dame
        if start_row == end_row or start_col == end_col or abs(start_row - end_row) == abs(start_col - end_col):
            return is_path_clear(board, start_pos, end_pos)
    elif piece_type == 'K':  # Roi
        if abs(start_row - end_row) <= 1 and abs(start_col - end_col) <= 1:
            if not is_in_check_after_move(board, start_pos, (end_row, end_col), turn):
                if not are_kings_adjacent(board, start_pos, (end_row, end_col), turn):
                    return True
                else:
                    print("Les rois ne peuvent pas être adjacents.")
                    return False
            else:
                return False
        if (start_row, start_col) == (7, 4) and turn == 'w':
            if end_row == 7 and (end_col == 6 or end_col == 2):
                return can_castle(board, (start_row, start_col), (end_row, end_col), turn, castling_rights)
        if (start_row, start_col) == (0, 4) and turn == 'b':
            if end_row == 0 and (end_col == 6 or end_col == 2):
                return can_castle(board, (start_row, start_col), (end_row, end_col), turn, castling_rights)
    elif piece_type == 'N':  # Cavalier
        if (abs(start_row - end_row), abs(start_col - end_col)) in [(2, 1), (1, 2)]:
            return True
    return False

# Fonction principale pour exécuter le jeu
def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Jeu d\'échecs')
    board = create_board()
    images = load_images()
    selected_piece = None
    turn = 'w'
    en_passant_possible = None  # Stocker la position éligible pour la prise en passant
    castling_rights = {'wK': True, 'wQ': True, 'bK': True, 'bQ': True}  # Droits de roque
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
                if selected_piece:
                    # Vérification de l'échec et des coups légaux
                    king_pos = find_king(board, turn)
                    if is_in_check(board, king_pos, turn):
                        simulated_board = simulate_move(board, selected_piece, (row, col))
                        king_pos = find_king(simulated_board, turn)
                        if is_in_check(simulated_board, king_pos, turn):
                            print("Ce coup n'est pas autorisé, vous êtes en échec.")
                            selected_piece = None
                            continue
                    if is_valid_move(board, selected_piece, (row, col), turn, en_passant_possible, castling_rights):
                        piece = board[selected_piece[0]][selected_piece[1]]
                        board[row][col] = piece
                        board[selected_piece[0]][selected_piece[1]] = '--'

                        # Gérer la prise en passant
                        if piece[1] == 'P' and en_passant_possible and (row, col) == en_passant_possible:
                            board[selected_piece[0]][col] = '--'

                        # Vérification si un pion a bougé de deux cases pour la prise en passant
                        if piece[1] == 'P' and abs(row - selected_piece[0]) == 2:
                            en_passant_possible = (row + (1 if turn == 'w' else -1), col)
                        else:
                            en_passant_possible = None

                        # Gérer le roque
                        if piece[1] == 'K':
                            if col == 6:  # Roque petit
                                board[row][5] = board[row][7]
                                board[row][7] = '--'
                            elif col == 2:  # Roque grand
                                board[row][3] = board[row][0]
                                board[row][0] = '--'
                            castling_rights[turn + 'K'] = False
                            castling_rights[turn + 'Q'] = False

                        # Mettre à jour les droits de roque pour les tours
                        if piece[1] == 'R':
                            if selected_piece == (7, 0):
                                castling_rights['wQ'] = False
                            elif selected_piece == (7, 7):
                                castling_rights['wK'] = False
                            elif selected_piece == (0, 0):
                                castling_rights['bQ'] = False
                            elif selected_piece == (0, 7):
                                castling_rights['bK'] = False

                        # Changement de tour après un coup valide
                        turn = 'b' if turn == 'w' else 'w'
                    selected_piece = None
                else:
                    selected_piece = (row, col)

        draw_board(win)
        draw_pieces(win, board, images)
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
