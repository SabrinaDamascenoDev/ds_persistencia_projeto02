from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Integer
from datetime import datetime, UTC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.usuario import Usuario
    from models.livro import Livro


class LivrosCompras(SQLModel, table=True):
    __tablename__ = "livroscompras"

    # MUDANÇA AQUI: usar sa_column ao invés de sa_column_kwargs
    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )
    usuario_id: int = Field(foreign_key="usuarios.id")
    livro_id: int = Field(foreign_key="livros.id")
    data_compra: datetime = Field(default_factory=datetime.now)
    preco_pago: float
    quantidade_comprados: int

    usuario: "Usuario" = Relationship(back_populates="livros_comprados")
    livro: "Livro" = Relationship(back_populates="compras")


class LivrosComprasPost(SQLModel):
    usuario_id: int
    livro_id: int
    quantidade_comprados: int


class LivrosComprasRead(SQLModel):
    usuario_id: int
    livro_id: int
    preco_pago: float
    quantidade_comprados: int
    data_compra: datetime


class LivrosComprasResponse(SQLModel):
    id: int
    usuario_id: int
    livro_id: int
    data_compra: datetime
    preco_pago: float
    quantidade_comprados: int