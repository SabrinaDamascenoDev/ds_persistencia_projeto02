from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from database import get_session
from models.livro import Livro, LivroPost, LivroUpdate
from models.livroCompras import LivrosCompras
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/livros")

@router.get("/buscar")
async def buscar_livros(
    titulo: str | None = None,
    autor: str | None = None,
    preco_min: float | None = None,
    preco_max: float | None = None,
    estoque_menor_que: int | None = None,
    ordenar_por: str | None = Query(None, enum=["preco", "titulo", "estoque"]),
    session=Depends(get_session)
):
    try:
        query = select(Livro)

        if titulo:
            query = query.where(Livro.titulo.ilike(f"%{titulo}%"))

        if autor:
            query = query.where(Livro.autor.ilike(f"%{autor}%"))

        if preco_min is not None:
            query = query.where(Livro.preco_uni >= preco_min)

        if preco_max is not None:
            query = query.where(Livro.preco_uni <= preco_max)

        if estoque_menor_que is not None:
            query = query.where(Livro.quantidade_estoque < estoque_menor_que)

        if ordenar_por == "preco":
            query = query.order_by(Livro.preco_uni)
        elif ordenar_por == "titulo":
            query = query.order_by(Livro.titulo)
        elif ordenar_por == "estoque":
            query = query.order_by(Livro.quantidade_estoque)

        result = await session.exec(query)
        livros = result.all()

        return {"resultado": livros}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Erro ao buscar livros")


# ---------- CONSULTA RELACIONAMENTO: LIVROS COMPRADOS POR UM USUÁRIO ----------
@router.get("/usuario/{usuario_id}")
async def livros_de_usuario(usuario_id: int, session=Depends(get_session)):
    try:
        query = (
            select(Livro)
            .join(LivrosCompras)
            .where(LivrosCompras.usuario_id == usuario_id)
        )
        result = await session.exec(query)
        livros = result.all()

        return {"usuario_id": usuario_id, "livros": livros}

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Erro ao consultar livros do usuário")
