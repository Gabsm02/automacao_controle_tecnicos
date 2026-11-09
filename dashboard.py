import os
import re
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.express as px
import unicodedata

# =========================================================
# 1. PALETA DE CORES
# =========================================================

VIVO_ROXO = "#6E00A7"
VIVO_ROXO_ESCURO = "#400056"
VIVO_MAGENTA = "#D84AFF"
VIVO_LILAS = "#A855F7"
VIVO_LILAS_CLARO = "#E9D5FF"
VIVO_FUNDO = "#F8F5FA"
VIVO_BRANCO = "#FFFFFF"
VIVO_TEXTO = "#2D1B33"
VIVO_CINZA = "#6B7280"


PALETA_VIVO = [
    VIVO_ROXO,
    VIVO_MAGENTA,
    VIVO_ROXO_ESCURO,
    VIVO_LILAS,
    "#9333EA",
    "#C026D3",
    "#7E22CE",
    "#E879F9",
]


ESCALA_VIVO = [
    [0.00, "#F8F5FA"],
    [0.15, "#F3E8FF"],
    [0.30, "#E9D5FF"],
    [0.45, "#D8B4FE"],
    [0.60, "#C084FC"],
    [0.75, "#A855F7"],
    [0.88, "#6E00A7"],
    [1.00, "#400056"],
]


# Status da força de trabalho: (fundo da célula, texto, cor do gráfico)
CORES_PRESENCA = {
    "ATIVO": ("#DCFCE7", "#166534", "#16A34A"),
    "SOBRE AVISO": ("#FEF3C7", "#92400E", "#F59E0B"),
    "BH": ("#E9D5FF", VIVO_ROXO_ESCURO, VIVO_LILAS),
    "FOLGA": ("#F3F4F6", "#4B5563", "#9CA3AF"),
    "FÉRIAS": ("#DBEAFE", "#1E40AF", "#3B82F6"),
    "ATESTADO": ("#FEE2E2", "#991B1B", "#DC2626"),
}


# =========================================================
# 2. CONFIGURACAO DA PAGINA
# =========================================================

st.set_page_config(page_title="Controle de Técnicos", page_icon="📊", layout="wide")


