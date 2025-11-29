from sqlmodel import Relationship, SQLModel, Field
from livro import LivroBase

class Admin(SQLModel, table=True):
    __tablename__ = "admins"
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    email: str
    livros_adicionados: list[LivroBase] = Relationship(back_populates=)