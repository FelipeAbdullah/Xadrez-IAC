import pygame
import chess
import sys
import time
import math
import random

# Configurações do jogo
WIDTH, HEIGHT = 600, 600
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = HEIGHT
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 128)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
TIME_LIMIT = 10  # limite de tempo para IA pensar (segundos)

# Profundidade máxima da busca para evitar travamentos
MAX_DEPTH = 4

# Valores de peça simplificados
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

# Unicode para peças
UNICODE_PIECE = {
    'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
    'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'
}

# Inicialização do Pygame
pygame.init()
pygame.font.init()

def draw_game_state(screen, board, valid_moves=None, sq_selected=None):
    """Responsável por todo o desenho gráfico do estado atual do jogo."""
    draw_board(screen)  # desenha os quadrados
    highlight_squares(screen, board, valid_moves, sq_selected)  # destaca movimentos possíveis
    draw_pieces(screen, board)  # desenha as peças no tabuleiro


def draw_board(screen):
    """Desenha o tabuleiro."""
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlight_squares(screen, board, valid_moves, sq_selected):
    """Destaca o quadrado selecionado e movimentos válidos."""
    if sq_selected is not None:
        row, col = sq_selected
        # Destaca o quadrado selecionado
        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)  # transparência
        s.fill(pygame.Color('blue'))
        screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
        
        # Destaca movimentos válidos
        if valid_moves:
            for move in valid_moves:
                end_row = 7 - (move.to_square // 8)
                end_col = move.to_square % 8
                s.fill(pygame.Color('green'))
                screen.blit(s, (end_col * SQ_SIZE, end_row * SQ_SIZE))


def draw_pieces(screen, board):
    """Desenha as peças usando símbolos Unicode."""
    font_size = int(SQ_SIZE * 0.8)
    font = pygame.font.SysFont("DejaVu Sans", font_size)

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            square = chess.square(col, 7 - row)
            piece = board.piece_at(square)
            if piece:
                symbol = piece.symbol()
                glyph = UNICODE_PIECE[symbol]
                main_color = WHITE if symbol.isupper() else BLACK
                outline_color = BLACK if symbol.isupper() else WHITE
                center_x = col * SQ_SIZE + SQ_SIZE // 2
                center_y = row * SQ_SIZE + SQ_SIZE // 2

                # Desenha o contorno (renderiza em várias posições offset)
                offsets = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
                for dx, dy in offsets:
                    outline_text = font.render(glyph, True, outline_color)
                    outline_rect = outline_text.get_rect(center=(center_x + dx, center_y + dy))
                    screen.blit(outline_text, outline_rect)

                # Desenha a peça principal
                main_text = font.render(glyph, True, main_color)
                main_rect = main_text.get_rect(center=(center_x, center_y))
                screen.blit(main_text, main_rect)


def draw_move_log(screen, move_log, captured_white, captured_black):
    """Desenha painel de histórico e peças capturadas."""
    font = pygame.font.SysFont("Arial", 14, True, False)
    move_log_rect = pygame.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    pygame.draw.rect(screen, pygame.Color("black"), move_log_rect)

    temp_board = chess.Board()
    x, y = WIDTH + 5, 5
    cap_font = pygame.font.SysFont("DejaVu Sans", 24)

    # Peças capturadas de White (ou seja, peças brancas fora do tabuleiro)
    text = font.render("Capturadas (Brancas):", True, WHITE)
    screen.blit(text, (x, y))
    y += 20
    cap_text = cap_font.render("".join(UNICODE_PIECE[p] for p in captured_white), True, WHITE)
    screen.blit(cap_text, (x, y))

    y += 35
    text = font.render("Capturadas (Pretas):", True, WHITE)
    screen.blit(text, (x, y))
    y += 20
    cap_text = cap_font.render("".join(UNICODE_PIECE[p] for p in captured_black), True, WHITE)
    screen.blit(cap_text, (x, y))

    y += 40
    for i, move in enumerate(move_log):
        move_text = f"{(i//2)+1}. " if i % 2 == 0 else ""
        move_text += temp_board.san(move)
        temp_board.push(move)

        text = font.render(move_text, True, pygame.Color("white"))
        screen.blit(text, (x, y + i * 20))


def draw_end_game_text(screen, text):
    """Desenha a mensagem de fim de jogo na tela."""
    font = pygame.font.SysFont("Arial", 32, True, False)
    text_object = font.render(text, False, pygame.Color("white"))
    text_location = pygame.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH//2 - text_object.get_width()//2, 
        HEIGHT//2 - text_object.get_height()//2
    )
    screen.blit(text_object, text_location)
    
    # Adiciona instrução para reiniciar
    restart_font = pygame.font.SysFont("Arial", 16, True, False)
    restart_text = restart_font.render("Pressione R para reiniciar o jogo", False, pygame.Color("white"))
    restart_location = text_location.move(0, text_object.get_height() + 10)
    screen.blit(restart_text, restart_location)


