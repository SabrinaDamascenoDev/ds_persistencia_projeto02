from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models.livroCompras import LivrosCompras, LivrosComprasPost

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[LivrosCompras])
async def listar_compras(session: AsyncSession = Depends(get_session)):
    stmt = select(LivrosCompras)
    result = await session.execute(stmt)
    return result.scalars().unique().all()


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
    update_data = dados.dict(exclude_unset=True)
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




