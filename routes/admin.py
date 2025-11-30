from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func
from database import get_session
from models.admin import Admin
from models.livro import Livro
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/admins")

@router.get("/ranking")
async def ranking_admins(session=Depends(get_session)):
    try:
        query = (
            select(Admin, func.count(Livro.id).label("total"))
            .join(Livro)
            .group_by(Admin.id)
            .order_by(func.count(Livro.id).desc())
        )

        result = await session.exec(query)
        return [{"admin": adm, "livros_adicionados": total} for adm, total in result.all()]

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Erro ao consultar ranking")


@router.get("/{admin_id}/genero/{genero}")
async def admin_por_genero(admin_id: int, genero: str, session=Depends(get_session)):
    try:
        query = (
            select(Livro)
            .where(Livro.admin_id == admin_id)
            .where(Livro.genero.ilike(f"%{genero}%"))
        )

        result = await session.exec(query)
        return result.all()

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Erro ao consultar livros do admin")
