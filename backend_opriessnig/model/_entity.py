from typing import override

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ._base import Base


class Entity(Base):
    """Base table for joined-table inheritance used by Entity-derived models."""

    __tablename__: str = "entities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=255))
    type: Mapped[str] = mapped_column(String())

    @override
    def __repr__(self) -> str:
        return f"Entity(id={self.id}, name='{self.name}')"

    # `polymorphic_on` drives runtime subtype resolution for joined inheritance.
    __mapper_args__: dict[str, str] = {
        "polymorphic_identity": "entities",
        "polymorphic_on": "type",
    }


