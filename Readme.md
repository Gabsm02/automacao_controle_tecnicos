# 📊 Automação Controle de Técnicos

Projeto desenvolvido em Python para automatizar a consolidação e análise de atividades técnicas provenientes das bases TOA e ETA.

A aplicação realiza o tratamento dos dados, padroniza as informações, consulta dados complementares em uma base DE/PARA e gera uma base consolidada utilizada por um dashboard interativo desenvolvido com Streamlit e Plotly.

---

## 🎯 Objetivo

Centralizar as informações operacionais dos técnicos em uma única base e disponibilizar uma visão gerencial e interativa da operação.

O projeto permite acompanhar:

- Quantidade total de atividades
- Quantidade de técnicos
- Atividades concluídas
- Taxa de conclusão
- Atividades por técnico
- Atividades por coordenador
- Atividades por supervisor
- Atividades por tipo
- Atividades por status
- Atividades por origem
- Atividades por classificação
- Atividades por dia da semana
- Quantidade diária de atividades por técnico

---

## ⚙️ Funcionamento

O projeto possui duas etapas principais:

### 1. Tratamento e consolidação dos dados

O script principal lê as bases:

- `BASE TOA.xlsx`
- `BASE ETA.xlsx`
- `tbDEPARA.xlsx`

Os dados são tratados e consolidados no arquivo:

`Base_Final.xlsx`

Durante o processamento, o sistema:

1. Lê as bases TOA e ETA
2. Seleciona somente as colunas necessárias
3. Padroniza os nomes das colunas
4. Converte as datas
5. Calcula automaticamente o dia da semana
6. Identifica a origem da atividade como TOA ou ETA
7. Mantém o histórico da base consolidada
8. Consulta a base `tbDEPARA`
9. Relaciona `Recurso` com `Nome`
10. Adiciona:
   - COORD
   - Supervisor
   - CLASSIFICACAO
11. Gera/atualiza `Base_Final.xlsx`

---

## 📊 Dashboard

O dashboard foi desenvolvido utilizando Streamlit e Plotly.

O dashboard lê automaticamente:

`Base_Final.xlsx`

e disponibiliza filtros e gráficos interativos.

### Filtros disponíveis

- Técnico
- Tipo
- Origem
- COORD
- Supervisor
- Status
- Classificação
- Dia da Semana

Também existe uma busca rápida pelo nome do técnico.

---

## 📈 Indicadores

O painel apresenta indicadores como:

- 📋 Total de registros
- 👷 Total de técnicos
- ✅ Atividades concluídas
- ⏳ Outros status
- 📈 Taxa de conclusão

Todos os indicadores são atualizados automaticamente conforme os filtros selecionados.

---

## 👷 Análise dos Técnicos por Coordenador

Ao selecionar um coordenador no filtro `COORD`, o dashboard permite analisar os técnicos pertencentes à coordenação selecionada.

A visualização apresenta a quantidade de atividades de cada técnico por data.

Exemplo:

| Técnico | 01/10/2026 | 02/10/2026 | 03/10/2026 | Total |
|---|---:|---:|---:|---:|
| Técnico A | 8 | 5 | 7 | 20 |
| Técnico B | 6 | 9 | 4 | 19 |
| Técnico C | 3 | 5 | 6 | 14 |

Isso permite acompanhar a distribuição diária das atividades dentro de cada coordenação.

---

## 🗂️ Estrutura esperada

```text
automacao_controle_tecnicos/
│
├── index.py
├── dashboard.py
├── requirements.txt
├── README.md
│
├── BASE TOA.xlsx
├── BASE ETA.xlsx
├── tbDEPARA.xlsx
└── Base_Final.xlsx