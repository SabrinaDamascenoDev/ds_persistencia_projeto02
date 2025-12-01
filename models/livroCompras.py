from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Integer
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.usuario import Usuario
    from models.livro import Livro


class LivrosCompras(SQLModel, table=True):
    """
    Modelo que representa uma compra de livros no sistema.

    Registra as transações de compra realizadas pelos usuários, incluindo
    informações sobre quantidade, preço pago e data da compra. Gerencia
    automaticamente a relação entre usuários e livros comprados.

    Atributos:
        id (int | None): Identificador único da compra (auto-incremento).
        usuario_id (int): ID do usuário que realizou a compra.
        livro_id (int): ID do livro comprado.
        data_compra (datetime): Data e hora da compra (gerada automaticamente).
        preco_pago (float): Valor total pago na compra.
        quantidade_comprados (int): Quantidade de livros comprados.
        usuario (Usuario): Relacionamento com o usuário que fez a compra.
        livro (Livro): Relacionamento com o livro comprado.
    """
    __tablename__ = "livroscompras"

    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )
    usuario_id: int = Field(foreign_key="usuarios.id")
    livro_id: int = Field(foreign_key="livros.id")
    data_compra: datetime = Field(default_factory=datetime.now)
    preco_pago: float
    quantidade_comprados: int

    usuario: "Usuario" = Relationship(
        back_populates="livros_comprados",
        sa_relationship_kwargs={"lazy": "noload"}
    )
    livro: "Livro" = Relationship(
        back_populates="compras",
        sa_relationship_kwargs={"lazy": "noload"}
    )


class LivrosComprasPost(SQLModel):
    """
    Modelo utilizado para criação de uma nova compra (POST).

    O preço total é calculado automaticamente pelo sistema com base
    no preço unitário do livro e na quantidade comprada.

    Atributos:
        usuario_id (int): ID do usuário que está realizando a compra.
        livro_id (int): ID do livro a ser comprado.
        quantidade_comprados (int): Quantidade de livros a comprar (deve ser maior que 0).
    """
    usuario_id: int
    livro_id: int
    quantidade_comprados: int = Field(gt=0)


class LivrosComprasRead(SQLModel):
    """
    Modelo de leitura de dados de compra (sem ID).

    Usado para retornar informações de compra sem expor o ID interno,
    útil em contextos onde apenas os dados da transação são relevantes.

    Atributos:
        usuario_id (int): ID do usuário que realizou a compra.
        livro_id (int): ID do livro comprado.
        preco_pago (float): Valor total pago.
        quantidade_comprados (int): Quantidade comprada.
        data_compra (datetime): Data e hora da compra.
    """
    usuario_id: int
    livro_id: int
    preco_pago: float
    quantidade_comprados: int
    data_compra: datetime


class LivrosComprasResponse(SQLModel):
    """
    Modelo de resposta completa de uma compra.

    Usado como response_model nos endpoints da API para retornar
    informações completas de uma compra, incluindo o ID.

    Atributos:
        id (int): ID único da compra.
        usuario_id (int): ID do usuário que realizou a compra.
        livro_id (int): ID do livro comprado.
        data_compra (datetime): Data e hora da compra.
        preco_pago (float): Valor total pago.
        quantidade_comprados (int): Quantidade comprada.
    """
    id: int
    usuario_id: int
    livro_id: int
    data_compra: datetime
    preco_pago: float
    quantidade_comprados: int