from typing import Optional


class GameEngine:
    """TicTacToe game logic engine"""
    
    WINNING_COMBINATIONS = [
        # Rows
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        # Columns
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        # Diagonals
        [0, 4, 8],
        [2, 4, 6],
    ]

    @staticmethod
    def is_valid_move(board: list, position: int) -> bool:
        """Check if move at position is valid"""
        if position < 0 or position > 8:
            return False
        if board[position] is not None:
            return False
        return True

    @staticmethod
    def check_winner(board: list, player: str) -> bool:
        """Check if player has won"""
        for combo in GameEngine.WINNING_COMBINATIONS:
            if all(board[i] == player for i in combo):
                return True
        return False

    @staticmethod
    def is_board_full(board: list) -> bool:
        """Check if board is full (draw condition)"""
        return all(cell is not None for cell in board)

    @staticmethod
    def get_game_status(board: list) -> str:
        """Get current game status"""
        # Check X win
        if GameEngine.check_winner(board, "X"):
            return "won"
        # Check O win
        if GameEngine.check_winner(board, "O"):
            return "won"
        # Check draw
        if GameEngine.is_board_full(board):
            return "draw"
        # Game ongoing
        return "ongoing"

    @staticmethod
    def make_move(board: list, position: int, player: str) -> tuple[bool, str]:
        """
        Make a move on the board.
        Returns: (success: bool, message: str)
        """
        if not GameEngine.is_valid_move(board, position):
            return False, f"Invalid move: position {position} is not available"
        
        board[position] = player
        return True, f"Move successful: {player} played at position {position}"

    @staticmethod
    def get_next_player(current_player: str) -> str:
        """Get the next player to move"""
        return "O" if current_player == "X" else "X"
