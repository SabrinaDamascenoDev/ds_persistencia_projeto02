from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from database import get_session
from models.usuario import Usuario, UsuarioBase, UsuarioPost, UsuarioComCompras

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

@router.post("/", response_model=Usuario)
def criar_usuario(usuario:UsuarioPost, session: Session = Depends(get_session)):
    db_user = Usuario(**usuario.model_dump())
    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except Exception as e:
        session.rollback()
        raise e

@router.get("/", response_model=list[UsuarioComCompras])
def listar_livros(session: Session = Depends(get_session)):
    stmt = select(Usuario).options(joinedload(Usuario.livros_comprados))
    return session.exec(stmt).unique().all()