import csv
import os
import sqlite3

DATABASE_PATH = 'banco_produtos.db'
CSV_PATH = os.path.join('dados', 'produtos.csv')

DEPARTMENTS = [
    (
        'Descartáveis e Embalagens',
        'descartaveis-e-embalagens',
        [
            ('Copos e Cumbucas', 'copos-e-cumbucas'),
            ('Sacolas e Filmes', 'sacolas-e-filmes'),
        ],
    ),
    (
        'Eletrodomésticos e Equipamentos',
        'eletrodomesticos-e-equipamentos',
        [
            ('Bebedores e Purificadores', 'bebedores-e-purificadores'),
            ('Climatizadores', 'climatizadores'),
            ('Espremedores e Trituradores', 'espremedores-e-trituradores'),
            ('Máquinas de Lavar', 'maquinas-de-lavar'),
            ('Ventiladores', 'ventiladores'),
        ],
    ),
    (
        'Ferramentas e Construção',
        'ferramentas-e-construcao',
        [
            ('Acoplamentos', 'acoplamentos'),
            ('Carros Plataformas', 'carros-plataformas'),
            ('Compressores e Motocompressores', 'compressores-e-motocompressores'),
            ('Ferramentas e Acessórios', 'ferramentas-e-acessorios'),
            ('Materiais Hidráulicos', 'materiais-hidraulicos'),
        ],
    ),
    (
        'Informática e Eletrônicos',
        'informatica-e-eletronicos',
        [
            ('Equipamentos de Áudio', 'equipamentos-de-audio'),
            ('Equipamentos e Acessórios de Informática', 'equipamentos-e-acessorios-de-informatica'),
            ('Fragmentadoras', 'fragmentadoras'),
            ('Impressoras e Suprimentos', 'impressoras-e-suprimentos'),
        ],
    ),
    (
        'Limpeza e Utilidades',
        'limpeza-e-utilidades',
        [
            ('Cestos e Lixeiras', 'cestos-e-lixeiras'),
        ],
    ),
    (
        'Materiais Elétricos',
        'materiais-eletricos',
        [
            ('Cabos Elétricos', 'cabos-eletricos'),
            ('Estabilizadores e Nobreaks', 'estabilizadores-e-nobreaks'),
            ('Transformadores', 'transformadores'),
        ],
    ),
    (
        'Segurança e Acessórios',
        'seguranca-e-acessorios',
        [
            ('Bicicletários', 'bicicletarios'),
            ('Descensores e Talabartes', 'descensores-e-talabartes'),
        ],
    ),
    (
        'Telefone e Comunicação',
        'telefone-e-comunicacao',
        [
            ('Aparelhos Celulares', 'aparelhos-celulares'),
            ('Telefonia', 'telefonia'),
        ],
    ),
    (
        'Outros',
        'outros',
        [],
    ),
]


def create_tables(cursor):
    cursor.execute('DROP TABLE IF EXISTS produtos')
    cursor.execute('DROP TABLE IF EXISTS categorias')
    cursor.execute('DROP TABLE IF EXISTS departamentos')

    cursor.execute(
        '''
        CREATE TABLE departamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            departamento_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            slug TEXT NOT NULL,
            FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            departamento_id INTEGER NOT NULL,
            categoria_id INTEGER,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            especificacoes TEXT NOT NULL,
            imagem TEXT NOT NULL,
            FOREIGN KEY (departamento_id) REFERENCES departamentos(id),
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
        '''
    )


def seed_departments(cursor):
    department_ids = {}
    category_ids = {}

    for name, slug, categories in DEPARTMENTS:
        cursor.execute(
            'INSERT INTO departamentos (nome, slug) VALUES (?, ?)',
            (name, slug),
        )
        department_id = cursor.lastrowid
        department_ids[name] = department_id

        for category_name, category_slug in categories:
            cursor.execute(
                '''
                INSERT INTO categorias (departamento_id, nome, slug)
                VALUES (?, ?, ?)
                ''',
                (department_id, category_name, category_slug),
            )
            category_ids[(name, category_name)] = cursor.lastrowid

    return department_ids, category_ids


def seed_products(cursor, department_ids, category_ids):
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f'CSV não encontrado: {CSV_PATH}')

    with open(CSV_PATH, 'r', encoding='utf-8-sig', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            department_name = row['departamento'].strip()
            category_name = row['categoria'].strip()
            department_id = department_ids.get(department_name)

            if department_id is None:
                print(f'[AVISO] Departamento ignorado no CSV: {department_name}')
                continue

            category_id = None
            if category_name:
                category_id = category_ids.get((department_name, category_name))
                if category_id is None:
                    print(f'[AVISO] Categoria ignorada no CSV: {category_name}')

            cursor.execute(
                '''
                INSERT INTO produtos (
                    departamento_id, categoria_id, nome, descricao, especificacoes, imagem
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (
                    department_id,
                    category_id,
                    row['nome'].strip(),
                    row['descricao'].strip(),
                    row['especificacoes'].strip(),
                    row['imagem'].strip(),
                ),
            )


def main():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    create_tables(cursor)
    department_ids, category_ids = seed_departments(cursor)
    seed_products(cursor, department_ids, category_ids)

    connection.commit()
    cursor.execute('SELECT COUNT(*) FROM produtos')
    product_count = cursor.fetchone()[0]
    connection.close()

    print(f'[SUCESSO] Banco criado em {DATABASE_PATH} com {product_count} produtos.')


if __name__ == '__main__':
    main()
