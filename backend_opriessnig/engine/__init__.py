from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

from backend_opriessnig.config import Config
from backend_opriessnig.model import Base
from ._game_engine import GameEngine


def get_engine(config_file: str = "") -> Engine:
    config = Config.get_instance(config_file)
    engine_kwargs: dict[str, object] = {}
    if config.connection_string.startswith("sqlite"):
        engine_kwargs = {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }

    engine = create_engine(config.connection_string, **engine_kwargs)
    Base.metadata.create_all(engine)
    return engine


__all__ = ["get_engine", "GameEngine"]

