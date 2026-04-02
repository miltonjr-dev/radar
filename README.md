# RADAR — Dashboard Comercial

> **R**esultado, **A**nálise e **D**esempenho em **A**tendimento e **R**elacionamento

Dashboard comercial desenvolvido em Python para visualização de indicadores de varejo em tempo real.

---

## Indicadores exibidos

| KPI | Descrição |
|-----|-----------|
| Vendas vs Meta | Comparativo por vendedor no mês atual |
| Evolução Mensal | Tendência de vendas nos últimos 3 meses |
| Taxa de Conversão | % de atendimentos convertidos em venda por vendedor |
| Ticket Médio | Valor médio por pedido por vendedor |
| Vendas Diárias | Histórico dos últimos 30 dias com média móvel 7 dias |
| Carteira de Clientes | Distribuição entre ativos, em risco e inativos |

---

## Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)

---

## Como rodar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Gerar dados simulados
python gerar_dados.py

# 3. Gerar dashboard
python dashboard.py
```

O dashboard será salvo em `output/dashboard_radar.png` e exibido na tela.

---

## Estrutura

```
radar/
├── gerar_dados.py     # Gerador de dados simulados
├── dashboard.py       # Dashboard principal
├── requirements.txt
├── data/              # CSVs gerados
└── output/            # Dashboard exportado
```