# =========================================================
# 3. ESTILO DO DASHBOARD
# =========================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {VIVO_FUNDO};
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    h1,
    h2,
    h3 {{
        color: {VIVO_ROXO_ESCURO};
    }}

    [data-testid="stMetric"] {{
        background-color: {VIVO_BRANCO};
        border: 1px solid {VIVO_LILAS_CLARO};
        border-left: 5px solid {VIVO_ROXO};
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 3px 10px rgba(64, 0, 86, 0.08);
    }}

    div[data-testid="stMetricValue"] {{
        font-size: 30px;
        font-weight: 700;
        color: {VIVO_ROXO};
    }}

    div[data-testid="stMetricLabel"] {{
        color: {VIVO_TEXTO};
        font-weight: 600;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {VIVO_BRANCO};
        border-right: 1px solid {VIVO_LILAS_CLARO};
    }}

    section[data-testid="stSidebar"] h1 {{
        color: {VIVO_ROXO};
    }}

    .stDownloadButton > button {{
        background-color: {VIVO_ROXO};
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }}

    .stDownloadButton > button:hover {{
        background-color: {VIVO_ROXO_ESCURO};
        color: white;
        border: none;
    }}

    hr {{
        border-color: {VIVO_LILAS_CLARO};
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 4. TITULO
# =========================================================

st.title("📊 Controle de Técnicos")

st.caption(
    "Acompanhamento das atividades TOA e ETA por técnico, "
    "tipo, coordenação, supervisor e classificação."
)


# =========================================================
# 5. ARQUIVO
# =========================================================

arquivo = "Base_Final.xlsx"
ARQUIVO_FORCA_TRABALHO = "PRODUÇÃO B2B-OUTUBRO.xlsx"
ARQUIVO_CADERNO = "Caderno B2B_tempo.xlsx"


def versao_arquivo(caminho):

    # A data de modificação entra como argumento das funções com cache:
    # quando a planilha é salva de novo, o Streamlit relê o arquivo.
    try:
        return os.path.getmtime(caminho)
    except OSError:
        return None


# Metas financeiras por coordenador, indexadas pelo primeiro nome normalizado.
METAS_COORDENADOR = {
    "DIEGO": 72000,
    "RICARDO": 198000,
    "WEDSON": 144000,
}


# =========================================================
# 6. CARREGAR BASE
# =========================================================


@st.cache_data
def carregar_base(versao):

    df = pd.read_excel(arquivo, engine="openpyxl")

    df.columns = df.columns.astype(str).str.strip()

    return df


try:

    base = carregar_base(versao_arquivo(arquivo))

except FileNotFoundError:

    st.error(f"O arquivo '{arquivo}' não foi encontrado.")

    st.stop()

except Exception as erro:

    st.error(f"Erro ao carregar a base: {erro}")

    st.stop()


@st.cache_data
def carregar_forca_trabalho(versao):

    df = pd.read_excel(
        ARQUIVO_FORCA_TRABALHO,
        sheet_name="FORÇA DE TRABALHO",
        header=13,
        engine="openpyxl",
    )

    df.columns = df.columns.astype(str).str.strip()

    return df


def normalizar_nome(texto):

    if pd.isna(texto):
        return ""

    texto = str(texto).strip().upper()

    texto = "".join(
        c
        for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )

    return texto


def formatar_moeda(valor):

    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_numero(valor, casas=2):

    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


@st.cache_data
def carregar_caderno(versao):

    # A aba "Planilha1" relaciona cada Tipo da Base_Final com sua
    # pontuação e valor. Tipos marcados como "NA" não pontuam.
    df = pd.read_excel(
        ARQUIVO_CADERNO,
        sheet_name="Planilha1",
        engine="openpyxl",
    )

    df.columns = df.columns.astype(str).str.strip()

    df["CHAVE_TIPO"] = df["Tipo"].apply(normalizar_nome)
    df["Pontuação"] = pd.to_numeric(df["PONTUAÇÃO"], errors="coerce").fillna(0)
    df["Valor"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)

    return (
        df[df["CHAVE_TIPO"] != ""]
        .drop_duplicates("CHAVE_TIPO")[["Tipo", "CHAVE_TIPO", "Pontuação", "Valor"]]
        .reset_index(drop=True)
    )


@st.cache_data
def carregar_presenca(versao):

    # Converte a matriz Nome x Data da força de trabalho em uma linha
    # por técnico e dia. Alguns cabeçalhos vêm como "07/10/20262",
    # por isso a data é extraída por expressão regular.
    df = carregar_forca_trabalho(versao)

    df = df[df["Nome"].notna()].copy()

    colunas_data = {}

    for coluna in df.columns:

        if isinstance(coluna, datetime):

            colunas_data[coluna] = pd.Timestamp(coluna).normalize()

            continue

        encontrado = re.search(r"\d{2}/\d{2}/\d{4}", str(coluna))

        if encontrado:

            colunas_data[coluna] = pd.to_datetime(
                encontrado.group(), format="%d/%m/%Y"
            )

    presenca = df.melt(
        id_vars=["Nome"],
        value_vars=list(colunas_data),
        var_name="Coluna",
        value_name="Presença",
    )

    presenca["Data"] = presenca["Coluna"].map(colunas_data)
    presenca["Presença"] = (
        presenca["Presença"].fillna("").astype(str).str.strip().str.upper()
    )
    presenca["CHAVE"] = presenca["Nome"].apply(normalizar_nome)

    return presenca[["CHAVE", "Nome", "Data", "Presença"]]


forca_trabalho = carregar_forca_trabalho(versao_arquivo(ARQUIVO_FORCA_TRABALHO)).copy()

forca_trabalho["CHAVE"] = forca_trabalho["Nome"].apply(normalizar_nome)

colunas_datas = [coluna for coluna in forca_trabalho.columns if "/" in str(coluna)]

forca_trabalho["Dias Trabalhados"] = (
    forca_trabalho[colunas_datas]
    .astype(str)
    .apply(lambda coluna: coluna.str.upper().str.strip())
    .eq("ATIVO")
    .sum(axis=1)
)

dias_trabalhados = forca_trabalho[["CHAVE", "Dias Trabalhados"]].copy()


# =========================================================
# 7. VERIFICANDO COLUNAS
# =========================================================

colunas_necessarias = [
    "Recurso",
    "Tipo",
    "Tipo_Padronizado",
    "Status",
    "Data Concluída",
    "Origem",
    "Dia Semana",
    "COORD",
    "Supervisor",
    "CLASSIFICACAO",
]


colunas_faltando = [
    coluna for coluna in colunas_necessarias if coluna not in base.columns
]


if colunas_faltando:

    st.error("Algumas colunas necessárias não foram encontradas " "na Base_Final.xlsx.")

    st.write("Colunas faltando:", colunas_faltando)

    st.write("Colunas encontradas:", list(base.columns))

    st.stop()


# =========================================================
# 8. TRATAMENTO DOS DADOS DE TEXTO
# =========================================================

colunas_texto = [
    "Recurso",
    "Tipo",
    "Tipo_Padronizado",
    "Status",
    "Origem",
    "Dia Semana",
    "COORD",
    "Supervisor",
    "CLASSIFICACAO",
]


for coluna in colunas_texto:

    base[coluna] = base[coluna].fillna("").astype(str).str.strip()


# =========================================================
# 9. TRATAMENTO DA DATA
# =========================================================

base["Data Concluída"] = pd.to_datetime(
    base["Data Concluída"], errors="coerce", dayfirst=True
)


# =========================================================
# 9.1 PONTUACAO E VALOR (CADERNO B2B)
# =========================================================

try:

    caderno = carregar_caderno(versao_arquivo(ARQUIVO_CADERNO))

except Exception as erro:

    st.error(f"Erro ao carregar o Caderno B2B_tempo.xlsx: {erro}")

    st.stop()


base["CHAVE"] = base["Recurso"].apply(normalizar_nome)

base["CHAVE_TIPO"] = base["Tipo"].apply(normalizar_nome)

base = base.merge(
    caderno[["CHAVE_TIPO", "Pontuação", "Valor"]], on="CHAVE_TIPO", how="left"
).drop(columns=["CHAVE_TIPO"])

# Somente atividades concluídas geram pontuação e valor.
atividade_concluida = base["Status"].apply(normalizar_nome).eq("CONCLUIDA")

base["Pontuação"] = base["Pontuação"].fillna(0).where(atividade_concluida, 0)

base["Valor"] = base["Valor"].fillna(0).where(atividade_concluida, 0)


# =========================================================
# 9.2 PRESENCA DIARIA (FORCA DE TRABALHO)
# =========================================================

# COORD, Supervisor e Classificação vêm da Base_Final para que a
# presença responda aos mesmos filtros do restante do painel.
cadastro_tecnicos = (
    base[base["CHAVE"] != ""]
    .groupby("CHAVE")[["Recurso", "COORD", "Supervisor", "CLASSIFICACAO"]]
    .first()
)

presenca = carregar_presenca(versao_arquivo(ARQUIVO_FORCA_TRABALHO)).merge(
    cadastro_tecnicos, left_on="CHAVE", right_index=True, how="left"
)

presenca["Recurso"] = presenca["Recurso"].fillna(presenca["Nome"])

for coluna in ["COORD", "Supervisor", "CLASSIFICACAO"]:

    presenca[coluna] = presenca[coluna].fillna("")


# =========================================================
# 10. FUNCAO PARA PEGAR VALORES VALIDOS
# =========================================================


def valores_validos(df, coluna):

    valores = (
        df.loc[df[coluna].astype(str).str.strip().ne(""), coluna]
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    return sorted(valores)


# =========================================================
# 11. SIDEBAR
# =========================================================

st.sidebar.title("🔎 Filtros")

st.sidebar.caption("Utilize os filtros para analisar a operação.")


# =========================================================
# 12. BUSCA RAPIDA POR TECNICO
# =========================================================

busca_recurso = st.sidebar.text_input(
    "🔍 Buscar técnico", placeholder="Digite parte do nome..."
)


# =========================================================
# 13. LISTAS DOS FILTROS
# =========================================================

lista_tecnicos = valores_validos(base, "Recurso")

lista_tipo = valores_validos(base, "Tipo_Padronizado")

lista_origem = valores_validos(base, "Origem")

lista_coord = valores_validos(base, "COORD")

lista_supervisor = valores_validos(base, "Supervisor")

lista_status = valores_validos(base, "Status")

lista_classificacao = valores_validos(base, "CLASSIFICACAO")


# =========================================================
# 14. ORDEM DOS DIAS DA SEMANA
# =========================================================

ordem_dias = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


dias_existentes = valores_validos(base, "Dia Semana")


lista_dias = [dia for dia in ordem_dias if dia in dias_existentes]


for dia in dias_existentes:

    if dia not in lista_dias:

        lista_dias.append(dia)


# =========================================================
# 15. FILTRO TECNICO
# =========================================================

tecnicos_selecionados = st.sidebar.multiselect(
    "👷 Técnico", lista_tecnicos, default=[], placeholder="Todos os técnicos"
)


# =========================================================
# 16. FILTRO TIPO
# =========================================================

tipo = st.sidebar.multiselect(
    "Tipo de Atividade", lista_tipo, default=[], placeholder="Todos os tipos"
)


# =========================================================
# 17. FILTRO ORIGEM
# =========================================================

origem = st.sidebar.multiselect(
    "Origem", lista_origem, default=[], placeholder="Todas as origens"
)


# =========================================================
# 18. FILTRO COORD
# =========================================================

coord = st.sidebar.multiselect(
    "COORD", lista_coord, default=[], placeholder="Todos os coordenadores"
)


# =========================================================
# 19. FILTRO SUPERVISOR
# =========================================================

supervisor = st.sidebar.multiselect(
    "Supervisor", lista_supervisor, default=[], placeholder="Todos os supervisores"
)


# =========================================================
# 20. FILTRO STATUS
# =========================================================

status = st.sidebar.multiselect(
    "Status", lista_status, default=[], placeholder="Todos os status"
)


# =========================================================
# 21. FILTRO CLASSIFICACAO
# =========================================================

classificacao = st.sidebar.multiselect(
    "Classificação",
    lista_classificacao,
    default=[],
    placeholder="Todas as classificações",
)


# =========================================================
# 22. FILTRO DIA DA SEMANA
# =========================================================

dia_semana = st.sidebar.multiselect(
    "Dia da Semana", lista_dias, default=[], placeholder="Todos os dias"
)


# =========================================================
# 23. FILTRO DE PERIODO
# =========================================================

datas_validas = base["Data Concluída"].dropna()


if not datas_validas.empty:

    data_minima = datas_validas.min().date()

    data_maxima = datas_validas.max().date()

    periodo = st.sidebar.date_input(
        "📅 Período",
        value=(data_minima, data_maxima),
        min_value=data_minima,
        max_value=data_maxima,
        format="DD/MM/YYYY",
    )

else:

    periodo = None


# =========================================================
# 24. APLICANDO FILTROS
# =========================================================

df = base.copy()


if busca_recurso:

    df = df[df["Recurso"].str.contains(busca_recurso, case=False, na=False)]


if tecnicos_selecionados:

    df = df[df["Recurso"].isin(tecnicos_selecionados)]


if tipo:

    df = df[df["Tipo_Padronizado"].isin(tipo)]


if origem:

    df = df[df["Origem"].isin(origem)]


if coord:

    df = df[df["COORD"].isin(coord)]


if supervisor:

    df = df[df["Supervisor"].isin(supervisor)]


if status:

    df = df[df["Status"].isin(status)]


if classificacao:

    df = df[df["CLASSIFICACAO"].isin(classificacao)]


if dia_semana:

    df = df[df["Dia Semana"].isin(dia_semana)]


if periodo and isinstance(periodo, (list, tuple)) and len(periodo) == 2:

    data_inicio = pd.Timestamp(periodo[0])

    data_fim = pd.Timestamp(periodo[1])

    df = df[(df["Data Concluída"] >= data_inicio) & (df["Data Concluída"] <= data_fim)]


# =========================================================
# 24.1 APLICANDO FILTROS NA PRESENCA
# =========================================================

# Filtros de técnico e de data. Tipo, Origem e Status são atributos
# da atividade e não se aplicam à presença.
df_presenca = presenca.copy()


if busca_recurso:

    df_presenca = df_presenca[
        df_presenca["Recurso"].str.contains(busca_recurso, case=False, na=False)
    ]


if tecnicos_selecionados:

    df_presenca = df_presenca[df_presenca["Recurso"].isin(tecnicos_selecionados)]


if coord:

    df_presenca = df_presenca[df_presenca["COORD"].isin(coord)]


if supervisor:

    df_presenca = df_presenca[df_presenca["Supervisor"].isin(supervisor)]


if classificacao:

    df_presenca = df_presenca[df_presenca["CLASSIFICACAO"].isin(classificacao)]


if dia_semana:

    df_presenca = df_presenca[
        df_presenca["Data"].dt.weekday.map(dict(enumerate(ordem_dias))).isin(
            dia_semana
        )
    ]


if periodo and isinstance(periodo, (list, tuple)) and len(periodo) == 2:

    df_presenca = df_presenca[
        (df_presenca["Data"] >= data_inicio) & (df_presenca["Data"] <= data_fim)
    ]


# =========================================================
# 25. INDICADORES GERAIS
# =========================================================

total_registros = len(df)


total_tecnicos = df.loc[df["Recurso"] != "", "Recurso"].nunique()


df_concluidos = df[df["Status"].str.contains("conclu", case=False, na=False)]


total_concluidos = len(df_concluidos)


total_outros = total_registros - total_concluidos


if total_registros > 0:

    taxa_conclusao = (total_concluidos / total_registros) * 100

else:

    taxa_conclusao = 0


# =========================================================
# 26. CARDS PRINCIPAIS
# =========================================================

col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric("📋 Registros", f"{total_registros:,}".replace(",", "."))


with col2:

    st.metric("👷 Técnicos", f"{total_tecnicos:,}".replace(",", "."))


with col3:

    st.metric("✅ Concluídos", f"{total_concluidos:,}".replace(",", "."))


with col4:

    st.metric("⏳ Outros Status", f"{total_outros:,}".replace(",", "."))


with col5:

    st.metric("📈 Taxa conclusão", f"{taxa_conclusao:.1f}%")


# =========================================================
# 26.1 CARDS DE PONTUACAO, VALOR E PRESENCA
# =========================================================

total_pontuacao = df["Pontuação"].sum()

total_valor = df["Valor"].sum()

total_dias_presenca = len(df_presenca[df_presenca["Presença"] != ""])

total_dias_ativo = int(df_presenca["Presença"].eq("ATIVO").sum())

if total_dias_presenca > 0:

    taxa_presenca = (total_dias_ativo / total_dias_presenca) * 100

else:

    taxa_presenca = 0


# Sem filtro de COORD, a meta exibida e a soma de todos os coordenadores.
coordenadores_meta = coord if coord else list(lista_coord)

meta_financeira = sum(
    METAS_COORDENADOR.get(normalizar_nome(c).split(" ")[0], 0)
    for c in coordenadores_meta
)

if meta_financeira > 0:

    atingimento_meta = (total_valor / meta_financeira) * 100

else:

    atingimento_meta = None

# Gap positivo indica quanto falta para a meta; negativo, quanto foi superado.
gap_meta = meta_financeira - total_valor


col6, col7, col8, col9, col10 = st.columns(5)


with col6:

    st.metric("🏆 Pontuação", formatar_numero(total_pontuacao))


with col7:

    st.metric("💰 Valor", formatar_moeda(total_valor))


with col8:

    st.metric(
        "🙋 Presença (força de trabalho)",
        f"{taxa_presenca:.1f}%",
        help="Dias com status ATIVO sobre o total de dias registrados "
        "na aba FORÇA DE TRABALHO, dentro dos filtros selecionados.",
    )


with col9:

    st.metric(
        "🎯 Meta financeira",
        formatar_moeda(meta_financeira) if meta_financeira > 0 else "—",
        delta=(
            f"{formatar_numero(atingimento_meta, 1)}% atingido"
            if atingimento_meta is not None
            else None
        ),
        delta_color="off",
        help="Meta do(s) coordenador(es) filtrado(s): Diego R$ 72 mil, "
        "Ricardo R$ 198 mil e Wedson R$ 144 mil. Sem filtro, exibe a soma "
        "das metas. O percentual compara o Valor com a meta.",
    )


with col10:

    if meta_financeira <= 0:

        st.metric("📉 Gap da meta", "—")

    elif gap_meta > 0:

        st.metric(
            "📉 Gap da meta",
            formatar_moeda(gap_meta),
            delta=f"-{formatar_numero(gap_meta / meta_financeira * 100, 1)}% para a meta",
            help="Diferença entre a meta financeira e o Valor realizado.",
        )

    else:

        st.metric(
            "📉 Gap da meta",
            "+" + formatar_moeda(-gap_meta),
            delta="Meta batida",
            help="Valor realizado acima da meta financeira.",
        )


st.divider()


# =========================================================
# 27. PRIMEIRA LINHA DE GRAFICOS
# =========================================================

grafico1, grafico2 = st.columns([2, 1])


# =========================================================
# 28. ATIVIDADES POR SUPERVISOR
# =========================================================

with grafico1:

    st.subheader("Atividades por Supervisor")

    df_supervisor = df[df["Supervisor"] != ""].copy()

    if not df_supervisor.empty:

        supervisor_df = (
            df_supervisor.groupby("Supervisor")
            .size()
            .reset_index(name="Quantidade")
            .sort_values("Quantidade", ascending=False)
        )

        fig_supervisor = px.bar(
            supervisor_df,
            x="Supervisor",
            y="Quantidade",
            text="Quantidade",
            color="Quantidade",
            color_continuous_scale=ESCALA_VIVO,
        )

        fig_supervisor.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Supervisor",
            yaxis_title="Quantidade de Atividades",
        )

        fig_supervisor.update_traces(textposition="outside")

        st.plotly_chart(fig_supervisor, use_container_width=True)

    else:

        st.info("Nenhuma informação de Supervisor.")


# =========================================================
# 29. ORIGEM DAS ATIVIDADES
# =========================================================

with grafico2:

    st.subheader("Origem das Atividades")

    df_origem = df[df["Origem"] != ""].copy()

    if not df_origem.empty:

        origem_df = df_origem.groupby("Origem").size().reset_index(name="Quantidade")

        fig_origem = px.pie(
            origem_df,
            names="Origem",
            values="Quantidade",
            hole=0.55,
            color_discrete_sequence=PALETA_VIVO,
        )

        fig_origem.update_traces(
            textinfo="percent+label", marker=dict(line=dict(color=VIVO_BRANCO, width=2))
        )

        st.plotly_chart(fig_origem, use_container_width=True)

    else:

        st.info("Nenhuma informação de Origem.")


# =========================================================
# 30. SEGUNDA LINHA DE GRAFICOS
# =========================================================

grafico3, grafico4 = st.columns(2)


# =========================================================
# 31. ATIVIDADES POR COORD
# =========================================================

with grafico3:

    st.subheader("Atividades por COORD")

    df_coord = df[df["COORD"] != ""].copy()

    if not df_coord.empty:

        coord_df = (
            df_coord.groupby("COORD")
            .size()
            .reset_index(name="Quantidade")
            .sort_values("Quantidade", ascending=True)
        )

        fig_coord = px.bar(
            coord_df,
            x="Quantidade",
            y="COORD",
            orientation="h",
            text="Quantidade",
            color="Quantidade",
            color_continuous_scale=ESCALA_VIVO,
        )

        fig_coord.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Quantidade de Atividades",
            yaxis_title="COORD",
        )

        fig_coord.update_traces(textposition="outside")

        st.plotly_chart(fig_coord, use_container_width=True)

    else:

        st.info("Nenhuma informação de COORD.")


# =========================================================
# 32. DISTRIBUICAO POR CLASSIFICACAO
# =========================================================

with grafico4:

    st.subheader("Distribuição por Classificação")

    df_classificacao = df[df["CLASSIFICACAO"] != ""].copy()

    if not df_classificacao.empty:

        classificacao_df = (
            df_classificacao.groupby("CLASSIFICACAO")
            .size()
            .reset_index(name="Quantidade")
            .sort_values("Quantidade", ascending=False)
        )

        fig_classificacao = px.bar(
            classificacao_df,
            x="CLASSIFICACAO",
            y="Quantidade",
            text="Quantidade",
            color="CLASSIFICACAO",
            color_discrete_sequence=PALETA_VIVO,
        )

        fig_classificacao.update_layout(
            showlegend=False, xaxis_title="Classificação", yaxis_title="Quantidade"
        )

        fig_classificacao.update_traces(textposition="outside")

        st.plotly_chart(fig_classificacao, use_container_width=True)

    else:

        st.info("Nenhuma informação de Classificação.")


# =========================================================
# 33. TERCEIRA LINHA DE GRAFICOS
# =========================================================

grafico5, grafico6 = st.columns(2)


# =========================================================
# 34. ATIVIDADES POR TIPO
# =========================================================

with grafico5:

    st.subheader("Atividades por Tipo")

    df_tipo = df[df["Tipo_Padronizado"] != ""].copy()

    if not df_tipo.empty:

        tipo_df = (
            df_tipo.groupby("Tipo_Padronizado")
            .size()
            .reset_index(name="Quantidade")
            .sort_values("Quantidade", ascending=True)
        )

        fig_tipo = px.bar(
            tipo_df,
            x="Quantidade",
            y="Tipo_Padronizado",
            orientation="h",
            text="Quantidade",
            color="Quantidade",
            color_continuous_scale=ESCALA_VIVO,
        )

        fig_tipo.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Quantidade",
            yaxis_title="Tipo Padronizado",
        )

        fig_tipo.update_traces(textposition="outside")

        st.plotly_chart(fig_tipo, use_container_width=True)

    else:

        st.info("Nenhuma informação de Tipo.")


