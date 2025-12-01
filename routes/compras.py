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
async def listar_compras(session: AsyncSession = Depends(get_session)):
    stmt = select(LivrosCompras)
    result = await session.execute(stmt)
    return result.scalars().unique().all()

@router.get("/search", response_model=list[LivrosCompras], summary="Filtrar Compras por Período")
async def buscar_e_filtrar_compras(
    session: AsyncSession = Depends(get_session),
    data_inicial: date | None = Query(None, description="Filtrar por compras realizadas a partir desta data (Formato: YYYY-MM-DD)"),
    data_final: date | None = Query(None, description="Filtrar por compras realizadas até esta data (Formato: YYYY-MM-DD)")
):
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
    try:
        stmt = select(func.sum(LivrosCompras.quantidade_comprados))
        result = await session.execute(stmt)
        total = result.scalar_one_or_none()
        return {"total_itens_comprados": total if total is not None else 0}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao calcular a agregação: {str(e)}")


@router.get("/{compra_id}", response_model=LivrosCompras)
async def obter_compra(compra_id: int, session: AsyncSession = Depends(get_session)):
    compra = await session.get(LivrosCompras, compra_id)
    if not compra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compra não encontrada")
    return compra


@router.put("/{compra_id}", response_model=LivrosCompras)
async def atualizar_compra(compra_id: int, dados: LivrosComprasPost, session: AsyncSession = Depends(get_session)):
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