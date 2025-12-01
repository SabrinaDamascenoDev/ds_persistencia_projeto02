from sqlmodel import Relationship, SQLModel, Field
from typing import TYPE_CHECKING, List
from models.livroCompras import LivrosComprasRead

if TYPE_CHECKING:
    from models.livroCompras import LivrosCompras


class UsuarioBase(SQLModel):
    """
    Modelo base para representar um usuário.

    Atributos:
        id (int | None): ID do usuário (gerado automaticamente no banco).
        nome (str): Nome completo do usuário.
        email (str): Endereço de e-mail.
        endereco (str): Endereço residencial.
        telefone (str): Número de telefone para contato.
    """
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    email: str
    endereco: str
    telefone: str


class Usuario(UsuarioBase, table=True):
    """
    Modelo principal da tabela 'usuarios'.

    Representa um usuário completo armazenado no banco e suas relações.

    Atributos:
        livros_comprados (list[LivrosCompras]): Lista de compras realizadas pelo usuário.
    """
    __tablename__ = "usuarios"

    livros_comprados: list["LivrosCompras"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"lazy": "noload"}
    )


class UsuarioPost(SQLModel):
    """
    Modelo utilizado para criação de um novo usuário (POST).

    Atributos:
        nome (str): Nome completo do usuário.
        email (str): Endereço de e-mail.
        endereco (str): Endereço residencial.
        telefone (str): Número de telefone para contato.
    """
    nome: str
    email: str
    endereco: str
    telefone: str


class UsuarioComCompras(UsuarioBase):
    """
    Modelo de resposta que inclui também as compras associadas ao usuário.

    Usado para endpoints GET que retornam o usuário com informações de compras.

    Atributos:
        livros_comprados (list[LivrosComprasRead]): Lista de compras realizadas.
    """
    livros_comprados: list[LivrosComprasRead] = []


class UsuarioUpdate(SQLModel):
    """
    Modelo para atualização parcial de um usuário (PATCH).

    Todos os campos são opcionais, permitindo atualizar apenas o que for necessário.

    Atributos:
        nome (str | None): Novo nome.
        email (str | None): Novo e-mail.
        endereco (str | None): Novo endereço.
        telefone (str | None): Novo telefone.
    """
    nome: str | None = None
    email: str | None = None
    endereco: str | None = None
    telefone: str | None = None