from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from models import Admin, Usuario, Livro, LivrosCompras
from routes import livro, admin, usuario, compras

app = FastAPI()

app.include_router(livro.router)
app.include_router(admin.router)
app.include_router(usuario.router)
app.include_router(compras.router)

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"erro": "Violação de integridade referencial", "detalhes": str(exc.orig)}
    )

@app.exception_handler(NoResultFound)
async def no_result_handler(request: Request, exc: NoResultFound):
    return JSONResponse(
        status_code=404,
        content={"erro": "Registro não encontrado"}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"erro": "Erro interno no servidor", "detalhes": str(exc)}
    )
