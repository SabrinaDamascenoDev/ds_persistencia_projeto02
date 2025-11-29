from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from database import get_session
from models.admin import Admin, AdminPost

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.post("/", response_model=Admin)
def criar_admin(admin:AdminPost, session: Session = Depends(get_session)):
    db_admin = Admin.model_validate(admin)
    try:
        session.add(db_admin)
        session.commit()
        session.refresh(db_admin)
        return db_admin
    except Exception as e:
        session.rollback()
        raise e
