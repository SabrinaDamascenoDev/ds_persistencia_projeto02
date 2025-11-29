from sqlmodel import Relationship, SQLModel, Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.livro import Livro


class AdminBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    email: str

class Admin(AdminBase, table=True):
    __tablename__ = "admins"
    livros_adicionados: list["Livro"] | None = Relationship(back_populates="admin_criador")

class AdminPost(SQLModel):
    nome: str
    email: str