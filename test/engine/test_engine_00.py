from backend_opriessnig.engine import GameEngine


def test_is_valid_move_bounds_and_occupied_cells() -> None:
    board = [None] * 9
    board[0] = "X"

    assert GameEngine.is_valid_move(board, -1) is False
    assert GameEngine.is_valid_move(board, 9) is False
    assert GameEngine.is_valid_move(board, 0) is False
    assert GameEngine.is_valid_move(board, 1) is True


def test_check_winner_detects_rows_columns_and_diagonals() -> None:
    row_win = ["X", "X", "X", None, None, None, None, None, None]
    column_win = ["O", None, None, "O", None, None, "O", None, None]
    diagonal_win = ["X", None, None, None, "X", None, None, None, "X"]

    assert GameEngine.check_winner(row_win, "X") is True
    assert GameEngine.check_winner(column_win, "O") is True
    assert GameEngine.check_winner(diagonal_win, "X") is True


def test_get_game_status_returns_ongoing_draw_or_won() -> None:
    ongoing_board = ["X", None, None, None, None, None, None, None, None]
    draw_board = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
    won_board = ["X", "X", "X", None, "O", None, "O", None, None]

    assert GameEngine.get_game_status(ongoing_board) == "ongoing"
    assert GameEngine.get_game_status(draw_board) == "draw"
    assert GameEngine.get_game_status(won_board) == "won"


def test_make_move_mutates_board_and_rejects_invalid_move() -> None:
    board = [None] * 9

    success, message = GameEngine.make_move(board, 4, "X")
    assert success is True
    assert "successful" in message.lower()
    assert board[4] == "X"

    second_success, second_message = GameEngine.make_move(board, 4, "O")
    assert second_success is False
    assert "invalid" in second_message.lower()


def test_get_next_player_switches_between_x_and_o() -> None:
    assert GameEngine.get_next_player("X") == "O"
    assert GameEngine.get_next_player("O") == "X"
