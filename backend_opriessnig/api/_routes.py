from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer

from backend_opriessnig.crud._crud import Crud
from backend_opriessnig.engine import GameEngine, get_engine
from backend_opriessnig.model import User
from backend_opriessnig.schema import GameFull, TokenResponse, UserLogin, UserRegister
from backend_opriessnig.service import AuthService


def define_routes(app: FastAPI) -> None:
    engine = get_engine()
    crud = Crud(engine)
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

    def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
        token_data = AuthService.verify_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = crud.get_user_by_name(token_data.user_name)
        if not user or user.entity_id != token_data.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    def create_token_response(user: User) -> TokenResponse:
        token = AuthService.create_access_token(
            {"sub": user.user_name, "user_id": user.entity_id}
        )
        return TokenResponse(
            access_token=token,
            user_name=user.user_name,
            user_id=user.entity_id,
        )

    @app.get("/", tags=["Root"])
    def get_root():
        return {
            "message": "TicTacToe Game API",
            "version": "1.0.0",
            "endpoints": {
                "register": "POST /auth/register",
                "login": "POST /auth/token",
                "create_game": "POST /games",
                "get_all_games": "GET /games",
                "get_game": "GET /games/{game_id}",
                "make_move": "PUT /games/{game_id}/move/{position} (position 1-9)",
                "delete_game": "DELETE /games/{game_id}",
                "play": "GET /play (browser UI)",
                "docs": "/docs (Swagger UI)",
                "redoc": "/redoc (ReDoc)",
            },
        }

    @app.get("/play", response_class=HTMLResponse, tags=["UI"], summary="Open the playable TicTacToe UI")
    def play_page():
        return HTMLResponse(
            """<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>TicTacToe Play</title>
  <style>
    :root {
      color-scheme: dark;
      --panel: rgba(14, 21, 36, 0.94);
      --border: rgba(148, 163, 184, 0.18);
      --text: #e5eefc;
      --muted: #9bb0d1;
      --accent: #7dd3fc;
      --accent-strong: #38bdf8;
      --danger: #fb7185;
      --success: #4ade80;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Segoe UI", Arial, sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(56, 189, 248, 0.16), transparent 28%),
        radial-gradient(circle at bottom right, rgba(59, 130, 246, 0.14), transparent 26%),
        linear-gradient(135deg, #040816 0%, #0a1631 55%, #111827 100%);
      display: grid;
      place-items: center;
      padding: 24px;
    }

    .shell {
      width: min(960px, 100%);
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 20px;
    }

    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 24px;
      box-shadow: 0 24px 80px rgba(2, 6, 23, 0.44);
      backdrop-filter: blur(16px);
    }

    h1 {
      margin: 0 0 12px;
      font-size: clamp(2.4rem, 5vw, 4.2rem);
      line-height: 0.95;
    }

    p {
      color: var(--muted);
      line-height: 1.6;
    }

    .status {
      margin-top: 18px;
      padding: 14px 16px;
      border: 1px solid var(--border);
      border-radius: 16px;
      background: rgba(15, 23, 42, 0.72);
    }

    .board {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin-top: 20px;
    }

    .cell {
      aspect-ratio: 1;
      border-radius: 18px;
      border: 1px solid rgba(148, 163, 184, 0.2);
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(2, 6, 23, 0.96));
      color: var(--text);
      font-size: clamp(2rem, 5vw, 3rem);
      font-weight: 700;
      cursor: pointer;
    }

    .cell:disabled {
      cursor: not-allowed;
      opacity: 0.92;
    }

    .side {
      display: grid;
      gap: 12px;
      align-content: start;
    }

    .button {
      width: 100%;
      border: 0;
      border-radius: 14px;
      padding: 14px 16px;
      font-weight: 700;
      cursor: pointer;
      color: #07111f;
      background: linear-gradient(135deg, var(--accent), var(--accent-strong));
    }

    .button.secondary {
      background: rgba(15, 23, 42, 0.85);
      color: var(--text);
      border: 1px solid rgba(148, 163, 184, 0.16);
    }

    .meta {
      display: grid;
      gap: 8px;
      padding: 14px 16px;
      border-radius: 16px;
      background: rgba(15, 23, 42, 0.72);
      border: 1px solid var(--border);
      color: var(--muted);
    }

    code {
      color: var(--text);
      word-break: break-word;
    }

    #message {
      min-height: 1.5em;
    }

    #message.success { color: var(--success); }
    #message.error { color: var(--danger); }

    @media (max-width: 840px) {
      .shell { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="card">
      <h1>TicTacToe</h1>
      <p>Quick Start registriert einen Demo-User, erstellt ein Spiel und speichert Token und Spielstand im Browser.</p>
      <div id="headline" class="status">Ready to start</div>
      <div id="detail" class="status">Click Quick Start to begin.</div>
      <div class="board" id="board">
        <button class="cell" data-position="1"></button>
        <button class="cell" data-position="2"></button>
        <button class="cell" data-position="3"></button>
        <button class="cell" data-position="4"></button>
        <button class="cell" data-position="5"></button>
        <button class="cell" data-position="6"></button>
        <button class="cell" data-position="7"></button>
        <button class="cell" data-position="8"></button>
        <button class="cell" data-position="9"></button>
      </div>
    </section>
    <aside class="card side">
      <button class="button" id="quickStart">Quick Start</button>
      <button class="button secondary" id="newGame">New Game</button>
      <button class="button secondary" id="resetSession">Reset Session</button>
      <div class="meta">
        <div>User: <code id="userName">-</code></div>
        <div>Game: <code id="gameId">-</code></div>
        <div>Token: <code id="tokenState">not set</code></div>
      </div>
      <div id="message"></div>
    </aside>
  </main>
  <script>
    const state = {
      token: localStorage.getItem("ttt_token") || "",
      userName: localStorage.getItem("ttt_user_name") || "-",
      userId: localStorage.getItem("ttt_user_id") || "",
      gameId: localStorage.getItem("ttt_game_id") || "",
      game: null,
    };

    const boardButtons = [...document.querySelectorAll(".cell")];
    const headline = document.getElementById("headline");
    const detail = document.getElementById("detail");
    const userName = document.getElementById("userName");
    const gameId = document.getElementById("gameId");
    const tokenState = document.getElementById("tokenState");
    const message = document.getElementById("message");

    const persist = () => {
      if (state.token) {
        localStorage.setItem("ttt_token", state.token);
        localStorage.setItem("ttt_user_name", state.userName);
        localStorage.setItem("ttt_user_id", String(state.userId));
      }
      if (state.gameId) {
        localStorage.setItem("ttt_game_id", String(state.gameId));
      }
    };

    const clear = () => {
      state.token = "";
      state.userName = "-";
      state.userId = "";
      state.gameId = "";
      state.game = null;
      localStorage.removeItem("ttt_token");
      localStorage.removeItem("ttt_user_name");
      localStorage.removeItem("ttt_user_id");
      localStorage.removeItem("ttt_game_id");
    };

    const show = (text, kind = "") => {
      message.textContent = text;
      message.className = kind;
    };

    const api = async (path, options = {}) => {
      const headers = { ...(options.headers || {}) };
      if (options.body) {
        headers["Content-Type"] = "application/json";
      }
      if (state.token) {
        headers.Authorization = `Bearer ${state.token}`;
      }

      const response = await fetch(path, { ...options, headers });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload.detail || `Request failed (${response.status})`);
      }
      return payload;
    };

    const render = (game = state.game) => {
      const board = game?.board || Array(9).fill(null);
      const status = game?.status || "idle";

      boardButtons.forEach((button, index) => {
        button.textContent = board[index] || "";
        button.disabled = !game || status !== "ongoing" || board[index] !== null;
      });

      userName.textContent = state.userName || "-";
      gameId.textContent = state.gameId || "-";
      tokenState.textContent = state.token ? "set" : "not set";

      if (!game) {
        headline.textContent = "Ready to start";
        detail.textContent = "Click Quick Start to register a demo user and create a game.";
      } else if (status === "won") {
        headline.textContent = `Player ${game.winner} wins`;
        detail.textContent = "Use New Game to play again.";
      } else if (status === "draw") {
        headline.textContent = "Draw";
        detail.textContent = "The board is full. Create a new game.";
      } else {
        headline.textContent = `Turn: ${game.current_player}`;
        detail.textContent = `Game ${state.gameId} is active.`;
      }
    };

    const loadGame = async () => {
      if (!state.token || !state.gameId) {
        return;
      }

      try {
        state.game = await api(`/games/${state.gameId}`);
        render();
        show("Saved game restored.", "success");
      } catch (error) {
        clear();
        render();
        show("Saved session expired. Start a new game.", "error");
      }
    };

    const quickStart = async () => {
      try {
        const suffix = Math.random().toString(36).slice(2, 8);
        const credentials = {
          user_name: `player_${suffix}`,
          password: "secret123",
          name: "Demo Player",
        };

        const tokenResponse = await api("/auth/register", {
          method: "POST",
          body: JSON.stringify(credentials),
        });

        state.token = tokenResponse.access_token;
        state.userName = tokenResponse.user_name;
        state.userId = tokenResponse.user_id;
        state.game = await api("/games", { method: "POST" });
        state.gameId = String(state.game.id);
        persist();
        render();
        show("Game created. You are X.", "success");
      } catch (error) {
        show(error.message, "error");
      }
    };

    const newGame = async () => {
      if (!state.token) {
        return show("Start a demo session first.", "error");
      }

      try {
        state.game = await api("/games", { method: "POST" });
        state.gameId = String(state.game.id);
        persist();
        render();
        show("New game created.", "success");
      } catch (error) {
        show(error.message, "error");
      }
    };

    const playMove = async (position) => {
      if (!state.token || !state.gameId) {
        return show("Start a game first.", "error");
      }

      try {
        state.game = await api(`/games/${state.gameId}/move/${position}`, { method: "PUT" });
        render();
        show(
          state.game.status === "won"
            ? `Player ${state.game.winner} wins.`
            : state.game.status === "draw"
              ? "Game ended in a draw."
              : `Next turn: ${state.game.current_player}`,
          "success"
        );
      } catch (error) {
        show(error.message, "error");
      }
    };

    document.getElementById("quickStart").addEventListener("click", quickStart);
    document.getElementById("newGame").addEventListener("click", newGame);
    document.getElementById("resetSession").addEventListener("click", () => {
      clear();
      render();
      show("Session cleared.");
    });
    boardButtons.forEach((button) => {
      button.addEventListener("click", () => playMove(button.dataset.position));
    });

    render();
    loadGame();
  </script>
</body>
</html>
""",
        )

    @app.post(
        "/auth/register",
        response_model=TokenResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["Auth"],
        summary="Register a new user",
    )
    def register_user(payload: UserRegister):
        existing_user = crud.get_user_by_name(payload.user_name)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {payload.user_name} already exists",
            )

        user = crud.create_user(
            user_name=payload.user_name,
            password=payload.password,
            name=payload.name,
        )
        return create_token_response(user)

    @app.post(
        "/auth/token",
        response_model=TokenResponse,
        tags=["Auth"],
        summary="Login and obtain a bearer token",
    )
    def login_user(payload: UserLogin):
        user = crud.get_user_by_name(payload.user_name)
        if not user or not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not AuthService.verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return create_token_response(user)

    @app.post(
        "/games",
        response_model=GameFull,
        status_code=status.HTTP_201_CREATED,
        tags=["Games"],
        summary="Create a new game",
    )
    def create_game(current_user: User = Depends(get_current_user)):
        try:
            return crud.create_game(user_id=current_user.entity_id)
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating game: {str(error)}",
            )

    @app.get(
        "/games",
        response_model=list[GameFull],
        tags=["Games"],
        summary="Get all games",
    )
    def get_all_games(current_user: User = Depends(get_current_user)):
        try:
            return crud.get_all_games(user_id=current_user.entity_id)
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving games: {str(error)}",
            )

    @app.get(
        "/games/{game_id}",
        response_model=GameFull,
        tags=["Games"],
        summary="Get a specific game",
    )
    def get_game(game_id: int, current_user: User = Depends(get_current_user)):
        try:
            game = crud.get_game(game_id=game_id)
            if not game or game.user_id != current_user.entity_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game {game_id} not found",
                )
            return game
        except HTTPException:
            raise
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving game: {str(error)}",
            )

    @app.put(
        "/games/{game_id}/move/{position}",
        response_model=GameFull,
        tags=["Games"],
        summary="Make a move in a game",
    )
    def make_move(game_id: int, position: int, current_user: User = Depends(get_current_user)):
        try:
            if position < 1 or position > 9:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid position: {position}. Position must be between 1 and 9.",
                )

            board_index = position - 1
            game = crud.get_game(game_id=game_id)
            if not game or game.user_id != current_user.entity_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game {game_id} not found",
                )

            if game.status != "ongoing":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Game is not ongoing (status: {game.status})",
                )

            if not GameEngine.is_valid_move(game.board, board_index):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Position {position} is already occupied",
                )

            success, message = GameEngine.make_move(game.board, board_index, game.current_player)
            if not success:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

            game.moves.append({"position": position, "player": game.current_player})

            new_status = GameEngine.get_game_status(game.board)
            winner = game.current_player if new_status == "won" else None
            next_player = GameEngine.get_next_player(game.current_player)

            updated_game = crud.update_game(
                game_id=game_id,
                board=game.board,
                status=new_status,
                winner=winner,
                current_player=next_player,
                moves=game.moves,
            )

            if not updated_game:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error updating game",
                )

            return updated_game
        except HTTPException:
            raise
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error making move: {str(error)}",
            )

    @app.delete(
        "/games/{game_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        tags=["Games"],
        summary="Delete a game",
    )
    def delete_game(game_id: int, current_user: User = Depends(get_current_user)):
        try:
            game = crud.get_game(game_id=game_id)
            if not game or game.user_id != current_user.entity_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game {game_id} not found",
                )

            if game.status == "ongoing":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only completed games can be deleted",
                )

            if not crud.delete_game(game_id=game_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game {game_id} not found",
                )
            return None
        except HTTPException:
            raise
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting game: {str(error)}",
            )