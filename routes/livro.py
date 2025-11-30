from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import joinedload
from sqlmodel import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models.livro import Livro, LivroPost, LivroUpdate, LivroComCompras
from models.livroCompras import LivrosCompras
from models.usuario import Usuario

router = APIRouter(
    prefix="/livros",
    tags=["Livros"]
)

@router.post("/", response_model=Livro)
async def criar_livro(livro: LivroPost, session: AsyncSession = Depends(get_session)):
    db_livro = Livro.model_validate(livro)
    try:
        session.add(db_livro)
        await session.commit()
        await session.refresh(db_livro)
        return db_livro
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=list[LivroComCompras])
async def listar_livros(session: AsyncSession = Depends(get_session)):
    stmt = select(Livro).options(joinedload(Livro.compras))
    result = await session.execute(stmt)
    return result.scalars().unique().all()


@router.get("/search", response_model=list[LivroComCompras], summary="Buscar, Filtrar e Ordenar Livros")
async def buscar_e_filtrar_livros(
    session: AsyncSession = Depends(get_session),
    busca: str | None = Query(None, description="Busca textual por Título ou Autor"),
    genero: str | None = Query(None, description="Filtrar por Gênero"),
    editora: str | None = Query(None, description="Filtrar por Editora"),
    admin_id: int | None = Query(None, description="Filtrar por ID do Admin criador"),
    ordernar_por: str = Query("id", description="Campo para ordenação (ex: id, titulo, preco_uni)"),
    ordem: str = Query("asc", description="Direção da ordenação (asc ou desc)")
):
    stmt = select(Livro).options(joinedload(Livro.compras))

    if busca:
        stmt = stmt.where(
            or_(
                Livro.titulo.ilike(f"%{busca}%"),
                Livro.autor.ilike(f"%{busca}%")
            )
        )

    filtros = []
    if genero:
        filtros.append(Livro.genero == genero)
    if editora:
        filtros.append(Livro.editora == editora)
    if admin_id is not None:
        filtros.append(Livro.admin_id == admin_id)

    if filtros:
        stmt = stmt.where(and_(*filtros))

    if ordernar_por in ["id", "titulo", "autor", "quantidade_paginas", "preco_uni"]:
        coluna = getattr(Livro, ordernar_por)
        if ordem.lower() == "desc":
            stmt = stmt.order_by(coluna.desc())
        else:
            stmt = stmt.order_by(coluna.asc())

    result = await session.execute(stmt)
    return result.scalars().unique().all()


@router.get("/comprados/usuario/{usuario_id}", response_model=list[LivroComCompras], summary="Listar Livros Comprados Por Usuário")
async def listar_livros_comprados_por_usuario(usuario_id: int, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(Livro)
        .join(LivrosCompras)
        .where(LivrosCompras.usuario_id == usuario_id)
        .options(joinedload(Livro.compras))
    )

    result = await session.execute(stmt)
    livros = result.scalars().unique().all()

    if not livros:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Nenhum livro encontrado para o usuário ID {usuario_id}")

    return livros

@router.get("/{id}", response_model=LivroComCompras)
async def obter_livro(id: int, session: AsyncSession = Depends(get_session)):
    stmt = select(Livro).where(Livro.id == id).options(joinedload(Livro.compras))
    result = await session.execute(stmt)
    livro = result.scalars().first()
    if not livro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")
    return livro

@router.put("/{id}", response_model=Livro)
async def livro_update(
    id: int,
    livro: LivroUpdate,
    session: AsyncSession = Depends(get_session),
):
    db_livro = await session.get(Livro, id)
    if not db_livro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")

    update_data = livro.model_dump(exclude_unset=True) if hasattr(livro, "model_dump") else livro.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_livro, key, value)

    try:
        await session.commit()
        await session.refresh(db_livro)
        return db_livro
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{id}")
async def deletar_livro(id: int, session: AsyncSession = Depends(get_session)):
    db_livro = await session.get(Livro, id)
    if not db_livro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")

    try:
        await session.delete(db_livro)
        await session.commit()
        return {"detail": "Livro removido"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))