from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from models.admin import Admin
    from models.livroCompras import LivrosCompras

from models.livroCompras import LivrosComprasRead

class LivroBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    titulo: str
    autor: str
    quantidade_paginas: int
    editora: str
    genero: str
    quantidade_estoque: int

class Livro(LivroBase, table=True):
    __tablename__ = "livros"
    admin_id: int = Field(default=None, foreign_key="admins.id")
    admin_criador: "Admin" = Relationship(back_populates="livros_adicionados")
    compras: list["LivrosCompras"] | None = Relationship(back_populates="livro")

class LivroUpdate(SQLModel):
    titulo: str | None = None
    autor: str | None = None
    quantidade_paginas: int | None = None
    editora: str | None = None
    genero: str | None = None
    quantidade_estoque: int | None = None

class LivroPost(SQLModel):
    titulo: str
    autor: str
    quantidade_paginas: int
    editora: str
    genero: str
    quantidade_estoque: int
    admin_id: int

class LivroComCompras(LivroBase):
    admin_id: int
    compras: List[LivrosComprasRead] = []  
