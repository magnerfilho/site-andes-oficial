import os
import sqlite3

from flask import Flask, abort, render_template

app = Flask(__name__)

DATABASE_PATH = 'banco_produtos.db'
ALL_PRODUCTS_SLUG = 'exibir-tudo'
HOME_CLIENTS = [
    {
        'image': 'imagens/clientes/marinha.png',
        'alt': 'Marinha do Brasil',
        'caption': 'Marinha do Brasil',
        'dark_background': False,
    },
    {
        'image': 'imagens/clientes/ufmg.svg',
        'alt': 'Universidade Federal de Minas Gerais',
        'caption': 'UFMG',
        'dark_background': False,
    },
    {
        'image': 'imagens/clientes/estado-goias.svg',
        'alt': 'Governo do Estado de Goiás',
        'caption': 'Estado de Goiás',
        'dark_background': False,
    },
    {
        'image': 'imagens/clientes/goinfra.png',
        'alt': 'GOINFRA — Agência Goiana de Infraestrutura e Transportes',
        'caption': 'GOINFRA-GO',
        'dark_background': True,
    },
    {
        'image': 'imagens/clientes/bombeiros-go.png',
        'alt': 'Corpo de Bombeiros Militar do Estado de Goiás',
        'caption': 'CBMGO',
        'dark_background': False,
    },
    {
        'image': 'imagens/clientes/mp-go.png',
        'alt': 'Ministério Público do Estado de Goiás',
        'caption': 'MP-GO',
        'dark_background': True,
    },
    {
        'image': 'imagens/clientes/seduc-go.png',
        'alt': 'Secretaria de Estado da Educação de Goiás',
        'caption': 'SEDUC-GO',
        'dark_background': False,
    },
    {
        'image': 'imagens/clientes/policia-penal-go.png',
        'alt': 'Polícia Penal do Estado de Goiás',
        'caption': 'Polícia Penal-GO',
        'dark_background': False,
    },
    {
        'image': 'imagens/clientes/ueg-oficial.png',
        'alt': 'Universidade Estadual de Goiás',
        'caption': 'UEG',
        'dark_background': True,
    },
    {
        'image': 'imagens/clientes/ufg.png',
        'alt': 'Universidade Federal de Goiás',
        'caption': 'UFG',
        'dark_background': False,
    },
    {
        'image': 'imagens/clientes/crp-rj.png',
        'alt': 'Conselho Regional de Psicologia do Estado do Rio de Janeiro',
        'caption': 'CRP-RJ',
        'dark_background': False,
    },
    {
        'image': 'imagens/clientes/saev.svg',
        'alt': 'SAEV — Superintendência de Água, Esgoto e Meio Ambiente de Votuporanga',
        'caption': 'SAEV Votuporanga',
        'dark_background': False,
    },
]


def get_connection():
    if not os.path.exists(DATABASE_PATH):
        raise FileNotFoundError(
            'Banco não encontrado. Execute python criar_banco.py antes de iniciar o site.'
        )

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def parse_specifications(text):
    return [part.strip() for part in text.split('|') if part.strip()]


def product_from_row(row):
    product = dict(row)
    product['lista_especificacoes'] = parse_specifications(product['especificacoes'])
    return product


def load_departments():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        '''
        SELECT
            d.id AS departamento_id,
            d.nome AS departamento_nome,
            d.slug AS departamento_slug,
            c.id AS categoria_id,
            c.nome AS categoria_nome,
            c.slug AS categoria_slug
        FROM departamentos d
        LEFT JOIN categorias c ON c.departamento_id = d.id
        ORDER BY d.id, c.id
        '''
    )
    rows = cursor.fetchall()
    connection.close()

    departments = []
    departments_by_id = {}

    for row in rows:
        department_id = row['departamento_id']
        if department_id not in departments_by_id:
            department = {
                'id': department_id,
                'nome': row['departamento_nome'],
                'slug': row['departamento_slug'],
                'categorias': [],
            }
            departments_by_id[department_id] = department
            departments.append(department)

        if row['categoria_id'] is not None:
            departments_by_id[department_id]['categorias'].append(
                {
                    'id': row['categoria_id'],
                    'nome': row['categoria_nome'],
                    'slug': row['categoria_slug'],
                }
            )

    return departments


def find_department(departments, slug):
    for department in departments:
        if department['slug'] == slug:
            return department
    return None


def find_category(department, slug):
    for category in department['categorias']:
        if category['slug'] == slug:
            return category
    return None


def load_products(department_slug=None, category_slug=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT
            p.id,
            p.nome,
            p.descricao,
            p.especificacoes,
            p.imagem,
            d.nome AS departamento_nome,
            d.slug AS departamento_slug,
            c.nome AS categoria_nome,
            c.slug AS categoria_slug
        FROM produtos p
        JOIN departamentos d ON d.id = p.departamento_id
        LEFT JOIN categorias c ON c.id = p.categoria_id
    '''
    filters = []
    params = []

    if department_slug:
        filters.append('d.slug = ?')
        params.append(department_slug)

    if category_slug:
        filters.append('c.slug = ?')
        params.append(category_slug)

    if filters:
        query += ' WHERE ' + ' AND '.join(filters)

    query += ' ORDER BY p.nome'
    cursor.execute(query, params)
    products = [product_from_row(row) for row in cursor.fetchall()]
    connection.close()
    return products


@app.route('/')
def home():
    return render_template(
        'index.html',
        pagina_ativa='inicio',
        clientes=HOME_CLIENTS,
    )


@app.route('/sobre')
def about():
    return render_template('sobre.html', pagina_ativa='sobre')


@app.route('/produtos')
@app.route('/produtos/<departamento_slug>')
@app.route('/produtos/<departamento_slug>/<categoria_slug>')
def products(departamento_slug=None, categoria_slug=None):
    departments = load_departments()
    selected_department = None
    selected_category = None
    show_all_products = False
    product_list = []

    if departamento_slug == ALL_PRODUCTS_SLUG:
        if categoria_slug:
            abort(404)
        show_all_products = True
        product_list = load_products()
    elif departamento_slug:
        selected_department = find_department(departments, departamento_slug)
        if selected_department is None:
            abort(404)

        if categoria_slug:
            selected_category = find_category(selected_department, categoria_slug)
            if selected_category is None:
                abort(404)

        product_list = load_products(departamento_slug, categoria_slug)

    return render_template(
        'produtos.html',
        pagina_ativa='produtos',
        departamentos=departments,
        produtos=product_list,
        departamento_atual=selected_department,
        categoria_atual=selected_category,
        exibir_tudo=show_all_products,
        slug_todos=ALL_PRODUCTS_SLUG,
    )


@app.route('/atas')
def price_records():
    return render_template('atas.html', pagina_ativa='atas')


@app.route('/contato')
def contact():
    return render_template('contato.html', pagina_ativa='contato')


if __name__ == '__main__':
    app.run(debug=True)
