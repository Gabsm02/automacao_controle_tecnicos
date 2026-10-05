import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# 1. CONFIGURACAO DA PAGINA
# =========================================================

st.set_page_config(page_title="Controle de Técnicos", page_icon="📊", layout="wide")


# =========================================================
# 2. ESTILO DO DASHBOARD
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e5e7eb;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.05);
    }

    div[data-testid="stMetricValue"] {
        font-size: 30px;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. TITULO
# =========================================================

st.title("📊 Controle de Técnicos")

st.caption(
    "Acompanhamento das atividades TOA e ETA por técnico, "
    "tipo, coordenação, supervisor e classificação."
)


# =========================================================
# 4. CONFIGURACAO DO ARQUIVO
# =========================================================

arquivo = "Base_Final.xlsx"


# =========================================================
# 5. CARREGANDO A BASE
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
# 6. VERIFICANDO AS COLUNAS
# =========================================================

colunas_necessarias = [
    "Recurso",
    "Tipo",
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
# 7. TRATAMENTO DAS COLUNAS DE TEXTO
# =========================================================

colunas_texto = [
    "Recurso",
    "Tipo",
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
# 8. TRATAMENTO DA DATA
# =========================================================

base["Data Concluída"] = pd.to_datetime(
    base["Data Concluída"], errors="coerce", dayfirst=True
)


# =========================================================
# 9. FUNCAO PARA RETORNAR VALORES SEM VAZIOS
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
# 10. SIDEBAR
# =========================================================

st.sidebar.title("🔎 Filtros")

st.sidebar.caption("Utilize os filtros para analisar a operação.")


# =========================================================
# 11. PESQUISA RAPIDA POR TECNICO
# =========================================================

busca_recurso = st.sidebar.text_input(
    "🔍 Buscar técnico", placeholder="Digite parte do nome..."
)


# =========================================================
# 12. LISTAS DOS FILTROS
# =========================================================

lista_tecnicos = valores_validos(base, "Recurso")

lista_tipo = valores_validos(base, "Tipo")

lista_origem = valores_validos(base, "Origem")

lista_coord = valores_validos(base, "COORD")

lista_supervisor = valores_validos(base, "Supervisor")

lista_status = valores_validos(base, "Status")

lista_classificacao = valores_validos(base, "CLASSIFICACAO")


# =========================================================
# 13. ORDEM DOS DIAS
# =========================================================

ordem_dias = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


dias_existentes = valores_validos(base, "Dia Semana")


lista_dias = [dia for dia in ordem_dias if dia in dias_existentes]


# =========================================================
# 14. FILTRO TECNICO
# =========================================================

tecnicos_selecionados = st.sidebar.multiselect(
    "👷 Técnico", lista_tecnicos, default=[], placeholder="Todos os técnicos"
)


# =========================================================
# 15. FILTRO TIPO
# =========================================================

tipo = st.sidebar.multiselect(
    "Tipo", lista_tipo, default=[], placeholder="Todos os tipos"
)


# =========================================================
# 16. FILTRO ORIGEM
# =========================================================

origem = st.sidebar.multiselect(
    "Origem", lista_origem, default=[], placeholder="Todas as origens"
)


# =========================================================
# 17. FILTRO COORD
# =========================================================

coord = st.sidebar.multiselect(
    "COORD", lista_coord, default=[], placeholder="Todos os coordenadores"
)


# =========================================================
# 18. FILTRO SUPERVISOR
# =========================================================

supervisor = st.sidebar.multiselect(
    "Supervisor", lista_supervisor, default=[], placeholder="Todos os supervisores"
)


# =========================================================
# 19. FILTRO STATUS
# =========================================================

status = st.sidebar.multiselect(
    "Status", lista_status, default=[], placeholder="Todos os status"
)


# =========================================================
# 20. FILTRO CLASSIFICACAO
# =========================================================

classificacao = st.sidebar.multiselect(
    "Classificação",
    lista_classificacao,
    default=[],
    placeholder="Todas as classificações",
)


# =========================================================
# 21. FILTRO DIA DA SEMANA
# =========================================================

dia_semana = st.sidebar.multiselect(
    "Dia da Semana", lista_dias, default=[], placeholder="Todos os dias"
)


# =========================================================
# 22. FILTRO DE PERIODO
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
# 23. APLICANDO OS FILTROS
# =========================================================

df = base.copy()


# Pesquisa pelo nome
if busca_recurso:

    df = df[df["Recurso"].str.contains(busca_recurso, case=False, na=False)]


# Técnico
if tecnicos_selecionados:

    df = df[df["Recurso"].isin(tecnicos_selecionados)]


# Tipo
if tipo:

    df = df[df["Tipo"].isin(tipo)]


# Origem
if origem:

    df = df[df["Origem"].isin(origem)]


# COORD
if coord:

    df = df[df["COORD"].isin(coord)]


# Supervisor
if supervisor:

    df = df[df["Supervisor"].isin(supervisor)]


# Status
if status:

    df = df[df["Status"].isin(status)]


# Classificação
if classificacao:

    df = df[df["CLASSIFICACAO"].isin(classificacao)]


# Dia da semana
if dia_semana:

    df = df[df["Dia Semana"].isin(dia_semana)]


# Período
if periodo and isinstance(periodo, (list, tuple)) and len(periodo) == 2:

    data_inicio = pd.Timestamp(periodo[0])

    data_fim = pd.Timestamp(periodo[1])

    df = df[(df["Data Concluída"] >= data_inicio) & (df["Data Concluída"] <= data_fim)]


# =========================================================
# 24. INDICADORES GERAIS
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
# 25. CARDS
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
# 26. PRIMEIRA LINHA
# SUPERVISOR + ORIGEM
# =========================================================

grafico1, grafico2 = st.columns([2, 1])


# =========================================================
# 27. ATIVIDADES POR SUPERVISOR
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
            color_continuous_scale="Blues",
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
# 28. ORIGEM DAS ATIVIDADES
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
            color_discrete_sequence=["#2563EB", "#16A34A", "#F59E0B"],
        )

        fig_origem.update_traces(textinfo="percent+label")

        st.plotly_chart(fig_origem, use_container_width=True)

    else:

        st.info("Nenhuma informação de Origem.")


# =========================================================
# 29. SEGUNDA LINHA
# COORD + CLASSIFICACAO
# =========================================================

grafico3, grafico4 = st.columns(2)


# =========================================================
# 30. ATIVIDADES POR COORD
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
            color_continuous_scale="Purples",
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
# 31. CLASSIFICACAO
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
        )

        fig_classificacao.update_layout(
            showlegend=False, xaxis_title="Classificação", yaxis_title="Quantidade"
        )

        fig_classificacao.update_traces(textposition="outside")

        st.plotly_chart(fig_classificacao, use_container_width=True)

    else:

        st.info("Nenhuma informação de Classificação.")


# =========================================================
# 32. TERCEIRA LINHA
# TIPO + STATUS
# =========================================================

grafico5, grafico6 = st.columns(2)


# =========================================================
# 33. ATIVIDADES POR TIPO
# =========================================================

with grafico5:

    st.subheader("Atividades por Tipo")

    df_tipo = df[df["Tipo"] != ""].copy()

    if not df_tipo.empty:

        tipo_df = (
            df_tipo.groupby("Tipo")
            .size()
            .reset_index(name="Quantidade")
            .sort_values("Quantidade", ascending=True)
        )

        fig_tipo = px.bar(
            tipo_df,
            x="Quantidade",
            y="Tipo",
            orientation="h",
            text="Quantidade",
            color="Quantidade",
            color_continuous_scale="Teal",
        )

        fig_tipo.update_layout(
            coloraxis_showscale=False, xaxis_title="Quantidade", yaxis_title="Tipo"
        )

        fig_tipo.update_traces(textposition="outside")

        st.plotly_chart(fig_tipo, use_container_width=True)

    else:

        st.info("Nenhuma informação de Tipo.")


# =========================================================
# 34. DISTRIBUICAO POR STATUS
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
            status_df, x="Status", y="Quantidade", text="Quantidade", color="Status"
        )

        fig_status.update_layout(
            showlegend=False, xaxis_title="Status", yaxis_title="Quantidade"
        )

        fig_status.update_traces(textposition="outside")

        st.plotly_chart(fig_status, use_container_width=True)

    else:

        st.info("Nenhuma informação de Status.")


