from fastapi import FastAPI
from models import Admin, Usuario, Livro, LivrosCompras
from routes import livro, admin, usuario, compras
app = FastAPI()

app.include_router(livro.router)
app.include_router(admin.router)
app.include_router(usuario.router)
app.include_router(compras.router)