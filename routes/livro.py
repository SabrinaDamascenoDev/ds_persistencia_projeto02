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
    """
    Cria um novo livro no banco de dados.

    Args:
        livro (LivroPost): Dados enviados para criação do livro.
        session (AsyncSession): Sessão assíncrona de banco de dados.

    Returns:
        Livro: Registro do livro criado.

    Raises:
        HTTPException 500: Caso ocorra erro ao salvar no banco.
    """
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
async def listar_livros(offset: int = 0, limit: int = Query(default=10, le=100), session: AsyncSession = Depends(get_session)):
    """
    Lista livros com informações das compras relacionadas.

    Args:
        offset (int): Número de itens para pular.
        limit (int): Quantidade máxima de itens retornados.
        session (AsyncSession): Sessão assíncrona do banco.

    Returns:
        list[LivroComCompras]: Lista paginada de livros.
    """
    stmt = (select(Livro).offset(offset).limit(limit)
            .options(joinedload(Livro.compras)))
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
    """
    Busca livros com filtros avançados, ordenação e busca textual.

    Args:
        session (AsyncSession): Sessão do banco.
        busca (str | None): Texto para busca em título ou autor.
        genero (str | None): Filtro por gênero.
        editora (str | None): Filtro por editora.
        admin_id (int | None): Filtro pelo admin criador.
        ordernar_por (str): Campo de ordenação.
        ordem (str): Direção da ordenação ("asc" ou "desc").

    Returns:
        list[LivroComCompras]: Lista filtrada e ordenada de livros.
    """
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

@router.get("/{id}", response_model=LivroComCompras)
async def obter_livro(id: int, session: AsyncSession = Depends(get_session)):
    """
    Obtém um livro pelo seu ID, incluindo compras associadas.

    Args:
        id (int): ID do livro.
        session (AsyncSession): Sessão assíncrona do banco.

    Returns:
        LivroComCompras: Livro encontrado.

    Raises:
        HTTPException 404: Caso o livro não exista.
    """
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
    """
    Atualiza um livro existente com os campos informados.

    Args:
        id (int): ID do livro.
        livro (LivroUpdate): Dados atualizados.
        session (AsyncSession): Sessão assíncrona do banco.

    Returns:
        Livro: Livro atualizado.

    Raises:
        HTTPException 404: Caso o livro não exista.
        HTTPException 500: Caso ocorra erro na atualização.
    """
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
    """
    Remove um livro do banco de dados.

    Args:
        id (int): ID do livro a ser removido.
        session (AsyncSession): Sessão assíncrona do banco.

    Returns:
        dict: Mensagem de confirmação.

    Raises:
        HTTPException 404: Caso o livro não exista.
        HTTPException 500: Caso ocorra erro ao deletar.
    """
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
