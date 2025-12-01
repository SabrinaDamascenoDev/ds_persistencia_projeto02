from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models.usuario import Usuario, UsuarioBase, UsuarioPost, UsuarioComCompras

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

@router.post("/", response_model=Usuario)
async def criar_usuario(usuario: UsuarioPost, session: AsyncSession = Depends(get_session)):
    """
    Criar um novo usuário.

    Args:
        usuario (UsuarioPost): Dados para criação do usuário.
        session (AsyncSession): Sessão do banco de dados.

    Returns:
        Usuario: Usuário recém-criado.

    Raises:
        HTTPException 500: Caso ocorra um erro ao salvar no banco.
    """
    db_user = Usuario.model_validate(usuario)
    try:
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", response_model=list[UsuarioComCompras])
async def listar_usuarios(offset: int = 0, limit: int = Query(default=10, le=100), session: AsyncSession = Depends(get_session)):
    """
    Listar usuários cadastrados com paginação.

    Args:
        offset (int): Valor inicial da consulta.
        limit (int): Máximo de registros retornados.
        session (AsyncSession): Sessão do banco de dados.

    Returns:
        list[UsuarioComCompras]: Lista de usuários com compras relacionadas.
    """
    stmt = (
        select(Usuario)
        .offset(offset)
        .limit(limit)
        .options(joinedload(Usuario.livros_comprados))
    )
    result = await session.execute(stmt)
    return result.scalars().unique().all()


@router.get("/search", response_model=list[UsuarioComCompras], summary="Filtrar e Ordenar Usuários")
async def buscar_e_filtrar_usuarios(
    session: AsyncSession = Depends(get_session),
    nome: str | None = Query(None, description="Filtrar por nome parcial"),
    ordernar_por: str = Query("id", description="Campo para ordenação (ex: id, nome, email)"),
    ordem: str = Query("asc", description="Direção da ordenação (asc ou desc)")
):
    """
    Buscar usuários aplicando filtros e ordenação dinâmica.

    Args:
        session (AsyncSession): Sessão do banco de dados.
        nome (str | None): Filtro por nome parcial.
        ordernar_por (str): Campo usado na ordenação.
        ordem (str): Direção da ordenação (asc/desc).

    Returns:
        list[UsuarioComCompras]: Usuários filtrados e ordenados.
    """
    stmt = select(Usuario).options(joinedload(Usuario.livros_comprados))

    if nome:
        stmt = stmt.where(Usuario.nome.ilike(f"%{nome}%"))

    if ordernar_por in ["id", "nome", "email", "endereco"]:
        coluna = getattr(Usuario, ordernar_por)
        stmt = stmt.order_by(coluna.desc() if ordem.lower() == "desc" else coluna.asc())

    result = await session.execute(stmt)
    return result.scalars().unique().all()


@router.get("/{usuario_id}", response_model=UsuarioComCompras)
async def obter_usuario(usuario_id: int, session: AsyncSession = Depends(get_session)):
    """
    Obter detalhes completos de um usuário específico.

    Args:
        usuario_id (int): ID do usuário.
        session (AsyncSession): Sessão do banco de dados.

    Returns:
        UsuarioComCompras: Dados do usuário encontrado.

    Raises:
        HTTPException 404: Se o usuário não existir.
    """
    stmt = (
        select(Usuario)
        .where(Usuario.id == usuario_id)
        .options(joinedload(Usuario.livros_comprados))
    )
    result = await session.execute(stmt)
    usuario = result.scalars().first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario não encontrado"
        )

    return usuario


@router.put("/{usuario_id}", response_model=Usuario)
async def atualizar_usuario(usuario_id: int, dados: UsuarioBase, session: AsyncSession = Depends(get_session)):
    """
    Atualizar parcialmente os dados de um usuário.

    Args:
        usuario_id (int): ID do usuário a atualizar.
        dados (UsuarioBase): Campos atualizáveis.
        session (AsyncSession): Sessão do banco de dados.

    Returns:
        Usuario: Usuário atualizado.

    Raises:
        HTTPException 404: Caso o usuário não exista.
        HTTPException 500: Caso ocorra erro ao atualizar.
    """
    usuario = await session.get(Usuario, usuario_id)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario não encontrado"
        )

    update_data = dados.model_dump(exclude_unset=True) if hasattr(dados, "model_dump") else dados.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(usuario, key, value)

    try:
        await session.commit()
        await session.refresh(usuario)
        return usuario
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{usuario_id}")
async def deletar_usuario(usuario_id: int, session: AsyncSession = Depends(get_session)):
    """
    Deletar um usuário específico.

    Args:
        usuario_id (int): ID do usuário.
        session (AsyncSession): Sessão do banco de dados.

    Returns:
        dict: Mensagem de sucesso.

    Raises:
        HTTPException 404: Caso o usuário não exista.
        HTTPException 500: Caso ocorra erro ao remover.
    """
    usuario = await session.get(Usuario, usuario_id)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario não encontrado"
        )

    try:
        await session.delete(usuario)
        await session.commit()
        return {"detail": "Usuario removido"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
