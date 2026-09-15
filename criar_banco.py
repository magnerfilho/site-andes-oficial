import csv
import json
import os
import sqlite3
import unicodedata

DATABASE_PATH = 'banco_produtos.db'
CSV_PATH = os.path.join('dados', 'produtos.csv')
JSON_PATH = os.path.join('dados', 'andes_produtos_base.json')
PLACEHOLDER_IMAGE = 'produtos/placeholder.svg'
# limite do título no card para não estourar o layout
TITLE_MAX_LENGTH = 90

DEPARTMENT_ALIASES = {
    'Telefonia e Comunicação': 'Telefone e Comunicação',
}

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


def normalize_text(value):
    text = ' '.join((value or '').replace('\n', ' ').split()).lower()
    decomposed = unicodedata.normalize('NFD', text)
    return ''.join(character for character in decomposed if unicodedata.category(character) != 'Mn')


def contains_any(text, keywords):
    return any(keyword in text for keyword in keywords)


def infer_subcategory(department_name, description):
    text = normalize_text(description)

    if department_name == 'Descartáveis e Embalagens':
        if contains_any(text, ['cumbuca', 'copo']):
            return 'Copos e Cumbucas'
        if contains_any(text, ['sacola', 'filme']):
            return 'Sacolas e Filmes'

    if department_name == 'Eletrodomésticos e Equipamentos':
        if contains_any(text, ['climatizador']):
            return 'Climatizadores'
        if contains_any(text, ['ventilador']):
            return 'Ventiladores'
        if contains_any(text, ['espremedor', 'triturador', 'multiprocessador']):
            return 'Espremedores e Trituradores'
        if contains_any(text, ['tanquinho', 'maquina de lavar', 'secadora']):
            return 'Máquinas de Lavar'
        if contains_any(text, ['bebedouro', 'bebedor', 'purificador']):
            return 'Bebedores e Purificadores'

    if department_name == 'Ferramentas e Construção':
        if contains_any(text, ['acoplamento']):
            return 'Acoplamentos'
        if contains_any(text, ['carro plataforma', 'plataforma']):
            return 'Carros Plataformas'
        if contains_any(text, ['compressor', 'motocompressor']):
            return 'Compressores e Motocompressores'
        if contains_any(text, ['hidraulico', 'torneira', 'valvula', 'mangueira', 'tampao']):
            return 'Materiais Hidráulicos'
        return 'Ferramentas e Acessórios'

    if department_name == 'Informática e Eletrônicos':
        if contains_any(text, ['fragmentadora']):
            return 'Fragmentadoras'
        if contains_any(text, ['impressora', 'cartucho']):
            return 'Impressoras e Suprimentos'
        if contains_any(text, ['microfone', 'pedestal', 'caixa de som', 'acustica']):
            return 'Equipamentos de Áudio'
        return 'Equipamentos e Acessórios de Informática'

    if department_name == 'Limpeza e Utilidades':
        if contains_any(text, ['lixeira', 'lixo', 'cesto', 'balde']):
            return 'Cestos e Lixeiras'

    if department_name == 'Materiais Elétricos':
        if contains_any(text, ['transformador']):
            return 'Transformadores'
        if contains_any(text, ['nobreak', 'estabilizador']):
            return 'Estabilizadores e Nobreaks'
        if contains_any(text, ['mouse', 'teclado', 'headset', 'microfone', 'caixa de som']):
            return None
        if 'cabo' in text:
            return 'Cabos Elétricos'

    if department_name == 'Segurança e Acessórios':
        if contains_any(text, ['biciclet']):
            return 'Bicicletários'
        if contains_any(text, ['descensor', 'talabarte']):
            return 'Descensores e Talabartes'

    if department_name == 'Telefone e Comunicação':
        if contains_any(text, ['galaxy', 'celular', 'smartphone']):
            return 'Aparelhos Celulares'
        return 'Telefonia'

    return None


def clean_description(text):
    cleaned = ' '.join((text or '').replace('\n', ' ').split())
    if cleaned.count('-') >= 4 and cleaned.count(' ') <= 2:
        cleaned = cleaned.replace('-', ' ')
    return cleaned


def build_title(brand, description):
    title = description
    period_index = title.find('. ')
    if 20 <= period_index <= TITLE_MAX_LENGTH:
        title = title[:period_index]
    elif len(title) > TITLE_MAX_LENGTH:
        title = title[: TITLE_MAX_LENGTH - 3].rstrip() + '...'

    if brand and brand.lower() not in title.lower():
        return f'{brand} — {title}'
    return title


def load_catalog_from_json():
    if not os.path.exists(JSON_PATH):
        raise FileNotFoundError(f'JSON não encontrado: {JSON_PATH}')

    with open(JSON_PATH, 'r', encoding='utf-8') as json_file:
        rows = json.load(json_file)

    catalog = []
    seen = set()

    for row in rows:
        department_name = DEPARTMENT_ALIASES.get(row.get('Categoria'), row.get('Categoria'))
        if department_name not in {item[0] for item in DEPARTMENTS}:
            department_name = 'Outros'

        description = clean_description(row.get('Descrição Limpa') or row.get('Descrição Original'))
        brand = (row.get('Marca') or '').strip()
        unique_key = (brand.lower(), description.lower())
        if unique_key in seen or not description:
            continue
        seen.add(unique_key)

        category_name = infer_subcategory(department_name, description) or ''
        catalog.append(
            {
                'departamento': department_name,
                'categoria': category_name,
                'nome': build_title(brand, description),
                'descricao': description,
                'especificacoes': f'Marca: {brand}' if brand else 'Marca: não informada',
                'imagem': PLACEHOLDER_IMAGE,
            }
        )

    return catalog


def write_catalog_csv(catalog):
    with open(CSV_PATH, 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=['departamento', 'categoria', 'nome', 'descricao', 'especificacoes', 'imagem'],
        )
        writer.writeheader()
        writer.writerows(catalog)


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


def seed_products(cursor, department_ids, category_ids, catalog):
    for row in catalog:
        department_name = row['departamento']
        category_name = row['categoria']
        department_id = department_ids.get(department_name)

        if department_id is None:
            print(f'[AVISO] Departamento ignorado: {department_name}')
            continue

        category_id = None
        if category_name:
            category_id = category_ids.get((department_name, category_name))
            if category_id is None:
                print(f'[AVISO] Categoria ignorada: {category_name}')

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
                row['nome'],
                row['descricao'],
                row['especificacoes'],
                row['imagem'],
            ),
        )


def main():
    catalog = load_catalog_from_json()
    write_catalog_csv(catalog)

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    create_tables(cursor)
    department_ids, category_ids = seed_departments(cursor)
    seed_products(cursor, department_ids, category_ids, catalog)

    connection.commit()
    cursor.execute('SELECT COUNT(*) FROM produtos')
    product_count = cursor.fetchone()[0]
    connection.close()

    print(f'[SUCESSO] Banco criado em {DATABASE_PATH} com {product_count} produtos.')


if __name__ == '__main__':
    main()