# =========================================================
# 35. ATIVIDADES POR DIA DA SEMANA
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
            line=dict(width=4), marker=dict(size=10), textposition="top center"
        )

        st.plotly_chart(fig_dias, use_container_width=True)

    else:

        st.info("Nenhum dia da semana válido encontrado.")

else:

    st.info("Nenhuma informação de Dia da Semana.")


# =========================================================
# 36. PRODUTIVIDADE DOS TECNICOS
# =========================================================

st.divider()

st.subheader("👷 Produtividade dos Técnicos")

st.caption(
    "A análise abaixo respeita todos os filtros selecionados, "
    "incluindo COORD, Supervisor, Técnico, Tipo e Período."
)


df_produtividade = df[(df["Recurso"] != "") & (df["Data Concluída"].notna())].copy()


if not df_produtividade.empty:

    # =====================================================
    # 37. CRIANDO DATA SEM HORARIO
    # =====================================================

    df_produtividade["Data"] = df_produtividade["Data Concluída"].dt.normalize()

    # =====================================================
    # 38. TOTAL POR TECNICO
    # Essa variável serve apenas para ordenar o Heatmap
    # =====================================================

    total_atividades_tecnico = (
        df_produtividade.groupby("Recurso")
        .size()
        .reset_index(name="Quantidade")
        .sort_values("Quantidade", ascending=False)
    )

    # =====================================================
    # 39. HEATMAP
    # =====================================================

    st.markdown("### 🔥 Atividades por Técnico e Data")

    st.caption(
        "Cada célula representa a quantidade de atividades "
        "do técnico naquela data. Cores mais escuras "
        "representam maior volume de atividades."
    )

    heatmap_df = (
        df_produtividade.groupby(["Recurso", "Data"])
        .size()
        .reset_index(name="Quantidade")
    )

    # =====================================================
    # CRIANDO MATRIZ TECNICO X DATA
    # =====================================================

    heatmap_pivot = heatmap_df.pivot_table(
        index="Recurso",
        columns="Data",
        values="Quantidade",
        fill_value=0,
        aggfunc="sum",
    )

    # =====================================================
    # ORDENANDO AS DATAS
    # =====================================================

    heatmap_pivot = heatmap_pivot.sort_index(axis=1)

    # =====================================================
    # ORDENANDO OS TECNICOS POR VOLUME
    # SEM EXIBIR UM RANKING SEPARADO
    # =====================================================

    ordem_tecnicos = total_atividades_tecnico["Recurso"].tolist()

    ordem_tecnicos = [
        tecnico for tecnico in ordem_tecnicos if tecnico in heatmap_pivot.index
    ]

    heatmap_pivot = heatmap_pivot.loc[ordem_tecnicos]

    # =====================================================
    # FORMATANDO DATAS PARA DD/MM
    # =====================================================

    heatmap_pivot.columns = [data.strftime("%d/%m") for data in heatmap_pivot.columns]

    # =====================================================
    # CRIANDO O HEATMAP
    # =====================================================

    fig_heatmap = px.imshow(
        heatmap_pivot,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=[
            [0.00, "#F8FAFC"],
            [0.15, "#DBEAFE"],
            [0.35, "#93C5FD"],
            [0.55, "#60A5FA"],
            [0.75, "#2563EB"],
            [1.00, "#172554"],
        ],
        labels={"x": "Data", "y": "Técnico", "color": "Atividades"},
    )

    # =====================================================
    # ALTURA DINAMICA DO HEATMAP
    # =====================================================

    altura_heatmap = max(500, len(heatmap_pivot) * 35)

    fig_heatmap.update_layout(
        height=altura_heatmap,
        xaxis_title="Data",
        yaxis_title="Técnico",
        coloraxis_colorbar=dict(title="Atividades"),
        margin=dict(l=10, r=10, t=50, b=20),
    )

    fig_heatmap.update_xaxes(side="top", tickangle=-45)

    st.plotly_chart(fig_heatmap, use_container_width=True)

    # =====================================================
    # 40. TABELA DE ATIVIDADES DIARIAS
    # =====================================================

    st.markdown("### 📋 Quantidade Diária por Técnico")

    tabela_diaria = heatmap_pivot.copy()

    tabela_diaria["TOTAL"] = tabela_diaria.sum(axis=1)

    tabela_diaria = tabela_diaria.sort_values("TOTAL", ascending=False)

    st.dataframe(tabela_diaria, use_container_width=True)

    # =====================================================
    # 41. MEDIA PRODUTIVA
    # =====================================================

    st.divider()

    st.subheader("📈 Média Produtiva por Técnico")

    st.caption(
        "Média produtiva = total de atividades do técnico "
        "dividido pela quantidade de dias em que o técnico "
        "teve pelo menos uma atividade registrada."
    )

    # =====================================================
    # TOTAL DE ATIVIDADES POR TECNICO
    # =====================================================

    total_por_tecnico = (
        df_produtividade.groupby("Recurso").size().reset_index(name="Total Atividades")
    )

    # =====================================================
    # DIAS COM ATIVIDADE POR TECNICO
    # =====================================================

    dias_por_tecnico = (
        df_produtividade.groupby("Recurso")["Data"]
        .nunique()
        .reset_index(name="Dias com Atividade")
    )

    # =====================================================
    # JUNTANDO OS RESULTADOS
    # =====================================================

    media_produtiva = total_por_tecnico.merge(
        dias_por_tecnico, on="Recurso", how="left"
    )

    # =====================================================
    # CALCULANDO A MEDIA DIARIA
    # =====================================================

    media_produtiva["Média Diária"] = (
        media_produtiva["Total Atividades"] / media_produtiva["Dias com Atividade"]
    )

    media_produtiva["Média Diária"] = media_produtiva["Média Diária"].round(2)

    media_produtiva = media_produtiva.sort_values(
        ["Média Diária", "Total Atividades"], ascending=[False, False]
    )

    # =====================================================
    # 42. INDICADORES DE PRODUTIVIDADE
    # =====================================================

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
        f"Maior média produtiva: "
        f"{tecnico_maior_media} "
        f"com {maior_media:.2f} atividades/dia."
    )

    # =====================================================
    # 43. GRAFICO DA MEDIA PRODUTIVA
    # =====================================================

    media_grafico = media_produtiva.sort_values("Média Diária", ascending=True)

    fig_media = px.bar(
        media_grafico,
        x="Média Diária",
        y="Recurso",
        orientation="h",
        text="Média Diária",
        color="Média Diária",
        color_continuous_scale="Greens",
        custom_data=["Total Atividades", "Dias com Atividade"],
        labels={"Recurso": "Técnico", "Média Diária": ("Média de Atividades por Dia")},
    )

    fig_media.update_traces(
        textposition="outside",
        texttemplate="%{text:.2f}",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Média diária: %{x:.2f}<br>"
            "Total de atividades: %{customdata[0]}<br>"
            "Dias com atividade: %{customdata[1]}"
            "<extra></extra>"
        ),
    )

    altura_media = max(500, len(media_grafico) * 35)

    fig_media.update_layout(
        height=altura_media,
        coloraxis_showscale=False,
        xaxis_title="Média de Atividades por Dia",
        yaxis_title="Técnico",
    )

    st.plotly_chart(fig_media, use_container_width=True)

    # =====================================================
    # 44. TABELA DE MEDIA PRODUTIVA
    # =====================================================

    st.markdown("### 📋 Resumo de Produtividade")

    tabela_media = media_produtiva.rename(columns={"Recurso": "Técnico"}).reset_index(
        drop=True
    )

    st.dataframe(tabela_media, use_container_width=True, hide_index=True)


