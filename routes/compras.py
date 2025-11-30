from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, func
from datetime import datetime
from database import get_session
from models.livroCompras import LivrosCompras
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/compras")

@router.get("/total-usuario/{usuario_id}")
async def total_gasto(usuario_id: int, session=Depends(get_session)):
    try:
        query = select(func.sum(LivrosCompras.preco_pago)).where(
            LivrosCompras.usuario_id == usuario_id
        )

        result = await session.exec(query)
        return {"usuario_id": usuario_id, "total_gasto": result.one_or_none()}

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Erro ao calcular total gasto")


# -------- TOTAL ARRECADADO NO SISTEMA --------
@router.get("/total-sistema")
async def total_sistema(session=Depends(get_session)):
    try:
        query = select(func.sum(LivrosCompras.preco_pago))
        result = await session.exec(query)
        return {"total_arrecadado": result.one_or_none()}

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Erro ao calcular total arrecadado")


# -------- COMPRAS POR PERÍODO --------
@router.get("/periodo")
async def compras_periodo(
    inicio: datetime = Query(...),
    fim: datetime = Query(...),
    session=Depends(get_session)
):
    try:
        query = (
            select(LivrosCompras)
            .where(LivrosCompras.data_compra >= inicio)
            .where(LivrosCompras.data_compra <= fim)
        )
        result = await session.exec(query)
        return result.all()

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Erro ao consultar período")
