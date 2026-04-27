import uuid

import pytest
from fastapi.testclient import TestClient

from backend_opriessnig.api import build_app

@pytest.fixture
def client():
    """Create a test client."""
    app = build_app()
    return TestClient(app)


@pytest.fixture
def user_credentials():
    """Generate unique credentials for isolated test users."""
    suffix = uuid.uuid4().hex[:8]
    return {
        "user_name": f"tester_{suffix}",
        "password": "secret123",
        "name": "Test User",
    }


@pytest.fixture
def auth_headers(client, user_credentials):
    """Register a user and return a valid bearer auth header."""
    response = client.post("/auth/register", json=user_credentials)
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestGameAPI:
    """Integration tests for authentication and game endpoints."""

    def test_get_root(self, client):
        """Root endpoint returns API metadata and endpoint overview."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "TicTacToe Game API"

    def test_play_page(self, client):
        """Playable UI endpoint serves an HTML page."""
        response = client.get("/play")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "TicTacToe" in response.text

    def test_register_user(self, client, user_credentials):
        """Register endpoint creates a user and returns a bearer token."""
        response = client.post("/auth/register", json=user_credentials)
        assert response.status_code == 201
        data = response.json()
        assert data["user_name"] == user_credentials["user_name"]
        assert data["token_type"] == "bearer"
        assert data["access_token"]

    def test_login_user(self, client, user_credentials):
        """Login endpoint issues a bearer token for valid credentials."""
        client.post("/auth/register", json=user_credentials)

        response = client.post(
            "/auth/token",
            json={
                "user_name": user_credentials["user_name"],
                "password": user_credentials["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_name"] == user_credentials["user_name"]
        assert data["token_type"] == "bearer"

    def test_create_game_requires_auth(self, client):
        """Game creation is rejected when no auth token is provided."""
        response = client.post("/games")
        assert response.status_code == 401

    def test_create_game(self, client, auth_headers):
        """Creating a game initializes board, status, and current player."""
        response = client.post("/games", headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "ongoing"
        assert data["current_player"] == "X"
        assert len(data["board"]) == 9
        assert all(cell is None for cell in data["board"])

    def test_get_all_games(self, client, auth_headers):
        """List endpoint returns all games for the authenticated user."""
        client.post("/games", headers=auth_headers)
        client.post("/games", headers=auth_headers)

        response = client.get("/games", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_get_game_by_id(self, client, auth_headers):
        """Fetching an existing game by ID returns its current state."""
        create_response = client.post("/games", headers=auth_headers)
        game_id = create_response.json()["id"]

        response = client.get(f"/games/{game_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == game_id
        assert data["status"] == "ongoing"

    def test_get_game_not_found(self, client, auth_headers):
        """Fetching a missing game ID returns 404."""
        response = client.get("/games/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_make_move_success(self, client, auth_headers):
        """Valid move updates board, switches player, and records the move."""
        create_response = client.post("/games", headers=auth_headers)
        game_id = create_response.json()["id"]

        response = client.put(f"/games/{game_id}/move/1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["board"][0] == "X"
        assert data["current_player"] == "O"
        assert len(data["moves"]) == 1
        assert data["moves"][0]["position"] == 1

    def test_make_move_invalid_position_out_of_bounds(self, client, auth_headers):
        """Move endpoint rejects positions outside the supported 1-9 range."""
        create_response = client.post("/games", headers=auth_headers)
        game_id = create_response.json()["id"]

        response = client.put(f"/games/{game_id}/move/10", headers=auth_headers)
        assert response.status_code == 400
        assert "Invalid position" in response.json()["detail"]

    def test_make_move_occupied_position(self, client, auth_headers):
        """Move endpoint rejects selecting an already occupied cell."""
        create_response = client.post("/games", headers=auth_headers)
        game_id = create_response.json()["id"]

        client.put(f"/games/{game_id}/move/1", headers=auth_headers)
        response = client.put(f"/games/{game_id}/move/1", headers=auth_headers)
        assert response.status_code == 400
        assert "occupied" in response.json()["detail"].lower()

    def test_make_move_game_not_found(self, client, auth_headers):
        """Move endpoint returns 404 when the game ID does not exist."""
        response = client.put("/games/99999/move/1", headers=auth_headers)
        assert response.status_code == 404

    def test_win_detection_x(self, client, auth_headers):
        """A winning move sets game status to won and winner to X."""
        create_response = client.post("/games", headers=auth_headers)
        game_id = create_response.json()["id"]

        client.put(f"/games/{game_id}/move/1", headers=auth_headers)
        client.put(f"/games/{game_id}/move/4", headers=auth_headers)
        client.put(f"/games/{game_id}/move/2", headers=auth_headers)
        client.put(f"/games/{game_id}/move/5", headers=auth_headers)
        response = client.put(f"/games/{game_id}/move/3", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "won"
        assert data["winner"] == "X"

    def test_draw_game(self, client, auth_headers):
        """A full board without winner sets game status to draw."""
        create_response = client.post("/games", headers=auth_headers)
        game_id = create_response.json()["id"]

        positions = [1, 2, 3, 5, 4, 6, 9, 7, 8]
        for position in positions[:-1]:
            client.put(f"/games/{game_id}/move/{position}", headers=auth_headers)

        response = client.put(f"/games/{game_id}/move/{positions[-1]}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "draw"
        assert all(cell is not None for cell in data["board"])

    def test_cannot_move_on_finished_game(self, client, auth_headers):
        """Further moves are blocked once a game is no longer ongoing."""
        create_response = client.post("/games", headers=auth_headers)
        game_id = create_response.json()["id"]

        client.put(f"/games/{game_id}/move/1", headers=auth_headers)
        client.put(f"/games/{game_id}/move/4", headers=auth_headers)
        client.put(f"/games/{game_id}/move/2", headers=auth_headers)
        client.put(f"/games/{game_id}/move/5", headers=auth_headers)
        client.put(f"/games/{game_id}/move/3", headers=auth_headers)

        response = client.put(f"/games/{game_id}/move/6", headers=auth_headers)
        assert response.status_code == 400
        assert "not ongoing" in response.json()["detail"].lower()

    def test_delete_completed_game(self, client, auth_headers):
        """Completed games can be deleted and are no longer retrievable."""
        create_response = client.post("/games", headers=auth_headers)
        game_id = create_response.json()["id"]

        client.put(f"/games/{game_id}/move/1", headers=auth_headers)
        client.put(f"/games/{game_id}/move/4", headers=auth_headers)
        client.put(f"/games/{game_id}/move/2", headers=auth_headers)
        client.put(f"/games/{game_id}/move/5", headers=auth_headers)
        client.put(f"/games/{game_id}/move/3", headers=auth_headers)

        response = client.delete(f"/games/{game_id}", headers=auth_headers)
        assert response.status_code == 204

        response = client.get(f"/games/{game_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_cannot_delete_ongoing_game(self, client, auth_headers):
        """Ongoing games cannot be deleted."""
        create_response = client.post("/games", headers=auth_headers)
        game_id = create_response.json()["id"]

        response = client.delete(f"/games/{game_id}", headers=auth_headers)
        assert response.status_code == 400
        assert "completed" in response.json()["detail"].lower()

    def test_register_duplicate_user_conflict(self, client, user_credentials):
        """Registering an existing username is rejected with 409."""
        first_response = client.post("/auth/register", json=user_credentials)
        assert first_response.status_code == 201

        second_response = client.post("/auth/register", json=user_credentials)
        assert second_response.status_code == 409
        assert "already exists" in second_response.json()["detail"].lower()

    def test_login_invalid_password_rejected(self, client, user_credentials):
        """Login fails with 401 when password does not match stored hash."""
        register_response = client.post("/auth/register", json=user_credentials)
        assert register_response.status_code == 201

        response = client.post(
            "/auth/token",
            json={
                "user_name": user_credentials["user_name"],
                "password": "wrong-password",
            },
        )
        assert response.status_code == 401
        assert "invalid username or password" in response.json()["detail"].lower()

    def test_games_endpoint_rejects_invalid_token(self, client):
        """Protected game endpoints reject malformed bearer tokens."""
        response = client.get("/games", headers={"Authorization": "Bearer not-a-valid-token"})
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_user_cannot_access_other_users_game(self, client):
        """Game endpoints enforce ownership and hide foreign games as not found."""
        owner_credentials = {
            "user_name": f"owner_{uuid.uuid4().hex[:8]}",
            "password": "secret123",
            "name": "Owner",
        }
        intruder_credentials = {
            "user_name": f"intruder_{uuid.uuid4().hex[:8]}",
            "password": "secret123",
            "name": "Intruder",
        }

        owner_register = client.post("/auth/register", json=owner_credentials)
        intruder_register = client.post("/auth/register", json=intruder_credentials)
        assert owner_register.status_code == 201
        assert intruder_register.status_code == 201

        owner_headers = {
            "Authorization": f"Bearer {owner_register.json()['access_token']}"
        }
        intruder_headers = {
            "Authorization": f"Bearer {intruder_register.json()['access_token']}"
        }

        game_response = client.post("/games", headers=owner_headers)
        assert game_response.status_code == 201
        game_id = game_response.json()["id"]

        # Foreign users should not be able to discover or mutate the game.
        get_response = client.get(f"/games/{game_id}", headers=intruder_headers)
        assert get_response.status_code == 404

        move_response = client.put(f"/games/{game_id}/move/1", headers=intruder_headers)
        assert move_response.status_code == 404

        # Finish game as owner to validate delete-authorization separately from "ongoing" rule.
        client.put(f"/games/{game_id}/move/1", headers=owner_headers)
        client.put(f"/games/{game_id}/move/4", headers=owner_headers)
        client.put(f"/games/{game_id}/move/2", headers=owner_headers)
        client.put(f"/games/{game_id}/move/5", headers=owner_headers)
        final_move = client.put(f"/games/{game_id}/move/3", headers=owner_headers)
        assert final_move.status_code == 200
        assert final_move.json()["status"] == "won"

        delete_response = client.delete(f"/games/{game_id}", headers=intruder_headers)
        assert delete_response.status_code == 404
