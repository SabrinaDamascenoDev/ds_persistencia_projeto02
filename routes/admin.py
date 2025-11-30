from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlmodel import select, or_
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
async def listar_admins(session: AsyncSession = Depends(get_session)):
    stmt = select(Admin).options(joinedload(Admin.livros_adicionados))
    result = await session.execute(stmt)
    return result.scalars().unique().all()

@router.get("/search", response_model=list[AdminComLivrosAdicionados], summary="Filtrar e Ordenar Admins")
async def buscar_e_filtrar_admins(
    session: AsyncSession = Depends(get_session),
    nome: str | None = Query(None, description="Filtrar por nome parcial"),
    email: str | None = Query(None, description="Filtrar por email parcial"),
    ordernar_por: str = Query("id", description="Campo para ordenação (ex: id, nome, email)"),
    ordem: str = Query("asc", description="Direção da ordenação (asc ou desc)")
):
    stmt = select(Admin).options(joinedload(Admin.livros_adicionados))

    if nome:
        stmt = stmt.where(Admin.nome.ilike(f"%{nome}%"))
    if email:
        stmt = stmt.where(Admin.email.ilike(f"%{email}%"))

    if ordernar_por in ["id", "nome", "email"]:
        coluna = getattr(Admin, ordernar_por)
        if ordem.lower() == "desc":
            stmt = stmt.order_by(coluna.desc())
        else:
            stmt = stmt.order_by(coluna.asc())

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