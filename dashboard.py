"""
RADAR — Dashboard Comercial
Resultado, Análise e Desempenho em Atendimento e Relacionamento
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
from datetime import date, timedelta
import os

# ── Configuração visual ──────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})

CORES = {
    'primaria':  '#6366f1',
    'sucesso':   '#22c55e',
    'atencao':   '#eab308',
    'perigo':    '#ef4444',
    'fundo':     '#0f172a',
    'card':      '#1e293b',
    'texto':     '#f1f5f9',
    'muted':     '#94a3b8',
}

CORES_VENDEDORES = ['#6366f1', '#22c55e', '#eab308', '#ef4444', '#06b6d4']


# ── Carregamento de dados ────────────────────────────────────────────────────
def carregar_dados():
    vendas = pd.read_csv('data/vendas.csv', parse_dates=['data'])
    atendimentos = pd.read_csv('data/atendimentos.csv', parse_dates=['data'])
    clientes = pd.read_csv('data/clientes.csv', parse_dates=['ultima_compra'])
    metas = pd.read_csv('data/metas.csv')
    return vendas, atendimentos, clientes, metas


# ── KPIs ─────────────────────────────────────────────────────────────────────
def calcular_kpis(vendas, atendimentos, clientes, metas):
    hoje = date.today()
    mes_atual = hoje.month
    ano_atual = hoje.year

    v_mes = vendas[
        (vendas['data'].dt.month == mes_atual) &
        (vendas['data'].dt.year == ano_atual) &
        (vendas['status'] == 'Concluído')
    ]

    total_vendas = v_mes['valor_total'].sum()
    meta_total = metas[(metas['mes'] == mes_atual) & (metas['ano'] == ano_atual)]['meta'].sum()
    ticket_medio = v_mes['valor_total'].mean() if len(v_mes) > 0 else 0
    total_pedidos = len(v_mes)

    at_mes = atendimentos[
        (atendimentos['data'].dt.month == mes_atual) &
        (atendimentos['data'].dt.year == ano_atual)
    ]
    taxa_conversao = at_mes['convertido'].mean() * 100 if len(at_mes) > 0 else 0
    total_atendimentos = len(at_mes)

    inativos = len(clientes[clientes['status'] == 'Inativo'])
    em_risco = len(clientes[clientes['status'] == 'Em risco'])

    return {
        'total_vendas': total_vendas,
        'meta_total': meta_total,
        'pct_meta': (total_vendas / meta_total * 100) if meta_total > 0 else 0,
        'ticket_medio': ticket_medio,
        'total_pedidos': total_pedidos,
        'taxa_conversao': taxa_conversao,
        'total_atendimentos': total_atendimentos,
        'inativos': inativos,
        'em_risco': em_risco,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_brl(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def card_kpi(ax, titulo, valor, subtitulo='', cor=None):
    ax.set_facecolor(CORES['card'])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    cor = cor or CORES['primaria']
    ax.text(0.5, 0.75, valor, ha='center', va='center',
            fontsize=20, fontweight='bold', color=cor)
    ax.text(0.5, 0.40, titulo, ha='center', va='center',
            fontsize=9, color=CORES['muted'])
    if subtitulo:
        ax.text(0.5, 0.18, subtitulo, ha='center', va='center',
                fontsize=8, color=CORES['muted'])


# ── Gráficos ──────────────────────────────────────────────────────────────────
def graf_vendas_vs_meta(ax, vendas, metas):
    hoje = date.today()
    mes, ano = hoje.month, hoje.year

    v = vendas[
        (vendas['data'].dt.month == mes) &
        (vendas['data'].dt.year == ano) &
        (vendas['status'] == 'Concluído')
    ].groupby('vendedor')['valor_total'].sum()

    m = metas[(metas['mes'] == mes) & (metas['ano'] == ano)].set_index('vendedor')['meta']

    vendedores = m.index.tolist()
    vendas_vals = [v.get(vend, 0) for vend in vendedores]
    metas_vals = [m[vend] for vend in vendedores]
    nomes_curtos = [n.split()[0] for n in vendedores]

    x = np.arange(len(vendedores))
    w = 0.35

    barras = ax.bar(x - w/2, vendas_vals, w, label='Vendas', color=CORES_VENDEDORES, alpha=0.85)
    ax.bar(x + w/2, metas_vals, w, label='Meta', color=CORES['muted'], alpha=0.4)

    for bar, val in zip(barras, vendas_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
                fmt_brl(val), ha='center', va='bottom', fontsize=7, color=CORES['texto'])

    ax.set_xticks(x)
    ax.set_xticklabels(nomes_curtos, color=CORES['texto'], fontsize=9)
    ax.set_title('Vendas vs Meta — Mês Atual', color=CORES['texto'], fontsize=10, pad=10)
    ax.set_facecolor(CORES['card'])
    ax.tick_params(colors=CORES['muted'])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'R${v/1000:.0f}k'))
    ax.legend(facecolor=CORES['card'], labelcolor=CORES['texto'], fontsize=8)


def graf_evolucao_mensal(ax, vendas):
    vendas_ok = vendas[vendas['status'] == 'Concluído'].copy()
    vendas_ok['mes_ano'] = vendas_ok['data'].dt.to_period('M')
    mensal = vendas_ok.groupby('mes_ano')['valor_total'].sum().sort_index().tail(3)

    labels = [str(p) for p in mensal.index]
    valores = mensal.values

    ax.plot(labels, valores, color=CORES['primaria'], linewidth=2.5, marker='o',
            markersize=8, markerfacecolor=CORES['primaria'])
    ax.fill_between(labels, valores, alpha=0.15, color=CORES['primaria'])

    for i, (x, y) in enumerate(zip(labels, valores)):
        ax.text(i, y + max(valores)*0.02, fmt_brl(y), ha='center', va='bottom',
                fontsize=8, color=CORES['texto'])

    ax.set_title('Evolução de Vendas — Últimos 3 Meses', color=CORES['texto'], fontsize=10, pad=10)
    ax.set_facecolor(CORES['card'])
    ax.tick_params(colors=CORES['muted'])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'R${v/1000:.0f}k'))


def graf_taxa_conversao(ax, atendimentos):
    por_vendedor = atendimentos.groupby('vendedor').agg(
        total=('convertido', 'count'),
        convertidos=('convertido', 'sum')
    )
    por_vendedor['taxa'] = por_vendedor['convertidos'] / por_vendedor['total'] * 100
    por_vendedor = por_vendedor.sort_values('taxa', ascending=True)
    nomes = [n.split()[0] for n in por_vendedor.index]

    cores = [CORES['sucesso'] if t >= 35 else CORES['atencao'] if t >= 25 else CORES['perigo']
             for t in por_vendedor['taxa']]

    bars = ax.barh(nomes, por_vendedor['taxa'], color=cores, alpha=0.85)

    for bar, val in zip(bars, por_vendedor['taxa']):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}%', va='center', fontsize=9, color=CORES['texto'])

    ax.axvline(35, color=CORES['sucesso'], linestyle='--', alpha=0.5, linewidth=1)
    ax.set_title('Taxa de Conversão por Vendedor (%)', color=CORES['texto'], fontsize=10, pad=10)
    ax.set_facecolor(CORES['card'])
    ax.tick_params(colors=CORES['muted'])
    ax.set_xlim(0, max(por_vendedor['taxa']) * 1.2)


def graf_ticket_medio(ax, vendas):
    v = vendas[vendas['status'] == 'Concluído']
    ticket = v.groupby('vendedor')['valor_total'].mean().sort_values(ascending=False)
    nomes = [n.split()[0] for n in ticket.index]

    bars = ax.bar(nomes, ticket.values, color=CORES_VENDEDORES, alpha=0.85)

    for bar, val in zip(bars, ticket.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                fmt_brl(val), ha='center', va='bottom', fontsize=7, color=CORES['texto'])

    ax.set_title('Ticket Médio por Vendedor', color=CORES['texto'], fontsize=10, pad=10)
    ax.set_facecolor(CORES['card'])
    ax.tick_params(colors=CORES['muted'])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'R${v:.0f}'))


def graf_clientes_inativos(ax, clientes):
    status_count = clientes['status'].value_counts()
    labels = status_count.index.tolist()
    valores = status_count.values
    cores_status = {'Ativo': CORES['sucesso'], 'Em risco': CORES['atencao'], 'Inativo': CORES['perigo']}
    cores = [cores_status.get(l, CORES['muted']) for l in labels]

    wedges, texts, autotexts = ax.pie(
        valores, labels=labels, colors=cores, autopct='%1.0f%%',
        startangle=90, pctdistance=0.75,
        wedgeprops={'width': 0.5, 'edgecolor': CORES['fundo'], 'linewidth': 2}
    )

    for t in texts:
        t.set_color(CORES['texto'])
        t.set_fontsize(9)
    for t in autotexts:
        t.set_color(CORES['fundo'])
        t.set_fontsize(8)
        t.set_fontweight('bold')

    ax.set_title('Carteira de Clientes', color=CORES['texto'], fontsize=10, pad=10)
    ax.set_facecolor(CORES['card'])


def graf_vendas_diarias(ax, vendas):
    hoje = date.today()
    ultimos_30 = hoje - timedelta(days=29)

    v = vendas[
        (vendas['data'] >= pd.Timestamp(ultimos_30)) &
        (vendas['status'] == 'Concluído')
    ].groupby('data')['valor_total'].sum().reset_index()
    v = v.sort_values('data')

    ax.bar(v['data'], v['valor_total'], color=CORES['primaria'], alpha=0.7, width=0.8)
    ax.plot(v['data'], v['valor_total'].rolling(7, min_periods=1).mean(),
            color=CORES['atencao'], linewidth=2, label='Média 7 dias')

    ax.set_title('Vendas Diárias — Últimos 30 Dias', color=CORES['texto'], fontsize=10, pad=10)
    ax.set_facecolor(CORES['card'])
    ax.tick_params(colors=CORES['muted'], labelrotation=30, labelsize=7)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'R${v/1000:.1f}k'))
    ax.legend(facecolor=CORES['card'], labelcolor=CORES['texto'], fontsize=8)


# ── Dashboard principal ───────────────────────────────────────────────────────
def gerar_dashboard():
    vendas, atendimentos, clientes, metas = carregar_dados()
    kpis = calcular_kpis(vendas, atendimentos, clientes, metas)

    fig = plt.figure(figsize=(20, 14), facecolor=CORES['fundo'])
    gs = gridspec.GridSpec(4, 4, figure=fig, hspace=0.55, wspace=0.35,
                           left=0.05, right=0.97, top=0.92, bottom=0.05)

    # Título
    fig.text(0.5, 0.96, 'RADAR — Dashboard Comercial',
             ha='center', fontsize=18, fontweight='bold', color=CORES['texto'])
    fig.text(0.5, 0.935, f'Atualizado em {date.today().strftime("%d/%m/%Y")}',
             ha='center', fontsize=10, color=CORES['muted'])

    # ── Linha 1: KPI Cards ──
    pct_cor = CORES['sucesso'] if kpis['pct_meta'] >= 100 else \
              CORES['atencao'] if kpis['pct_meta'] >= 70 else CORES['perigo']

    card_kpi(fig.add_subplot(gs[0, 0]), 'Vendas no Mês',
             fmt_brl(kpis['total_vendas']),
             f"{kpis['pct_meta']:.1f}% da meta", pct_cor)

    card_kpi(fig.add_subplot(gs[0, 1]), 'Ticket Médio',
             fmt_brl(kpis['ticket_medio']),
             f"{kpis['total_pedidos']} pedidos", CORES['primaria'])

    card_kpi(fig.add_subplot(gs[0, 2]), 'Taxa de Conversão',
             f"{kpis['taxa_conversao']:.1f}%",
             f"{kpis['total_atendimentos']} atendimentos",
             CORES['sucesso'] if kpis['taxa_conversao'] >= 35 else CORES['atencao'])

    card_kpi(fig.add_subplot(gs[0, 3]), 'Clientes Inativos',
             str(kpis['inativos']),
             f"{kpis['em_risco']} em risco", CORES['perigo'])

    # ── Linha 2: Vendas vs Meta | Evolução mensal ──
    graf_vendas_vs_meta(fig.add_subplot(gs[1, :2]), vendas, metas)
    graf_evolucao_mensal(fig.add_subplot(gs[1, 2:]), vendas)

    # ── Linha 3: Conversão | Ticket Médio ──
    graf_taxa_conversao(fig.add_subplot(gs[2, :2]), atendimentos)
    graf_ticket_medio(fig.add_subplot(gs[2, 2:]), vendas)

    # ── Linha 4: Vendas diárias | Carteira de clientes ──
    graf_vendas_diarias(fig.add_subplot(gs[3, :3]), vendas)
    graf_clientes_inativos(fig.add_subplot(gs[3, 3]), clientes)

    os.makedirs('output', exist_ok=True)
    caminho = 'output/dashboard_radar.png'
    plt.savefig(caminho, dpi=150, bbox_inches='tight', facecolor=CORES['fundo'])
    print(f'Dashboard salvo em {caminho}')
    plt.show()


if __name__ == '__main__':
    gerar_dashboard()
