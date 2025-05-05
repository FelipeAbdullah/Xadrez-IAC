import chess
import random
import time
import math
import sys

TIME_LIMIT = 120  # segundos para o motor responder

# Valores de peça simplificados
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}


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

    while True:
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


def ask_move(board: chess.Board) -> chess.Move:
    """Solicita e valida um movimento digitado pelo adversário."""

    while True:
        user_input = input("Seu movimento (ex: e2e4, Nf3 ou 'quit'): ").strip()
        if user_input.lower() in ("quit", "exit"):
            print("Jogo encerrado pelo usuário.")
            sys.exit(0)

        move = None
        try:
            if len(user_input) in (4, 5):
                move = chess.Move.from_uci(user_input)
            else:
                move = board.parse_san(user_input)
        except ValueError:
            pass

        if move is None or move not in board.legal_moves:
            print("Movimento ilegal – tente novamente.")
            continue
        return move


def main():
    board = chess.Board()
    # Sorteio para definir a cor do sistema
    system_color = random.choice([chess.WHITE, chess.BLACK])
    print("=== Jogo de Xadrez (IA − Alfa-Beta) ===")
    print(f"O sistema jogará com as {'brancas' if system_color else 'pretas'}.")
    print(board)

    while not board.is_game_over():
        # Vez da IA
        if board.turn == system_color:
            print("\nSistema pensando…")
            start = time.time()
            move = search_best_move(board, TIME_LIMIT)
            elapsed = time.time() - start

            if move is None:
                print("Tempo excedido (2 min). Sistema perde a partida!")
                return
            if move not in board.legal_moves:
                print("Sistema sugeriu movimento ilegal. Sistema perde a partida!")
                return

            san = board.san(move)
            board.push(move)
            print(f"Sistema joga: {san} (tempo: {elapsed:.1f}s)")
            print(board)
        else:  # Vez do adversário (usuário)
            move = ask_move(board)
            board.push(move)
            print(board)

    # --- Fim de jogo ---
    print("\n=== Resultado final ===")
    if board.is_checkmate():
        winner = "Sistema" if board.turn != system_color else "Você"
        print(f"Xeque-mate! {winner} venceu.")
    elif board.is_stalemate():
        print("Empate por afogamento.")
    elif board.is_insufficient_material():
        print("Empate – material insuficiente.")
    elif board.is_seventyfive_moves():
        print("Empate – regra dos 75 lances.")
    else:
        print("Jogo encerrado sem resultado conclusivo.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nJogo interrompido.")