else:

    st.info("Não existem atividades com data " "para calcular a produtividade.")


# =========================================================
# 45. DETALHAMENTO OPERACIONAL
# =========================================================

st.divider()

st.subheader("📋 Detalhamento Operacional")


st.caption(f"{len(df)} registros encontrados " "com os filtros selecionados.")


df_exibicao = df.copy()


# =========================================================
# 46. FORMATANDO A DATA PARA EXIBICAO
# =========================================================

df_exibicao["Data Concluída"] = (
    df_exibicao["Data Concluída"].dt.strftime("%d/%m/%Y").fillna("")
)


# =========================================================
# 47. REMOVENDO COLUNAS TOTALMENTE VAZIAS
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
# 48. EXIBINDO A TABELA
# =========================================================

if not df_exibicao.empty:

    st.dataframe(df_exibicao, use_container_width=True, hide_index=True, height=500)

else:

    st.warning("Nenhum registro encontrado " "com os filtros selecionados.")


# =========================================================
# 49. DOWNLOAD DOS DADOS FILTRADOS
# =========================================================

csv = df_exibicao.to_csv(index=False).encode("utf-8-sig")


st.download_button(
    label="⬇️ Baixar dados filtrados",
    data=csv,
    file_name="dados_filtrados.csv",
    mime="text/csv",
)


# =========================================================
# 50. INFORMACOES DA BASE
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
# 51. RODAPE
# =========================================================

st.divider()

st.caption("Dashboard de acompanhamento operacional | TOA e ETA")