def evaluate(board: chess.Board) -> int:
    """Avaliação simples baseada apenas em material. Pontuação positiva favorece as brancas."""

    # Condições terminais
    if board.is_checkmate():
        # O lado a jogar está em xeque-mate – logo, posição é perdida para ele.
        return -100000 if board.turn else 100000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for piece_type, value in PIECE_VALUES.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * value
        score -= len(board.pieces(piece_type, chess.BLACK)) * value
    return score


def alphabeta(
    board: chess.Board,
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
    start_time: float,
    time_limit: int,
):
    """Alpha-Beta recursivo. Retorna None se o tempo estourar."""

    # Controle de tempo
    if time.time() - start_time >= time_limit:
        return None

    if depth == 0 or board.is_game_over():
        return evaluate(board)

    if maximizing:
        max_eval = -math.inf
        for move in board.legal_moves:
            board.push(move)
            eval_ = alphabeta(board, depth - 1, alpha, beta, False, start_time, time_limit)
            board.pop()
            if eval_ is None:
                return None  # tempo esgotado
            max_eval = max(max_eval, eval_)
            alpha = max(alpha, eval_)
            if beta <= alpha:
                break  # poda beta
        return max_eval
    else:
        min_eval = math.inf
        for move in board.legal_moves:
            board.push(move)
            eval_ = alphabeta(board, depth - 1, alpha, beta, True, start_time, time_limit)
            board.pop()
            if eval_ is None:
                return None
            min_eval = min(min_eval, eval_)
            beta = min(beta, eval_)
            if beta <= alpha:
                break  # poda alfa
        return min_eval


def alphabeta_root(board: chess.Board, depth: int, start_time: float, time_limit: int):
    """Camada raiz do Alpha-Beta que devolve também o melhor lance encontrado."""

    maximizing = board.turn  # True se brancas a jogar
    best_move = None
    best_value = -math.inf if maximizing else math.inf

    for move in board.legal_moves:
        if time.time() - start_time >= time_limit:
            break
        board.push(move)
        value = alphabeta(board, depth - 1, -math.inf, math.inf, not maximizing, start_time, time_limit)
        board.pop()
        if value is None:
            break  # Estouro de tempo dentro da busca
        if maximizing and value > best_value:
            best_value = value
            best_move = move
        elif not maximizing and value < best_value:
            best_value = value
            best_move = move
    return best_value, best_move


def search_best_move(board: chess.Board, time_limit: int = TIME_LIMIT):
    """Iterative Deepening usando Alpha-Beta até esgotar o tempo."""

    start_time = time.time()
    depth = 1
    best_move = None

    while depth <= MAX_DEPTH:
        # Verifica tempo restante
        if time.time() - start_time >= time_limit:
            break
        value, move = alphabeta_root(board, depth, start_time, time_limit)
        if move is not None:
            best_move = move
        else:
            break  # tempo esgotado dentro da profundidade atual
        depth += 1
    return best_move


def get_chess_position(pos):
    """Converte posição do clique do mouse para posição no tabuleiro."""
    row = pos[1] // SQ_SIZE
    col = pos[0] // SQ_SIZE
    return row, col


def convert_to_chess_move(start_sq, end_sq, board):
    """Converte as coordenadas de tela em um movimento de xadrez."""
    start_row, start_col = start_sq
    end_row, end_col = end_sq
    
    # Converter para coordenadas chess
    from_square = chess.square(start_col, 7 - start_row)
    to_square = chess.square(end_col, 7 - end_row)
    
    # Verificar se é uma promoção
    move = chess.Move(from_square, to_square)
    if board.piece_at(from_square) and board.piece_at(from_square).piece_type == chess.PAWN:
        if (board.turn == chess.WHITE and end_row == 0) or (board.turn == chess.BLACK and end_row == 7):
            # Sempre promover para rainha
            move = chess.Move(from_square, to_square, promotion=chess.QUEEN)
    
    return move


def get_valid_moves(board, start_sq):
    """Obtém os movimentos válidos para a peça na posição start_sq."""
    row, col = start_sq
    square = chess.square(col, 7 - row)
    piece = board.piece_at(square)
    
    if piece and piece.color == board.turn:
        valid_moves = []
        for move in board.legal_moves:
            if move.from_square == square:
                valid_moves.append(move)
        return valid_moves
    return []


