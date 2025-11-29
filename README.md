# Projeto Livraria

## Como rodar o projeto

1. Clone o repositório
```bash
   git clone https://github.com/SabrinaDamascenoDev/ds_persistencia_projeto02.git
   cd ds_persistencia_projeto02
```

2. Instale as dependências com UV:
```bash
   uv sync
```
   
   Ou se não tiver UV instalado:
```bash
   pip install uv
   uv sync
```

3. Copie o arquivo de exemplo:
```bash
   cp .env.example .env
```

4. Execute as migrations:
```bash
   alembic upgrade head
```

5. Rode o servidor:
```bash
   fastapi dev main.py
```

6. Acesse: http://localhost:8000/docs