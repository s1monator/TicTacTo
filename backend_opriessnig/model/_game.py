from typing import override
from datetime import datetime

from sqlalchemy import String, Integer, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from ._base import Base


class Game(Base):
    __tablename__: str = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    board: Mapped[list] = mapped_column(JSON, default=lambda: [None] * 9)
    status: Mapped[str] = mapped_column(String(20), default="ongoing")  # ongoing, won, draw
    winner: Mapped[str | None] = mapped_column(String(1), nullable=True)  # 'X' or 'O'
    current_player: Mapped[str] = mapped_column(String(1), default="X")  # 'X' or 'O'
    moves: Mapped[list] = mapped_column(JSON, default=list)  # List of moves: [{"position": 0, "player": "X"}]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @override
    def __repr__(self) -> str:
        return f"Game(id={self.id}, user_id={self.user_id}, status='{self.status}', current_player='{self.current_player}')"

    __mapper_args__: dict[str, str] = {
        "polymorphic_identity": "games",
    }
