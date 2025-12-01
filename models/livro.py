from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from models.admin import Admin
    from models.livroCompras import LivrosCompras

from models.livroCompras import LivrosComprasRead


class LivroBase(SQLModel):
    """
    Modelo base para representar um livro.

    Atributos:
        id (int | None): ID do livro (gerado automaticamente no banco).
        titulo (str): Título do livro.
        autor (str): Nome do autor.
        quantidade_paginas (int): Quantidade total de páginas.
        editora (str): Nome da editora responsável.
        genero (str): Gênero literário.
        quantidade_estoque (int): Quantidade disponível em estoque.
        preco_uni (float): Preço unitário do livro.
    """
    id: int | None = Field(default=None, primary_key=True)
    titulo: str
    autor: str
    quantidade_paginas: int
    editora: str
    genero: str
    quantidade_estoque: int
    preco_uni: float


class Livro(LivroBase, table=True):
    """
    Modelo principal da tabela 'livros'.

    Representa um livro completo armazenado no banco e suas relações.

    Atributos:
        admin_id (int): ID do administrador responsável pelo cadastro.
        admin_criador (Admin): Relação com o Admin que cadastrou o livro.
        compras (list[LivrosCompras] | None): Lista de compras realizadas deste livro.
    """
    __tablename__ = "livros"

    admin_id: int = Field(default=None, foreign_key="admins.id")
    admin_criador: "Admin" = Relationship(back_populates="livros_adicionados")
    compras: list["LivrosCompras"] | None = Relationship(back_populates="livro")


class LivroUpdate(SQLModel):
    """
    Modelo para atualização parcial de um livro.

    Todos os campos são opcionais, permitindo atualizar apenas o que for necessário.

    Atributos:
        titulo (str | None): Novo título.
        autor (str | None): Novo autor.
        quantidade_paginas (int | None): Nova quantidade de páginas.
        editora (str | None): Nova editora.
        genero (str | None): Novo gênero.
        quantidade_estoque (int | None): Novo estoque.
        preco_uni (float | None): Novo preço.
    """
    titulo: str | None = None
    autor: str | None = None
    quantidade_paginas: int | None = None
    editora: str | None = None
    genero: str | None = None
    quantidade_estoque: int | None = None
    preco_uni: float | None = None


class LivroPost(SQLModel):
    """
    Modelo utilizado para criação de um novo livro (POST).

    Atributos:
        titulo (str): Título do livro.
        autor (str): Nome do autor.
        quantidade_paginas (int): Número de páginas.
        editora (str): Editora responsável.
        genero (str): Gênero do livro.
        quantidade_estoque (int): Estoque inicial.
        preco_uni (float): Preço unitário.
        admin_id (int): ID do administrador que cadastrou o livro.
    """
    titulo: str
    autor: str
    quantidade_paginas: int
    editora: str
    genero: str
    quantidade_estoque: int
    preco_uni: float
    admin_id: int


class LivroComCompras(LivroBase):
    """
    Modelo de resposta que inclui também as compras associadas ao livro.

    Usado para endpoints GET que retornam o livro com informações relacionadas.

    Atributos:
        admin_id (int): ID do admin que cadastrou o livro.
        compras (list[LivrosComprasRead]): Lista de compras deste livro.
    """
    admin_id: int
    compras: list[LivrosComprasRead] = []
