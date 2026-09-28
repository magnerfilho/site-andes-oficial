# Site oficial — Grupo Andes

Site institucional e catálogo de produtos do **Grupo Andes**, em Flask + SQLite + templates HTML.

Mostra clientes (órgãos e instituições), páginas institucionais e listagem de produtos por departamento e categoria.

## Páginas

| Rota | Página |
|---|---|
| `/` | Início (clientes em destaque) |
| `/sobre` | Sobre |
| `/produtos` | Catálogo (com filtros por departamento/categoria) |
| `/atas` | Atas |
| `/contato` | Contato |

## Stack

- Python
- Flask >= 3.0.0
- SQLite (`banco_produtos.db`, gerado pelo script de carga)
- Jinja2 (`templates/`)
- Arquivos estáticos em `static/`

## Como rodar
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python criar_banco.py
python app.py
