from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models.admin import Admin, AdminPost, AdminComLivrosAdicionados

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.post("/", response_model=Admin)
async def criar_admin(admin: AdminPost, session: AsyncSession = Depends(get_session)):
    db_admin = Admin.model_validate(admin)
    try:
        session.add(db_admin)
        await session.commit()
        await session.refresh(db_admin)
        return db_admin
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=list[AdminComLivrosAdicionados])
async def listar_livros(session: AsyncSession = Depends(get_session)):
    stmt = select(Admin).options(joinedload(Admin.livros_adicionados))
    result = await session.execute(stmt)
    return result.scalars().unique().all()


@router.get("/{admin_id}", response_model=AdminComLivrosAdicionados)
async def obter_admin(admin_id: int, session: AsyncSession = Depends(get_session)):
    stmt = select(Admin).where(Admin.id == admin_id).options(joinedload(Admin.livros_adicionados))
    result = await session.execute(stmt)
    admin = result.scalars().first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin não encontrado")
    return admin


@router.put("/{admin_id}", response_model=Admin)
async def atualizar_admin(admin_id: int, dados: AdminPost, session: AsyncSession = Depends(get_session)):
    admin = await session.get(Admin, admin_id)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin não encontrado")
    update_data = dados.model_dump(exclude_unset=True) if hasattr(dados, "model_dump") else dados.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(admin, key, value)
    try:
        await session.commit()
        await session.refresh(admin)
        return admin
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{admin_id}")
async def deletar_admin(admin_id: int, session: AsyncSession = Depends(get_session)):
    admin = await session.get(Admin, admin_id)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin não encontrado")
    try:
        await session.delete(admin)
        await session.commit()
        return {"detail": "Admin removido"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

