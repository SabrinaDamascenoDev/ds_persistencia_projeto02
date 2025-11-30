from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import joinedload
from sqlmodel import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models.livroCompras import LivrosCompras, LivrosComprasPost
from sqlalchemy import func
from datetime import date

router = APIRouter(
    prefix="/compras",
    tags=["Compras"]
)

@router.post("/", response_model=LivrosCompras)
async def realizar_compra(compra: LivrosComprasPost, session: AsyncSession = Depends(get_session)):
    compra_bd = LivrosCompras.model_validate(compra)
    try:
        session.add(compra_bd)
        await session.commit()
        await session.refresh(compra_bd)
        return compra_bd
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=list[LivrosCompras])
async def listar_compras(
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

@router.get("/total-itens", summary="Total Itens Comprados")
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

    update_data = dados.model_dump(exclude_unset=True) if hasattr(dados, "model_dump") else dados.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(compra, key, value)

    try:
        await session.commit()
        await session.refresh(compra)
        return compra
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{compra_id}")
async def deletar_compra(compra_id: int, session: AsyncSession = Depends(get_session)):
    compra = await session.get(LivrosCompras, compra_id)
    if not compra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compra não encontrada")

    try:
        await session.delete(compra)
        await session.commit()
        return {"detail": "Compra removida"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))