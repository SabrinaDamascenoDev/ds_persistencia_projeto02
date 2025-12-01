from sqlmodel import Relationship, SQLModel, Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.livro import Livro

from models.livro import LivroPost


class AdminBase(SQLModel):
    """
    Base para modelos relacionados ao Admin.

    Atributos:
        id (int | None): ID do administrador (gerado automaticamente no banco).
        nome (str): Nome do administrador.
        email (str): Endereço de e-mail do administrador.
    """
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    email: str


class Admin(AdminBase, table=True):
    """
    Modelo principal da tabela 'admins'.

    Representa um administrador que pode adicionar livros ao sistema.

    Relações:
        livros_adicionados (list[Livro] | None):
            Lista de livros adicionados por este admin.
    """
    __tablename__ = "admins"

    livros_adicionados: list["Livro"] | None = Relationship(
        back_populates="admin_criador"
    )


class AdminPost(SQLModel):
    """
    Modelo usado para criação de um novo Admin (POST).

    Atributos:
        nome (str): Nome do administrador.
        email (str): Email do administrador.
    """
    nome: str
    email: str


class AdminUpdate(SQLModel):
    """
    Modelo para atualização parcial de Admin (PUT/PATCH).

    Todos os campos são opcionais para permitir updates parciais.

    Atributos:
        nome (str | None): Novo nome (opcional).
        email (str | None): Novo email (opcional).
    """
    nome: str | None = None
    email: str | None = None


class AdminComLivrosAdicionados(AdminBase):
    """
    Modelo de resposta que inclui também os livros adicionados pelo Admin.

    Usado em endpoints GET.

    Atributos:
        livros_adicionados (list[LivroPost]):
            Dados dos livros cadastrados por este admin.
    """
    livros_adicionados: list[LivroPost]
