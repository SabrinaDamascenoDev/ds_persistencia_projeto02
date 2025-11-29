from sqlmodel import Relationship, SQLModel, Field

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.livroCompras import LivrosCompras

class UsuarioBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    email: str
    endereco: str
    telefone: str

class Usuario(UsuarioBase, table=True):
    __tablename__ = "usuarios"
    livros_comprados: list["LivrosCompras"] = Relationship(back_populates="usuario")

class UsuarioPost(SQLModel):
    nome: str
    email: str
    endereco: str
    telefone: str