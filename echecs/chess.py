import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load images
def load_images():
    pieces = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']
    images = {}
    for piece in pieces:
        images[piece] = pygame.transform.scale(pygame.image.load(f'images/{piece}.png'), (SQUARE_SIZE, SQUARE_SIZE))
    return images

# Draw the board
def draw_board(win):
    win.fill(WHITE)
    for row in range(ROWS):
        for col in range(row % 2, COLS, 2):
            pygame.draw.rect(win, BLACK, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Draw pieces
def draw_pieces(win, board, images):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != '--':
                win.blit(images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Initialize the board
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

# Vérification si le chemin est clair (pour les fous, tours, et reines)
def is_path_clear(board, start_pos, end_pos):
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    if start_row == end_row:  # Mouvement horizontal
        step = 1 if end_col > start_col else -1
        for col in range(start_col + step, end_col, step):
            if board[start_row][col] != '--':
                return False
    elif start_col == end_col:  # Mouvement vertical
        step = 1 if end_row > start_row else -1
        for row in range(start_row + step, end_row, step):
            if board[row][start_col] != '--':
                return False
    elif abs(start_row - end_row) == abs(start_col - end_col):  # Mouvement diagonal
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1
        for row, col in zip(range(start_row + row_step, end_row, row_step), range(start_col + col_step, end_col, col_step)):
            if board[row][col] != '--':
                return False
    return True

# Vérification si un mouvement met le roi en échec
def is_in_check_after_move(board, start_pos, end_pos, turn):
    # Simuler le déplacement
    simulated_board = [row[:] for row in board]
    simulated_board[end_pos[0]][end_pos[1]] = simulated_board[start_pos[0]][start_pos[1]]
    simulated_board[start_pos[0]][start_pos[1]] = '--'

    # Trouver la position du roi après le déplacement
    king_pos = None
    for row in range(ROWS):
        for col in range(COLS):
            if simulated_board[row][col] == f'{turn}K':
                king_pos = (row, col)
                break

    # Vérifier si le roi est en échec après le mouvement
    return is_in_check(simulated_board, king_pos, turn)

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

# Vérification de la validité des mouvements des pièces
def is_valid_move(board, start_pos, end_pos, turn, en_passant_possible, castling_rights):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    piece = board[start_row][start_col]
    target = board[end_row][end_col]

    if piece == '--':  # Pas de pièce sélectionnée
        return False
    if piece[0] != turn:  # Vérifier si la pièce appartient au joueur actuel
        return False
    if piece[0] == target[0]:  # Ne pas capturer ses propres pièces
        return False

    # Récupérer le type de la pièce (K, Q, R, B, N, P)
    piece_type = piece[1]

    # Vérification des règles de déplacement pour chaque pièce
    if piece_type == 'P':  # Pion
        direction = -1 if turn == 'w' else 1  # Blancs avancent vers le haut, noirs vers le bas
        
        # Mouvement simple vers l'avant
        if start_col == end_col:
            if end_row == start_row + direction and board[end_row][end_col] == '--':
                return True
            if (start_row == 1 or start_row == 6) and end_row == start_row + 2 * direction and board[start_row + direction][end_col] == '--' and board[end_row][end_col] == '--':
                return True
        # Capture en diagonale ou prise en passant
        elif abs(start_col - end_col) == 1 and end_row == start_row + direction:
            if target != '--' and target[0] != turn:  # Capture normale
                return True
            if en_passant_possible and (end_row, end_col) == en_passant_possible:  # Prise en passant
                return True

    elif piece_type == 'R':  # Tour
        if start_row == end_row or start_col == end_col:  # Mouvement en ligne droite
            return is_path_clear(board, start_pos, end_pos)

    elif piece_type == 'B':  # Fou
        if abs(start_row - end_row) == abs(start_col - end_col):  # Mouvement en diagonale
            return is_path_clear(board, start_pos, end_pos)

    elif piece_type == 'Q':  # Reine
        if start_row == end_row or start_col == end_col or abs(start_row - end_row) == abs(start_col - end_col):  # Ligne droite ou diagonale
            return is_path_clear(board, start_pos, end_pos)

    elif piece_type == 'K':  # Roi
        if abs(start_row - end_row) <= 1 and abs(start_col - end_col) <= 1:  # Déplacement d'une case dans n'importe quelle direction
            # Empêcher le roi de se déplacer sur une case où il serait en échec
            if not is_in_check_after_move(board, start_pos, (end_row, end_col), turn):
                return True
            else:
                return False

        # Gestion du roque
        if (start_row, start_col) == (7, 4) and turn == 'w':  # Roque blanc
            if end_row == 7 and (end_col == 6 or end_col == 2):  # Vers la droite (roque petit) ou gauche (roque grand)
                return can_castle(board, (start_row, start_col), (end_row, end_col), turn, castling_rights)
        if (start_row, start_col) == (0, 4) and turn == 'b':  # Roque noir
            if end_row == 0 and (end_col == 6 or end_col == 2):  # Vers la droite (roque petit) ou gauche (roque grand)
                return can_castle(board, (start_row, start_col), (end_row, end_col), turn, castling_rights)

    elif piece_type == 'N':  # Cavalier
        if (abs(start_row - end_row), abs(start_col - end_col)) in [(2, 1), (1, 2)]:  # Mouvement en "L"
            return True

    return False  # Si aucun mouvement valide n'est trouvé

# Vérifier si un roque est possible
def can_castle(board, king_pos, end_pos, turn, castling_rights):
    start_row, start_col = king_pos
    end_row, end_col = end_pos
    if turn == 'w':
        if end_col == 6 and castling_rights['wK']:  # Roque petit
            if is_path_clear_for_castling(board, (7, 4), (7, 7)):  # Le chemin est-il dégagé ?
                return True
        if end_col == 2 and castling_rights['wQ']:  # Roque grand
            if is_path_clear_for_castling(board, (7, 4), (7, 0)):  # Le chemin est-il dégagé ?
                return True
    elif turn == 'b':
        if end_col == 6 and castling_rights['bK']:  # Roque petit
            if is_path_clear_for_castling(board, (0, 4), (0, 7)):  # Le chemin est-il dégagé ?
                return True
        if end_col == 2 and castling_rights['bQ']:  # Roque grand
            if is_path_clear_for_castling(board, (0, 4), (0, 0)):  # Le chemin est-il dégagé ?
                return True
    return False

# Vérification si le chemin est clair (pour les roques)
def is_path_clear_for_castling(board, start_pos, end_pos):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    step = 1 if end_col > start_col else -1

    # Parcourt les colonnes entre le roi et la tour pour vérifier si le chemin est vide
    for col in range(start_col + step, end_col, step):
        if board[start_row][col] != '--':
            return False
    return True


# Simulate a move on the board
def simulate_move(board, start_pos, end_pos):
    board_copy = [row[:] for row in board]
    board_copy[end_pos[0]][end_pos[1]] = board_copy[start_pos[0]][start_pos[1]]
    board_copy[start_pos[0]][start_pos[1]] = '--'
    return board_copy

# Main function
def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Chess')
    board = create_board()
    images = load_images()
    selected_piece = None
    turn = 'w'
    en_passant_possible = None  # Stocke la position éligible pour la prise en passant
    castling_rights = {'wK': True, 'wQ': True, 'bK': True, 'bQ': True}  # Roque possible
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
                    if is_valid_move(board, selected_piece, (row, col), turn, en_passant_possible, castling_rights):
                        piece = board[selected_piece[0]][selected_piece[1]]
                        board[row][col] = piece
                        board[selected_piece[0]][selected_piece[1]] = '--'

                        # Gérer la prise en passant
                        if piece[1] == 'P' and en_passant_possible and (row, col) == en_passant_possible:
                            # Supprimer le pion capturé
                            board[selected_piece[0]][col] = '--'

                        # Vérification si un pion a bougé de deux cases pour permettre la prise en passant
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
                            if selected_piece == (7, 0):  # Tour gauche blanche
                                castling_rights['wQ'] = False
                            elif selected_piece == (7, 7):  # Tour droite blanche
                                castling_rights['wK'] = False
                            elif selected_piece == (0, 0):  # Tour gauche noire
                                castling_rights['bQ'] = False
                            elif selected_piece == (0, 7):  # Tour droite noire
                                castling_rights['bK'] = False

                        turn = 'b' if turn == 'w' else 'w'  # Changement de tour après un coup valide
                    selected_piece = None
                else:
                    selected_piece = (row, col)

        draw_board(win)
        draw_pieces(win, board, images)
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