# =========================================================
# 35. DISTRIBUICAO POR STATUS
# =========================================================

with grafico6:

    st.subheader("Distribuição por Status")

    df_status = df[df["Status"] != ""].copy()

    if not df_status.empty:

        status_df = (
            df_status.groupby("Status")
            .size()
            .reset_index(name="Quantidade")
            .sort_values("Quantidade", ascending=False)
        )

        fig_status = px.bar(
            status_df,
            x="Status",
            y="Quantidade",
            text="Quantidade",
            color="Status",
            color_discrete_sequence=PALETA_VIVO,
        )

        fig_status.update_layout(
            showlegend=False, xaxis_title="Status", yaxis_title="Quantidade"
        )

        fig_status.update_traces(textposition="outside")

        st.plotly_chart(fig_status, use_container_width=True)

    else:

        st.info("Nenhuma informação de Status.")


# =========================================================
# 36. ATIVIDADES POR DIA DA SEMANA
# =========================================================

st.divider()

st.subheader("📅 Atividades por Dia da Semana")


df_dias = df[df["Dia Semana"] != ""].copy()


if not df_dias.empty:

    dias_df = df_dias.groupby("Dia Semana").size().reset_index(name="Quantidade")

    dias_df["Dia Semana"] = pd.Categorical(
        dias_df["Dia Semana"], categories=ordem_dias, ordered=True
    )

    dias_df = dias_df.dropna(subset=["Dia Semana"]).sort_values("Dia Semana")

    if not dias_df.empty:

        fig_dias = px.line(
            dias_df, x="Dia Semana", y="Quantidade", markers=True, text="Quantidade"
        )

        fig_dias.update_layout(
            xaxis_title="Dia da Semana", yaxis_title="Quantidade de Atividades"
        )

        fig_dias.update_traces(
            line=dict(width=4, color=VIVO_ROXO),
            marker=dict(
                size=11, color=VIVO_MAGENTA, line=dict(width=2, color=VIVO_ROXO_ESCURO)
            ),
            textposition="top center",
        )

        st.plotly_chart(fig_dias, use_container_width=True)

    else:

        st.info("Nenhum dia da semana válido encontrado.")