def main():
    # Inicializar tela e relógio
    screen = pygame.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    pygame.display.set_caption("Xadrez com IA Alpha-Beta")
    clock = pygame.time.Clock()
    
    # Inicializar tabuleiro
    board = chess.Board()
    
    # Sorteio para definir a cor do sistema
    system_color = random.choice([chess.WHITE, chess.BLACK])
    human_color = not system_color
    
    status_font = pygame.font.SysFont("Arial", 18, True, False)
    status_text = f"Você joga com as {'brancas' if human_color else 'pretas'}"
    
    # Inicializar variáveis de controle
    running = True
    sq_selected = None  # (row, col)
    player_clicks = []  # [(row, col), (row, col)]
    move_log = []
    captured_white = []  # peças brancas capturadas
    captured_black = []  # peças pretas capturadas
    game_over = False
    ai_thinking = False
    ai_move = None
    thinking_start_time = 0
    
    # Loop principal do jogo
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Manipulação de teclado
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:  # reinicia o jogo
                    board = chess.Board()
                    system_color = random.choice([chess.WHITE, chess.BLACK])
                    human_color = not system_color
                    status_text = f"Você joga com as {'brancas' if human_color else 'pretas'}"
                    sq_selected = None
                    player_clicks = []
                    move_log = []
                    captured_white = []
                    captured_black = []
                    game_over = False
                    
            # Manipulação de mouse
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                # Só processa o clique se for a vez do jogador humano
                if board.turn == human_color and not ai_thinking:
                    location = pygame.mouse.get_pos()
                    if location[0] < WIDTH:  # garante que o clique foi no tabuleiro
                        col = location[0] // SQ_SIZE
                        row = location[1] // SQ_SIZE
                        
                        # Se o mesmo quadrado for clicado duas vezes, desmarque o quadrado
                        if sq_selected == (row, col):
                            sq_selected = None
                            player_clicks = []
                        else:
                            sq_selected = (row, col)
                            player_clicks.append(sq_selected)
                        
                        # Se tivermos dois cliques, tente fazer o movimento
                        if len(player_clicks) == 2:
                            move = convert_to_chess_move(player_clicks[0], player_clicks[1], board)
                            if move in board.legal_moves:
                                # Verifica captura antes do push
                                captured_piece = board.piece_at(move.to_square)
                                if captured_piece:
                                    if captured_piece.color == chess.WHITE:
                                        captured_white.append(captured_piece.symbol())
                                    else:
                                        captured_black.append(captured_piece.symbol())
                                board.push(move)
                                move_log.append(move)
                                sq_selected = None
                                player_clicks = []
                            else:
                                player_clicks = [sq_selected]  # reset e começa com o último clique
        
        # IA faz seu movimento se for a vez dela
        if not game_over and board.turn == system_color and not ai_thinking:
            ai_thinking = True
            thinking_start_time = time.time()
        
        # Processar pensamento da IA
        if ai_thinking:
            current_time = time.time()
            if ai_move is None:
                # Mostra tempo de pensamento
                elapsed = current_time - thinking_start_time
                if elapsed < TIME_LIMIT:
                    status_text = f"IA pensando... {elapsed:.1f}s"
                    
                    # Se estivermos dentro do mesmo frame, adia cálculo pesado
                    if elapsed < 0.1:  # pequeno delay para atualizar a interface
                        ai_move = None
                    else:
                        ai_move = search_best_move(board, TIME_LIMIT)
                else:
                    # Tempo excedido
                    status_text = "IA demorou demais. Você venceu!"
                    game_over = True
                    ai_thinking = False
            else:
                # IA tomou decisão, executa o movimento
                if ai_move in board.legal_moves:
                    san_move = board.san(ai_move)
                    captured_piece = board.piece_at(ai_move.to_square)
                    if captured_piece:
                        if captured_piece.color == chess.WHITE:
                            captured_white.append(captured_piece.symbol())
                        else:
                            captured_black.append(captured_piece.symbol())
                    board.push(ai_move)
                    move_log.append(ai_move)
                    status_text = f"IA jogou: {san_move}"
                else:
                    status_text = "IA sugeriu movimento ilegal! IA perde."
                    game_over = True
                
                ai_thinking = False
                ai_move = None
        
        # Verificar condições de fim de jogo
        if not game_over and board.is_game_over():
            game_over = True
            if board.is_checkmate():
                winner = "Você" if board.turn != human_color else "IA"
                status_text = f"Xeque-mate! {winner} venceu."
            elif board.is_stalemate():
                status_text = "Empate por afogamento."
            elif board.is_insufficient_material():
                status_text = "Empate por material insuficiente."
            elif board.is_fifty_moves():
                status_text = "Empate pela regra dos 50 lances."
            elif board.is_repetition():
                status_text = "Empate por repetição."
        
        # Renderização
        screen.fill(pygame.Color("black"))
        valid_moves = get_valid_moves(board, sq_selected) if sq_selected else None
        draw_game_state(screen, board, valid_moves, sq_selected)
        draw_move_log(screen, move_log, captured_white, captured_black)
        
        # Desenhar status do jogo
        status_obj = status_font.render(status_text, True, WHITE)
        screen.blit(status_obj, (10, HEIGHT - 30))
        
        if game_over:
            draw_end_game_text(screen, status_text)
        
        pygame.display.flip()
        clock.tick(MAX_FPS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        print("\nJogo interrompido.")
