"""
RADAR — Gerador de dados simulados para varejo
Gera CSVs realistas para demonstração do dashboard
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
import os

np.random.seed(42)

VENDEDORES = ['Carlos Silva', 'Fernanda Lima', 'Ricardo Santos', 'Juliana Rocha', 'André Costa']

PRODUTOS = [
    ('Smartphone Samsung A54', 1299.90),
    ('Notebook Dell Inspiron', 3499.90),
    ('Smart TV 50"', 2199.90),
    ('Fone Bluetooth JBL', 299.90),
    ('Tablet Lenovo', 1599.90),
    ('Câmera GoPro', 1899.90),
    ('Console PlayStation 5', 4299.90),
    ('Smartwatch Xiaomi', 599.90),
    ('Caixa de Som Portátil', 449.90),
    ('Monitor LG 24"', 1099.90),
]

METAS_MENSAIS = {
    'Carlos Silva':   35000,
    'Fernanda Lima':  40000,
    'Ricardo Santos': 30000,
    'Juliana Rocha':  38000,
    'André Costa':    32000,
}


def gerar_vendas():
    registros = []
    hoje = date.today()
    inicio = hoje - timedelta(days=89)

    for vendedor in VENDEDORES:
        # Cada vendedor tem um perfil de desempenho diferente
        perfil = {
            'Carlos Silva':   0.90,
            'Fernanda Lima':  1.10,
            'Ricardo Santos': 0.75,
            'Juliana Rocha':  1.05,
            'André Costa':    0.85,
        }[vendedor]

        dias_ativos = np.random.choice(range(inicio.toordinal(), hoje.toordinal()+1),
                                       size=int(60 * perfil), replace=False)

        for ordinal in dias_ativos:
            dia = date.fromordinal(ordinal)
            n_pedidos = np.random.randint(1, 5)
            for _ in range(n_pedidos):
                produto, preco = PRODUTOS[np.random.randint(0, len(PRODUTOS))]
                qtd = np.random.randint(1, 4)
                desconto = np.random.choice([0, 0, 0, 0.05, 0.10])
                valor = round(preco * qtd * (1 - desconto), 2)
                registros.append({
                    'data': dia,
                    'vendedor': vendedor,
                    'produto': produto,
                    'quantidade': qtd,
                    'valor_unitario': preco,
                    'desconto_pct': desconto,
                    'valor_total': valor,
                    'status': np.random.choice(['Concluído', 'Concluído', 'Concluído', 'Cancelado'],
                                               p=[0.85, 0.05, 0.05, 0.05]),
                })

    df = pd.DataFrame(registros)
    df['data'] = pd.to_datetime(df['data'])
    return df


def gerar_atendimentos():
    registros = []
    hoje = date.today()
    inicio = hoje - timedelta(days=89)

    for vendedor in VENDEDORES:
        perfil = {
            'Carlos Silva':   1.0,
            'Fernanda Lima':  1.2,
            'Ricardo Santos': 0.8,
            'Juliana Rocha':  1.1,
            'André Costa':    0.9,
        }[vendedor]

        n_atendimentos = int(np.random.randint(80, 120) * perfil)
        datas = [date.fromordinal(np.random.randint(inicio.toordinal(), hoje.toordinal()+1))
                 for _ in range(n_atendimentos)]

        for dia in datas:
            convertido = np.random.random() < (0.35 * perfil)
            registros.append({
                'data': dia,
                'vendedor': vendedor,
                'convertido': convertido,
                'canal': np.random.choice(['Loja', 'WhatsApp', 'Telefone', 'Site'],
                                          p=[0.50, 0.25, 0.15, 0.10]),
            })

    df = pd.DataFrame(registros)
    df['data'] = pd.to_datetime(df['data'])
    return df


def gerar_clientes():
    nomes = [
        'Marcos Oliveira', 'Ana Paula', 'Roberto Alves', 'Patrícia Costa', 'Leandro Mendes',
        'Cláudia Ferreira', 'Fernando Dias', 'Simone Nunes', 'Alexandre Lima', 'Beatriz Souza',
        'Eduardo Carvalho', 'Mariana Santos', 'Gustavo Rocha', 'Vanessa Pereira', 'Felipe Torres',
        'Daniela Martins', 'Thiago Barbosa', 'Larissa Ribeiro', 'Bruno Campos', 'Camila Gomes',
        'Paulo Henrique', 'Renata Lopes', 'Diego Araujo', 'Natália Cruz', 'Vinícius Moreira',
        'Isabela Cardoso', 'Rodrigo Pinto', 'Aline Freitas', 'Márcio Teixeira', 'Juliana Ramos',
    ]

    hoje = date.today()
    registros = []
    for i, nome in enumerate(nomes):
        ultima_compra = hoje - timedelta(days=np.random.randint(1, 200))
        registros.append({
            'id': i + 1,
            'nome': nome,
            'vendedor_responsavel': VENDEDORES[i % len(VENDEDORES)],
            'ultima_compra': ultima_compra,
            'total_compras': round(np.random.uniform(500, 15000), 2),
            'qtd_pedidos': np.random.randint(1, 20),
            'dias_sem_comprar': (hoje - ultima_compra).days,
        })

    df = pd.DataFrame(registros)
    df['ultima_compra'] = pd.to_datetime(df['ultima_compra'])
    df['status'] = df['dias_sem_comprar'].apply(
        lambda d: 'Ativo' if d <= 60 else ('Em risco' if d <= 120 else 'Inativo')
    )
    return df


def gerar_metas():
    hoje = date.today()
    registros = []
    for mes_offset in range(3):
        mes = (hoje.month - mes_offset - 1) % 12 + 1
        ano = hoje.year if hoje.month - mes_offset > 0 else hoje.year - 1
        for vendedor, meta in METAS_MENSAIS.items():
            registros.append({
                'ano': ano,
                'mes': mes,
                'vendedor': vendedor,
                'meta': meta,
            })
    return pd.DataFrame(registros)


if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)

    print('Gerando dados...')
    gerar_vendas().to_csv('data/vendas.csv', index=False)
    gerar_atendimentos().to_csv('data/atendimentos.csv', index=False)
    gerar_clientes().to_csv('data/clientes.csv', index=False)
    gerar_metas().to_csv('data/metas.csv', index=False)
    print('Dados gerados em data/')
