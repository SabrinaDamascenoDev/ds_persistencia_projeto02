from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from database import get_session
from models.livroCompras import LivrosCompras, LivrosComprasPost

router = APIRouter(
    prefix="/compras",
    tags=["Compras"]
)

@router.post("/", response_model=LivrosCompras)
def realizar_compra(compra:LivrosComprasPost, session: Session = Depends(get_session)):
    compra_bd = LivrosCompras.model_validate(compra)
    try:
        session.add(compra_bd)
        session.commit()
        session.refresh(compra_bd)
        return compra_bd
    except Exception as e:
        session.rollback()
        return e




