from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func
from database import get_session
from models.usuario import Usuario
from models.livroCompras import LivrosCompras
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/usuarios")

@router.get("/buscar")
async def buscar_usuarios(nome: str, session=Depends(get_session)):
    try:
        query = select(Usuario).where(Usuario.nome.ilike(f"%{nome}%"))
        result = await session.exec(query)
        return result.all()

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Erro ao buscar usuários")


@router.get("/mais-compras")
async def usuarios_com_mais_compras(minimo: int = 1, session=Depends(get_session)):
    try:
        query = (
            select(Usuario, func.count(LivrosCompras.livro_id).label("qtd"))
            .join(LivrosCompras)
            .group_by(Usuario.id)
            .having(func.count(LivrosCompras.livro_id) >= minimo)
        )

        result = await session.exec(query)
        return [{"usuario": u, "total_compras": qtd} for u, qtd in result.all()]

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Erro ao consultar usuários")
