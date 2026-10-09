import pandas as pd
import streamlit as st
import plotly.express as px

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


# =========================================================
# 6. CARREGAR BASE
# =========================================================


@st.cache_data
def carregar_base():

    df = pd.read_excel(arquivo, engine="openpyxl")

    df.columns = df.columns.astype(str).str.strip()

    return df


try:

    base = carregar_base()

except FileNotFoundError:

    st.error(f"O arquivo '{arquivo}' não foi encontrado.")

    st.stop()

except Exception as erro:

    st.error(f"Erro ao carregar a base: {erro}")

    st.stop()


# =========================================================
# 7. VERIFICANDO COLUNAS
# =========================================================

colunas_necessarias = [
    "Recurso",
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
        "Selecione um coordenador para visualizar a média "
        "produtiva dos técnicos vinculados a ele. A média é "
        "calculada dividindo o total de atividades pela "
        "quantidade de dias em que o técnico teve pelo menos "
        "uma atividade."
    )

    # =====================================================
    # COORDENADORES DISPONIVEIS PARA MEDIA
    # =====================================================

    coordenadores_media = (
        df_produtividade.loc[df_produtividade["COORD"] != "", "COORD"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    coordenadores_media = sorted(coordenadores_media)

    # =====================================================
    # FILTRO LOCAL DA MEDIA PRODUTIVA
    # =====================================================

    coordenador_media = st.selectbox(
        "🔎 Coordenador",
        options=coordenadores_media,
        index=None,
        placeholder="Selecione um coordenador...",
        key="coordenador_media",
    )

    # =====================================================
    # SOMENTE MOSTRA A MEDIA DEPOIS DA SELECAO
    # =====================================================

    if coordenador_media:

        df_media = df_produtividade[
            df_produtividade["COORD"] == coordenador_media
        ].copy()

        # =================================================
        # TOTAL DE ATIVIDADES POR TECNICO
        # =================================================

        total_por_tecnico = (
            df_media.groupby("Recurso").size().reset_index(name="Total Atividades")
        )

        # =================================================
        # QUANTIDADE DE DIAS COM ATIVIDADE
        # =================================================

        dias_por_tecnico = (
            df_media.groupby("Recurso")["Data"]
            .nunique()
            .reset_index(name="Dias com Atividade")
        )

        # =================================================
        # JUNTANDO RESULTADOS
        # =================================================

        media_produtiva = total_por_tecnico.merge(
            dias_por_tecnico, on="Recurso", how="left"
        )

        # =================================================
        # CALCULANDO A MEDIA
        # =================================================

        media_produtiva["Média Diária"] = (
            media_produtiva["Total Atividades"] / media_produtiva["Dias com Atividade"]
        )

        media_produtiva["Média Diária"] = media_produtiva["Média Diária"].round(2)

        media_produtiva = media_produtiva.sort_values(
            ["Média Diária", "Total Atividades"], ascending=[False, False]
        )

        # =================================================
        # INDICADORES DA MEDIA
        # =================================================

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
            f"Maior média produtiva de "
            f"{coordenador_media}: "
            f"{tecnico_maior_media} "
            f"com {maior_media:.2f} atividades/dia."
        )

        # =================================================
        # GRAFICO DA MEDIA PRODUTIVA
        # =================================================

        media_grafico = media_produtiva.sort_values("Média Diária", ascending=True)

        fig_media = px.bar(
            media_grafico,
            x="Média Diária",
            y="Recurso",
            orientation="h",
            text="Média Diária",
            color="Média Diária",
            color_continuous_scale=ESCALA_VIVO,
            custom_data=["Total Atividades", "Dias com Atividade"],
            labels={
                "Recurso": "Técnico",
                "Média Diária": "Média de Atividades por Dia",
            },
        )

        fig_media.update_traces(
            textposition="outside",
            texttemplate="%{text:.2f}",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Média diária: %{x:.2f}<br>"
                "Total de atividades: "
                "%{customdata[0]}<br>"
                "Dias com atividade: "
                "%{customdata[1]}"
                "<extra></extra>"
            ),
        )

        # =================================================
        # ALTURA DINAMICA
        # =================================================

        altura_media = max(400, len(media_grafico) * 45)

        fig_media.update_layout(
            height=altura_media,
            coloraxis_showscale=False,
            xaxis_title=("Média de Atividades por Dia"),
            yaxis_title="Técnico",
        )

        st.plotly_chart(fig_media, use_container_width=True)

        # =================================================
        # RESUMO DE PRODUTIVIDADE
        # =================================================

        st.markdown("### 📋 Resumo de Produtividade")

        st.caption(
            f"Resumo dos técnicos vinculados ao coordenador " f"{coordenador_media}."
        )

        tabela_media = media_produtiva.rename(
            columns={"Recurso": "Técnico"}
        ).reset_index(drop=True)

        st.dataframe(tabela_media, use_container_width=True, hide_index=True)

    else:

        st.info(
            "👆 Selecione um coordenador para visualizar "
            "a média produtiva dos técnicos."
        )


else:

    st.info("Não existem atividades com data " "para calcular a produtividade.")


# =========================================================
# 41. DETALHAMENTO OPERACIONAL
# =========================================================

st.divider()

st.subheader("📋 Detalhamento Operacional")


st.caption(f"{len(df)} registros encontrados " "com os filtros selecionados.")


df_exibicao = df.copy()


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
