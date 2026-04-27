from pydantic import BaseModel
from datetime import datetime


class GameBase(BaseModel):
    user_id: int


class GameCreate(GameBase):
    pass


class GameMove(BaseModel):
    position: int  # 1-9


class GameFull(GameBase):
    id: int
    board: list
    status: str
    winner: str | None
    current_player: str
    moves: list 
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
