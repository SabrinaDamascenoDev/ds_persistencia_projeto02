from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from database import get_session
from models.livro import Livro, LivroPost, LivroUpdate, LivroComCompras
from models.livroCompras import LivrosCompras, LivrosComprasPost
from models.usuario import Usuario

router = APIRouter(
    prefix="/livros",
    tags=["Livros"]
)

@router.post("/", response_model=Livro)
def criar_livro(livro: LivroPost, session: Session = Depends(get_session)):
    db_livro = Livro(**livro.model_dump())
    try:
        session.add(db_livro)
        session.commit()
        session.refresh(db_livro)
        return db_livro
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[LivroComCompras])
def listar_livros(session: Session = Depends(get_session)):
    stmt = select(Livro).options(joinedload(Livro.compras))
    return session.exec(stmt).unique().all() 


@router.patch("/{id}", response_model=Livro)
def livro_update(
    id: int,
    livro: LivroUpdate,
    session: Session = Depends(get_session),
):
    db_livro = session.get(Livro, id)
    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro not found")

    for key, value in livro.model_dump(exclude_unset=True).items():
        setattr(db_livro, key, value)

    session.add(db_livro)
    session.commit()
    session.refresh(db_livro)
    return db_livro
