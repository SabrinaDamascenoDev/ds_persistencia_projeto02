from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import joinedload
from sqlmodel import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models.livroCompras import LivrosCompras, LivrosComprasPost
from datetime import date
from models.livro import Livro

router = APIRouter(
    prefix="/compras",
    tags=["Compras"]
)


@router.post("/", response_model=LivrosCompras)
async def realizar_compra(compra: LivrosComprasPost, session: AsyncSession = Depends(get_session)):
    """
    Realiza a compra de um livro, reduzindo o estoque e registrando a compra no banco.

    Args:
        compra (LivrosComprasPost): Dados da compra enviados pelo usuário.
        session (AsyncSession): Sessão assíncrona com o banco de dados.

    Returns:
        LivrosCompras: Registro da compra criada.

    Raises:
        HTTPException 404: Caso o livro informado não exista.
        HTTPException 400: Caso o estoque seja insuficiente.
        HTTPException 500: Qualquer erro inesperado durante a operação.
    """
    try:
        livro = await session.get(Livro, compra.livro_id)
        if not livro:
            raise HTTPException(status_code=404, detail="Livro não encontrado")

        if livro.quantidade_estoque < compra.quantidade_comprados:
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente. Disponível: {livro.quantidade_estoque}"
            )

        livro.quantidade_estoque -= compra.quantidade_comprados

        preco_pago = livro.preco_uni * compra.quantidade_comprados

        compra_bd = LivrosCompras(
            usuario_id=compra.usuario_id,
            livro_id=compra.livro_id,
            quantidade_comprados=compra.quantidade_comprados,
            preco_pago=preco_pago
        )

        session.add(compra_bd)

        await session.commit()
        await session.refresh(compra_bd)
        await session.refresh(livro)

        return compra_bd

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[LivrosCompras])
async def listar_compras(offset: int = 0, limit: int = Query(default=10, le=100),
                         session: AsyncSession = Depends(get_session)):
    """
    Lista todas as compras registradas.

    Args:
        offset (int): Número de registros a pular.
        limit (int): Quantidade máxima de registros retornados.
        session (AsyncSession): Sessão assíncrona do banco.

    Returns:
        list[LivrosCompras]: Lista de compras.
    """
    stmt = select(LivrosCompras).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().unique().all()


@router.get("/search", response_model=list[LivrosCompras], summary="Filtrar Compras por Período")
async def buscar_e_filtrar_compras(
        session: AsyncSession = Depends(get_session),
        data_inicial: date | None = Query(None,
                                          description="Filtrar por compras realizadas a partir desta data (Formato: YYYY-MM-DD)"),
        data_final: date | None = Query(None,
                                        description="Filtrar por compras realizadas até esta data (Formato: YYYY-MM-DD)")
):
    """
    Filtra compras dentro de um intervalo de datas.

    Args:
        session (AsyncSession): Sessão assíncrona com o banco.
        data_inicial (date | None): Data mínima da compra.
        data_final (date | None): Data máxima da compra.

    Returns:
        list[LivrosCompras]: Lista de compras filtradas.
    """
    stmt = select(LivrosCompras)

    filtros = []

    if data_inicial:
        filtros.append(func.date(LivrosCompras.data_compra) >= data_inicial)

    if data_final:
        filtros.append(func.date(LivrosCompras.data_compra) <= data_final)

    if filtros:
        stmt = stmt.where(and_(*filtros))

    result = await session.execute(stmt)
    return result.scalars().unique().all()


@router.get("/metrics/total-itens", summary="Total Itens Comprados (Agregação)")
async def total_itens_comprados(session: AsyncSession = Depends(get_session)):
    """
    Calcula o total agregado de itens comprados.

    Args:
        session (AsyncSession): Sessão assíncrona com o banco.

    Returns:
        dict: Total de itens comprados.

    Raises:
        HTTPException 500: Caso ocorra erro no cálculo.
    """
    try:
        stmt = select(func.sum(LivrosCompras.quantidade_comprados))
        result = await session.execute(stmt)
        total = result.scalar_one_or_none()
        return {"total_itens_comprados": total if total is not None else 0}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Erro ao calcular a agregação: {str(e)}")


@router.get("/{compra_id}", response_model=LivrosCompras)
async def obter_compra(compra_id: int, session: AsyncSession = Depends(get_session)):
    """
    Obtém uma compra específica pelo ID.

    Args:
        compra_id (int): ID da compra desejada.
        session (AsyncSession): Sessão assíncrona do banco.

    Returns:
        LivrosCompras: Compra encontrada.

    Raises:
        HTTPException 404: Caso a compra não exista.
    """
    compra = await session.get(LivrosCompras, compra_id)
    if not compra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compra não encontrada")
    return compra


@router.put("/{compra_id}", response_model=LivrosCompras)
async def atualizar_compra(compra_id: int, dados: LivrosComprasPost, session: AsyncSession = Depends(get_session)):
    """
    Atualiza uma compra existente, recalculando estoque e preço pago.

    Args:
        compra_id (int): ID da compra a ser atualizada.
        dados (LivrosComprasPost): Dados atualizados enviados pelo usuário.
        session (AsyncSession): Sessão assíncrona do banco.

    Returns:
        LivrosCompras: Compra atualizada.

    Raises:
        HTTPException 404: Caso a compra ou livro não existam.
        HTTPException 400: Caso o estoque do novo livro seja insuficiente.
        HTTPException 500: Outros erros inesperados.
    """
    compra = await session.get(LivrosCompras, compra_id)
    if not compra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compra não encontrada")
    try:
        livro_antigo = await session.get(Livro, compra.livro_id)
        livro_novo = await session.get(Livro, dados.livro_id)

        if not livro_novo:
            raise HTTPException(status_code=404, detail="Livro não encontrado")

        if livro_antigo:
            livro_antigo.quantidade_estoque += compra.quantidade_comprados

        if livro_novo.quantidade_estoque < dados.quantidade_comprados:
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente. Disponível: {livro_novo.quantidade_estoque}"
            )

        livro_novo.quantidade_estoque -= dados.quantidade_comprados

        compra.usuario_id = dados.usuario_id
        compra.livro_id = dados.livro_id
        compra.quantidade_comprados = dados.quantidade_comprados
        compra.preco_pago = livro_novo.preco_uni * dados.quantidade_comprados

        await session.commit()
        await session.refresh(compra)

        return compra

    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{compra_id}")
async def deletar_compra(compra_id: int, session: AsyncSession = Depends(get_session)):
    """
    Deleta uma compra e devolve o estoque ao livro correspondente.

    Args:
        compra_id (int): ID da compra a ser removida.
        session (AsyncSession): Sessão assíncrona do banco.

    Returns:
        dict: Mensagem de sucesso.

    Raises:
        HTTPException 404: Caso a compra não exista.
        HTTPException 500: Caso ocorra erro ao deletar.
    """
    compra = await session.get(LivrosCompras, compra_id)
    if not compra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compra não encontrada")

    try:
        livro = await session.get(Livro, compra.livro_id)

        if livro:
            livro.quantidade_estoque += compra.quantidade_comprados

        await session.delete(compra)
        await session.commit()

        return {"detail": "Compra removida e estoque atualizado"}

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