else:

    st.info("Nenhuma informação de Dia da Semana.")


# =========================================================
# 37. PRODUTIVIDADE DOS TECNICOS
# =========================================================

st.divider()

st.subheader("👷 Produtividade dos Técnicos")

st.caption(
    "A análise respeita todos os filtros selecionados, "
    "incluindo COORD, Supervisor, Técnico, Tipo de Atividade, "
    "Origem, Status, Classificação, Dia da Semana e Período."
)


df_produtividade = df[(df["Recurso"] != "") & (df["Data Concluída"].notna())].copy()


if not df_produtividade.empty:

    # =====================================================
    # 38. DATA SEM HORARIO
    # =====================================================

    df_produtividade["Data"] = df_produtividade["Data Concluída"].dt.normalize()

    # =====================================================
    # 39. ATIVIDADES POR TECNICO E DATA
    # =====================================================

    st.markdown("### 🔥 Atividades por Técnico e Data")

    st.caption(
        "Selecione um coordenador para visualizar o Heatmap "
        "com os técnicos vinculados a ele."
    )

    coordenadores_heatmap = (
        df_produtividade.loc[df_produtividade["COORD"] != "", "COORD"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    coordenadores_heatmap = sorted(coordenadores_heatmap)

    coordenador_heatmap = st.selectbox(
        "🔎 Coordenador",
        options=coordenadores_heatmap,
        index=None,
        placeholder="Selecione um coordenador...",
        key="coordenador_heatmap",
    )

    if coordenador_heatmap:

        df_heatmap = df_produtividade[
            df_produtividade["COORD"] == coordenador_heatmap
        ].copy()

        total_atividades_tecnico = (
            df_heatmap.groupby("Recurso")
            .size()
            .reset_index(name="Quantidade")
            .sort_values("Quantidade", ascending=False)
        )

        total_tecnicos_coord = df_heatmap["Recurso"].nunique()

        total_atividades_coord = len(df_heatmap)

        indicador_coord1, indicador_coord2 = st.columns(2)

        with indicador_coord1:

            st.metric("👷 Técnicos do Coordenador", total_tecnicos_coord)

        with indicador_coord2:

            st.metric("📋 Atividades", f"{total_atividades_coord:,}".replace(",", "."))

        heatmap_df = (
            df_heatmap.groupby(["Recurso", "Data"])
            .size()
            .reset_index(name="Quantidade")
        )

        heatmap_pivot = heatmap_df.pivot_table(
            index="Recurso",
            columns="Data",
            values="Quantidade",
            fill_value=0,
            aggfunc="sum",
        )

        heatmap_pivot = heatmap_pivot.sort_index(axis=1)

        ordem_tecnicos = total_atividades_tecnico["Recurso"].tolist()

        ordem_tecnicos = [
            tecnico for tecnico in ordem_tecnicos if tecnico in heatmap_pivot.index
        ]

        heatmap_pivot = heatmap_pivot.loc[ordem_tecnicos]

        heatmap_pivot.columns = [
            data.strftime("%d/%m") for data in heatmap_pivot.columns
        ]

        fig_heatmap = px.imshow(
            heatmap_pivot,
            text_auto=True,
            aspect="auto",
            color_continuous_scale=ESCALA_VIVO,
            labels={"x": "Data", "y": "Técnico", "color": "Atividades"},
        )

        altura_heatmap = max(400, len(heatmap_pivot) * 45)

        fig_heatmap.update_layout(
            height=altura_heatmap,
            xaxis_title="Data",
            yaxis_title="Técnico",
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=50, b=20),
        )

        fig_heatmap.update_xaxes(side="top", tickangle=-45)

        st.plotly_chart(fig_heatmap, use_container_width=True)

        # ================================================
        # QUANTIDADE DIARIA POR TECNICO
        # ================================================

        st.markdown("### 📋 Quantidade Diária por Técnico")

        tabela_diaria = heatmap_pivot.copy()

        tabela_diaria["TOTAL"] = tabela_diaria.sum(axis=1)

        tabela_diaria = tabela_diaria.sort_values("TOTAL", ascending=False)

        st.dataframe(tabela_diaria, use_container_width=True)

    else:

        st.info(
            "👆 Selecione um coordenador para visualizar " "as atividades dos técnicos."
        )

    # =====================================================
    # 40. MEDIA PRODUTIVA POR TECNICO
    # =====================================================

    st.divider()
    st.subheader("📈 Média Produtiva por Técnico")

    st.caption(
        "Selecione um coordenador para visualizar a média produtiva dos técnicos "
        "vinculados a ele. A média considera somente colaboradores presentes "
        "na Base_Final e na base de força de trabalho, dividindo o total de "
        "atividades pelos dias com status ATIVO."
    )

    # =====================================================
    # INTERSECAO: BASE FINAL X FORCA DE TRABALHO
    # =====================================================

    chaves_forca = set(
        forca_trabalho.loc[forca_trabalho["CHAVE"] != "", "CHAVE"]
        .dropna()
        .astype(str)
        .tolist()
    )

    df_produtividade_media = df_produtividade.copy()
    df_produtividade_media["CHAVE"] = (
        df_produtividade_media["Recurso"].apply(normalizar_nome)
    )

    # Só permanecem colaboradores existentes nas duas bases.
    df_produtividade_media = df_produtividade_media[
        df_produtividade_media["CHAVE"].isin(chaves_forca)
    ].copy()

    # A lista de coordenadores nasce da interseção acima.
    coordenadores_media = sorted(
        df_produtividade_media.loc[
            df_produtividade_media["COORD"] != "", "COORD"
        ]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    if not coordenadores_media:
        st.info(
            "Nenhum coordenador possui colaboradores presentes simultaneamente "
            "na Base_Final e na base de força de trabalho."
        )
    else:
        coordenador_media = st.selectbox(
            "🔎 Coordenador",
            options=coordenadores_media,
            index=None,
            placeholder="Selecione um coordenador...",
            key="coordenador_media",
        )

        if coordenador_media:
            df_media = df_produtividade_media[
                df_produtividade_media["COORD"] == coordenador_media
            ].copy()

            total_por_tecnico = (
                df_media.groupby(["Recurso", "CHAVE"])
                .size()
                .reset_index(name="Total Atividades")
            )

            # Inner: ignora colaboradores que não estejam na força de trabalho.
            media_produtiva = total_por_tecnico.merge(
                dias_trabalhados,
                on="CHAVE",
                how="inner",
            )

            # Sem dias ATIVO, o colaborador não entra na média.
            media_produtiva = media_produtiva[
                media_produtiva["Dias Trabalhados"] > 0
            ].copy()

            if media_produtiva.empty:
                st.info(
                    "Nenhum colaborador do coordenador selecionado possui dias "
                    "com status ATIVO na base de força de trabalho."
                )
            else:
                media_produtiva["Média Diária"] = (
                    media_produtiva["Total Atividades"]
                    / media_produtiva["Dias Trabalhados"]
                ).round(2)

                media_produtiva = (
                    media_produtiva.drop(columns=["CHAVE"], errors="ignore")
                    .sort_values(
                        ["Média Diária", "Total Atividades"],
                        ascending=[False, False],
                    )
                    .reset_index(drop=True)
                )

                media_geral = media_produtiva["Média Diária"].mean()
                maior_media = media_produtiva["Média Diária"].max()
                tecnico_maior_media = media_produtiva.iloc[0]["Recurso"]
                quantidade_tecnicos_media = media_produtiva["Recurso"].nunique()

                media1, media2, media3 = st.columns(3)
                with media1:
                    st.metric("📊 Média Geral", f"{media_geral:.2f}")
                with media2:
                    st.metric("🏅 Maior Média", f"{maior_media:.2f}")
                with media3:
                    st.metric("👷 Técnicos Analisados", quantidade_tecnicos_media)

                st.info(
                    f"Maior média produtiva de {coordenador_media}: "
                    f"{tecnico_maior_media} com {maior_media:.2f} "
                    "atividades por dia trabalhado."
                )

                media_grafico = media_produtiva.sort_values(
                    "Média Diária", ascending=True
                )

                fig_media = px.bar(
                    media_grafico,
                    x="Média Diária",
                    y="Recurso",
                    orientation="h",
                    text="Média Diária",
                    color="Média Diária",
                    color_continuous_scale=ESCALA_VIVO,
                    custom_data=["Total Atividades", "Dias Trabalhados"],
                    labels={
                        "Recurso": "Técnico",
                        "Média Diária": "Média de Atividades por Dia Trabalhado",
                    },
                )

                fig_media.update_traces(
                    textposition="outside",
                    texttemplate="%{text:.2f}",
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        "Média diária: %{x:.2f}<br>"
                        "Total de atividades: %{customdata[0]}<br>"
                        "Dias trabalhados: %{customdata[1]}"
                        "<extra></extra>"
                    ),
                )

                altura_media = max(400, len(media_grafico) * 45)
                fig_media.update_layout(
                    height=altura_media,
                    coloraxis_showscale=False,
                    xaxis_title="Média de Atividades por Dia Trabalhado",
                    yaxis_title="Técnico",
                )
                st.plotly_chart(fig_media, use_container_width=True)

                st.markdown("### 📋 Resumo de Produtividade")
                st.caption(
                    f"Resumo dos técnicos de {coordenador_media} presentes "
                    "nas duas bases."
                )

                tabela_media = media_produtiva.rename(
                    columns={"Recurso": "Técnico"}
                ).reset_index(drop=True)

                st.dataframe(
                    tabela_media[
                        [
                            "Técnico",
                            "Total Atividades",
                            "Dias Trabalhados",
                            "Média Diária",
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info(
                "👆 Selecione um coordenador para visualizar a média produtiva."
            )

else:
    st.info("Não existem atividades com data para calcular a produtividade.")


# =========================================================
# 40.1 PONTUACAO E VALOR POR TECNICO
# =========================================================

st.divider()

st.subheader("🏆 Pontuação e Valor por Técnico")

st.caption(
    "Pontuação e valor de cada atividade concluída conforme o Caderno B2B "
    "(aba Planilha1). Respeita todos os filtros selecionados. As médias por "
    "dia consideram somente as datas da força de trabalho e os dias ATIVO."
)


df_pontos = df[
    (df["Recurso"] != "") & ((df["Pontuação"] > 0) | (df["Valor"] > 0))
].copy()


if not df_pontos.empty:

    df_pontos["Data"] = df_pontos["Data Concluída"].dt.normalize()

    pontos_tecnico = (
        df_pontos.groupby(["Recurso", "CHAVE"])
        .agg(
            COORD=("COORD", "first"),
            **{
                "Atividades Pontuadas": ("Pontuação", "size"),
                "Pontuação": ("Pontuação", "sum"),
                "Valor": ("Valor", "sum"),
            },
        )
        .reset_index()
    )

    # Dias ATIVO e pontuação somente nas datas cobertas pela força de
    # trabalho, para que a média diária compare períodos equivalentes.
    dias_presentes = (
        df_presenca[df_presenca["Presença"] == "ATIVO"]
        .groupby("CHAVE")
        .size()
        .rename("Dias Presentes")
    )

    pontos_datas_forca = (
        df_pontos[df_pontos["Data"].isin(df_presenca["Data"].unique())]
        .groupby("CHAVE")[["Pontuação", "Valor"]]
        .sum()
        .add_suffix(" Datas FT")
    )

    pontos_tecnico = pontos_tecnico.merge(
        dias_presentes, left_on="CHAVE", right_index=True, how="left"
    ).merge(pontos_datas_forca, left_on="CHAVE", right_index=True, how="left")

    dias_validos = pontos_tecnico["Dias Presentes"].where(
        pontos_tecnico["Dias Presentes"] > 0
    )

    pontos_tecnico["Pontuação/Dia"] = (
        pontos_tecnico["Pontuação Datas FT"].fillna(0) / dias_validos
    ).round(2)

    pontos_tecnico["Valor/Dia"] = (
        pontos_tecnico["Valor Datas FT"].fillna(0) / dias_validos
    ).round(2)

    pontos_tecnico = pontos_tecnico.sort_values(
        ["Pontuação", "Valor"], ascending=[False, False]
    ).reset_index(drop=True)

    pontos1, pontos2, pontos3, pontos4 = st.columns(4)

    with pontos1:

        st.metric("👷 Técnicos Pontuados", pontos_tecnico["Recurso"].nunique())

    with pontos2:

        st.metric(
            "📋 Atividades Pontuadas",
            f"{int(pontos_tecnico['Atividades Pontuadas'].sum()):,}".replace(",", "."),
        )

    with pontos3:

        st.metric(
            "🏅 Maior Pontuação",
            formatar_numero(pontos_tecnico.iloc[0]["Pontuação"]),
            help=pontos_tecnico.iloc[0]["Recurso"],
        )

    with pontos4:

        st.metric(
            "💰 Valor Médio por Técnico",
            formatar_moeda(pontos_tecnico["Valor"].mean()),
        )

    pontos_grafico = pontos_tecnico.sort_values("Pontuação", ascending=True)

    fig_pontos = px.bar(
        pontos_grafico,
        x="Pontuação",
        y="Recurso",
        orientation="h",
        text="Pontuação",
        color="Pontuação",
        color_continuous_scale=ESCALA_VIVO,
        custom_data=["Valor", "Atividades Pontuadas", "COORD"],
        labels={"Recurso": "Técnico"},
    )

    fig_pontos.update_traces(
        textposition="outside",
        texttemplate="%{text:.2f}",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Pontuação: %{x:.2f}<br>"
            "Valor: R$ %{customdata[0]:,.2f}<br>"
            "Atividades pontuadas: %{customdata[1]}<br>"
            "COORD: %{customdata[2]}"
            "<extra></extra>"
        ),
    )

    fig_pontos.update_layout(
        height=max(400, len(pontos_grafico) * 32),
        coloraxis_showscale=False,
        xaxis_title="Pontuação",
        yaxis_title="Técnico",
    )

    st.plotly_chart(fig_pontos, use_container_width=True)

    st.dataframe(
        pontos_tecnico.rename(columns={"Recurso": "Técnico"})[
            [
                "Técnico",
                "COORD",
                "Atividades Pontuadas",
                "Pontuação",
                "Valor",
                "Dias Presentes",
                "Pontuação/Dia",
                "Valor/Dia",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Pontuação": st.column_config.NumberColumn(format="%.2f"),
            "Valor": st.column_config.NumberColumn(format="R$ %.2f"),
            "Dias Presentes": st.column_config.NumberColumn(format="%d"),
            "Pontuação/Dia": st.column_config.NumberColumn(format="%.2f"),
            "Valor/Dia": st.column_config.NumberColumn(format="R$ %.2f"),
        },
    )

else:

    st.info("Nenhuma atividade pontuada com os filtros selecionados.")


with st.expander("📘 Tabela de pontuação (Caderno B2B)"):

    st.dataframe(
        caderno[(caderno["Pontuação"] > 0) | (caderno["Valor"] > 0)]
        .drop(columns=["CHAVE_TIPO"])
        .sort_values("Valor", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={"Valor": st.column_config.NumberColumn(format="R$ %.2f")},
    )

    st.caption("Tipos marcados como NA no caderno não geram pontuação nem valor.")


# =========================================================
# 40.2 PRESENCA DIARIA
# =========================================================

st.divider()

st.subheader("🗓️ Presença Diária")

st.caption(
    "Status diário de cada técnico conforme a aba FORÇA DE TRABALHO da "
    "PRODUÇÃO B2B-OUTUBRO.xlsx. Quando o técnico pontuou no dia, a "
    "pontuação aparece ao lado do status."
)


df_presenca_validos = df_presenca[df_presenca["Presença"] != ""].copy()


if not df_presenca_validos.empty:

    ativos_por_dia = (
        df_presenca_validos[df_presenca_validos["Presença"] == "ATIVO"]
        .groupby("Data")
        .size()
        .reindex(df_presenca_validos["Data"].unique(), fill_value=0)
    )

    presenca1, presenca2, presenca3 = st.columns(3)

    with presenca1:

        st.metric("👷 Técnicos na Força", df_presenca_validos["CHAVE"].nunique())

    with presenca2:

        st.metric("🙋 Média de Presentes/Dia", formatar_numero(ativos_por_dia.mean(), 1))

    with presenca3:

        st.metric("📈 Presença", f"{taxa_presenca:.1f}%")

    resumo_presenca = (
        df_presenca_validos.groupby(["Data", "Presença"])
        .size()
        .reset_index(name="Técnicos")
    )

    ordem_presenca = list(CORES_PRESENCA) + sorted(
        set(resumo_presenca["Presença"]) - set(CORES_PRESENCA)
    )

    fig_presenca = px.bar(
        resumo_presenca,
        x="Data",
        y="Técnicos",
        color="Presença",
        text="Técnicos",
        color_discrete_map={
            status: cores[2] for status, cores in CORES_PRESENCA.items()
        },
        category_orders={"Presença": ordem_presenca},
    )

    fig_presenca.update_xaxes(tickformat="%d/%m", dtick=86400000)

    fig_presenca.update_layout(
        xaxis_title="Data",
        yaxis_title="Técnicos",
        legend_title="Status",
    )

    st.plotly_chart(fig_presenca, use_container_width=True)

    # Matriz técnico x data com o status e a pontuação do dia
    pontos_dia = (
        df[df["Pontuação"] > 0]
        .assign(Data=df["Data Concluída"].dt.normalize())
        .groupby(["CHAVE", "Data"])["Pontuação"]
        .sum()
        .reset_index()
    )

    matriz_presenca = df_presenca_validos.merge(
        pontos_dia, on=["CHAVE", "Data"], how="left"
    )

    matriz_presenca["Célula"] = matriz_presenca["Presença"] + matriz_presenca[
        "Pontuação"
    ].apply(
        lambda pontos: (
            f" · {formatar_numero(pontos)} pts" if pd.notna(pontos) and pontos > 0 else ""
        )
    )

    tabela_presenca = matriz_presenca.pivot_table(
        index="Recurso",
        columns="Data",
        values="Célula",
        aggfunc="first",
    ).sort_index(axis=1)

    tabela_presenca.columns = [data.strftime("%d/%m") for data in tabela_presenca.columns]

    colunas_dias_presenca = list(tabela_presenca.columns)

    tabela_presenca = tabela_presenca.fillna("")

    tabela_presenca["Dias ATIVO"] = (
        tabela_presenca[colunas_dias_presenca]
        .apply(lambda coluna: coluna.str.startswith("ATIVO"))
        .sum(axis=1)
    )

    tabela_presenca.index.name = "Técnico"

    def estilo_presenca(celula):

        cores = CORES_PRESENCA.get(str(celula).split(" · ")[0])

        if not cores:
            return ""

        return f"background-color: {cores[0]}; color: {cores[1]};"

    st.dataframe(
        tabela_presenca.style.map(estilo_presenca, subset=colunas_dias_presenca),
        use_container_width=True,
        height=min(900, 35 * (len(tabela_presenca) + 1) + 3),
    )

else:

    st.info("Nenhum registro de presença para os filtros selecionados.")


# =========================================================
# 41. DETALHAMENTO OPERACIONAL
# =========================================================

st.divider()

st.subheader("📋 Detalhamento Operacional")


st.caption(f"{len(df)} registros encontrados " "com os filtros selecionados.")


df_exibicao = df.drop(columns=["CHAVE"]).copy()


# =========================================================
# 42. FORMATANDO A DATA
# =========================================================

df_exibicao["Data Concluída"] = (
    df_exibicao["Data Concluída"].dt.strftime("%d/%m/%Y").fillna("")
)


# =========================================================
# 43. REMOVENDO COLUNAS TOTALMENTE VAZIAS
# =========================================================

colunas_exibir = []


for coluna in df_exibicao.columns:

    possui_informacao = (
        df_exibicao[coluna].fillna("").astype(str).str.strip().ne("").any()
    )

    if possui_informacao:

        colunas_exibir.append(coluna)


df_exibicao = df_exibicao[colunas_exibir]


# =========================================================
# 44. EXIBINDO A TABELA
# =========================================================

if not df_exibicao.empty:

    st.dataframe(df_exibicao, use_container_width=True, hide_index=True, height=500)

else:

    st.warning("Nenhum registro encontrado " "com os filtros selecionados.")


# =========================================================
# 45. DOWNLOAD DOS DADOS FILTRADOS
# =========================================================

csv = df_exibicao.to_csv(index=False).encode("utf-8-sig")


st.download_button(
    label="⬇️ Baixar dados filtrados",
    data=csv,
    file_name="dados_filtrados.csv",
    mime="text/csv",
)


# =========================================================
# 46. INFORMACOES DA BASE
# =========================================================

with st.expander("ℹ️ Informações da Base"):

    st.write(f"Registros carregados: {len(base)}")

    st.write(
        "Técnicos cadastrados: "
        f"{base.loc[base['Recurso'] != '', 'Recurso'].nunique()}"
    )

    st.write(f"Registros após filtros: {len(df)}")

    if not datas_validas.empty:

        st.write("Primeira data disponível: " f"{data_minima.strftime('%d/%m/%Y')}")

        st.write("Última data disponível: " f"{data_maxima.strftime('%d/%m/%Y')}")


# =========================================================
# 47. RODAPE
# =========================================================

st.divider()

st.caption("Dashboard de acompanhamento operacional | TOA e ETA")
