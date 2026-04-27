from sqlalchemy import Engine
from sqlalchemy.orm import Session

from backend_opriessnig.model import Entity, Person, User, Game
from backend_opriessnig.schema import EntityBase, GameCreate
from backend_opriessnig.service import AuthService


class Crud:
    def __init__(self, engine: Engine):
        self._engine: Engine = engine

    def get_users(self, filter: str | None = None) -> list[User]:
        if not filter:
            return []
        return []

    def get_persons(self, filter: str | None = None) -> list[Person]:
        if not filter:
            return []
        return []

    def get_entities(self, filter: str | None = None) -> list[Entity]:
        if not filter:
            return []
        return []

    def create_entity(self, new_entity: EntityBase):
        with Session(self._engine) as session:
            assert new_entity
            assert session

    def get_user_by_name(self, user_name: str) -> User | None:
        with Session(self._engine) as session:
            return session.query(User).filter(User.user_name == user_name).first()

    def create_user(self, user_name: str, password: str, name: str) -> User:
        with Session(self._engine) as session:
            entity = Entity(name=name, type="entities")
            session.add(entity)
            session.flush()

            user = User(
                user_name=user_name,
                entity_id=entity.id,
                password_hash=AuthService.hash_password(password),
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    # ===== GAME CRUD OPERATIONS =====

    def create_game(self, user_id: int) -> Game:
        """Create a new game"""
        with Session(self._engine) as session:
            new_game = Game(user_id=user_id)
            session.add(new_game)
            session.commit()
            session.refresh(new_game)
            return new_game

    def get_game(self, game_id: int) -> Game | None:
        """Get a game by ID"""
        with Session(self._engine) as session:
            game = session.query(Game).filter(Game.id == game_id).first()
            return game

    def get_all_games(self, user_id: int | None = None) -> list[Game]:
        """Get all games, optionally filtered by user"""
        with Session(self._engine) as session:
            query = session.query(Game)
            if user_id:
                query = query.filter(Game.user_id == user_id)
            games = query.all()
            return games

    def update_game(self, game_id: int, board: list, status: str, winner: str | None = None, 
                    current_player: str | None = None, moves: list | None = None) -> Game | None:
        """Update mutable game fields and persist them atomically.
        """
        with Session(self._engine) as session:
            game = session.query(Game).filter(Game.id == game_id).first()
            if not game:
                return None
            
            game.board = board
            game.status = status
            if winner is not None:
                game.winner = winner
            if current_player:
                game.current_player = current_player
            if moves:
                game.moves = moves
            
            session.commit()
            session.refresh(game)
            return game

    def delete_game(self, game_id: int) -> bool:
        """Delete a game"""
        with Session(self._engine) as session:
            game = session.query(Game).filter(Game.id == game_id).first()
            if not game:
                return False
            session.delete(game)
            session.commit()
            return True

