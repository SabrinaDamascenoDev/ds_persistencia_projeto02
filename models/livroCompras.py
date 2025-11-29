from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, UTC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.usuario import Usuario
    from models.livro import Livro


class LivrosCompras(SQLModel, table=True):
    __tablename__ = "livroscompras"

    usuario_id: int = Field(primary_key=True, foreign_key="usuarios.id")
    livro_id: int = Field(primary_key=True, foreign_key="livros.id")
    data_compra: datetime = Field(default_factory=lambda: datetime.now(UTC))
    preco_pago: float
    quantidade_comprados: int

    usuario: "Usuario" = Relationship(back_populates="livros_comprados")
    livro: "Livro" = Relationship(back_populates="compras")


class LivrosComprasPost(SQLModel):
    usuario_id: int
    livro_id: int
    preco_pago: float
    quantidade_comprados: int


class LivrosComprasRead(SQLModel):
    usuario_id: int
    livro_id: int
    preco_pago: float
    quantidade_comprados: int
    data_compra: datetime