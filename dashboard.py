import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# 1. CONFIGURACAO DA PAGINA
# =========================================================

st.set_page_config(page_title="Controle de Técnicos", page_icon="📊", layout="wide")


# =========================================================
# 2. ESTILO
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
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
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
# 4. ARQUIVO
# =========================================================

arquivo = "Base_Final.xlsx"


# =========================================================
# 5. CARREGAR BASE
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

    st.error("Algumas colunas não foram encontradas na Base_Final.xlsx.")

    st.write("Colunas faltando:", colunas_faltando)

    st.write("Colunas encontradas:", list(base.columns))

    st.stop()


# =========================================================
# 7. TRATAMENTO DOS DADOS
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
# 8. TRATANDO A DATA
# =========================================================

base["Data Concluída"] = pd.to_datetime(
    base["Data Concluída"], errors="coerce", dayfirst=True
)


# =========================================================
# 9. FUNCAO PARA PEGAR VALORES VALIDOS
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
# 11. BUSCA RAPIDA
# =========================================================

busca_recurso = st.sidebar.text_input(
    "🔍 Buscar técnico", placeholder="Digite parte do nome..."
)


# =========================================================
# 12. LISTAS PARA OS FILTROS
# =========================================================

lista_tecnicos = valores_validos(base, "Recurso")

lista_tipo = valores_validos(base, "Tipo")

lista_origem = valores_validos(base, "Origem")

lista_coord = valores_validos(base, "COORD")

lista_supervisor = valores_validos(base, "Supervisor")

lista_status = valores_validos(base, "Status")

lista_classificacao = valores_validos(base, "CLASSIFICACAO")


# =========================================================
# 13. DIAS DA SEMANA
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
# 22. APLICANDO OS FILTROS
# =========================================================

df = base.copy()


# Busca pelo técnico
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


# Coordenador
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


# Dia da Semana
if dia_semana:

    df = df[df["Dia Semana"].isin(dia_semana)]


# =========================================================
# 23. INDICADORES
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
# 24. CARDS
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
# 25. ATIVIDADES POR SUPERVISOR + ORIGEM
# =========================================================

grafico1, grafico2 = st.columns([2, 1])


# =========================================================
# SUPERVISOR
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
            yaxis_title="Atividades",
        )

        fig_supervisor.update_traces(textposition="outside")

        st.plotly_chart(fig_supervisor, use_container_width=True)

    else:

        st.info("Nenhuma informação de supervisor encontrada.")


# =========================================================
# ORIGEM
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

        st.info("Nenhuma informação de origem encontrada.")


# =========================================================
# 26. COORD + CLASSIFICACAO
# =========================================================

grafico3, grafico4 = st.columns(2)


# =========================================================
# COORD
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

        st.plotly_chart(fig_coord, use_container_width=True)

    else:

        st.info("Nenhuma informação de COORD encontrada.")


# =========================================================
# CLASSIFICACAO
# =========================================================

with grafico4:

    st.subheader("Distribuição por Classificação")

    df_classificacao = df[df["CLASSIFICACAO"] != ""].copy()

    if not df_classificacao.empty:

        class_df = (
            df_classificacao.groupby("CLASSIFICACAO")
            .size()
            .reset_index(name="Quantidade")
            .sort_values("Quantidade", ascending=False)
        )

        fig_classificacao = px.bar(
            class_df,
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

        st.info("Nenhuma classificação encontrada.")


# =========================================================
# 27. TIPO + STATUS
# =========================================================

grafico5, grafico6 = st.columns(2)


# =========================================================
# TIPO
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

        st.plotly_chart(fig_tipo, use_container_width=True)

    else:

        st.info("Nenhuma informação de Tipo encontrada.")


# =========================================================
# STATUS
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

        st.info("Nenhuma informação de Status encontrada.")


# =========================================================
# 28. ATIVIDADES POR DIA DA SEMANA
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

        fig_dias.update_traces(line=dict(width=4), marker=dict(size=10))

        fig_dias.update_layout(
            xaxis_title="Dia da Semana", yaxis_title="Quantidade de Atividades"
        )

        st.plotly_chart(fig_dias, use_container_width=True)

    else:

        st.info("Nenhum dia da semana válido encontrado.")

else:

    st.info("Nenhuma informação de dia da semana encontrada.")


# =========================================================
# 29. ATIVIDADES DIARIAS POR TECNICO
# =========================================================

st.divider()

st.subheader("👷 Atividades Diárias por Técnico")

st.caption(
    "Ao selecionar um COORD nos filtros, são exibidos "
    "os técnicos desse coordenador e a quantidade de "
    "atividades realizada por cada técnico em cada data."
)


# =========================================================
# PREPARANDO DADOS
# =========================================================

df_tecnico_dia = df[(df["Recurso"] != "") & (df["Data Concluída"].notna())].copy()


if not df_tecnico_dia.empty:

    # =====================================================
    # CRIANDO DATA SEM HORARIO
    # =====================================================

    df_tecnico_dia["Data"] = df_tecnico_dia["Data Concluída"].dt.normalize()

    # =====================================================
    # CONTANDO ATIVIDADES POR TECNICO E DATA
    # =====================================================

    atividades_diarias = (
        df_tecnico_dia.groupby(["Recurso", "Data"])
        .size()
        .reset_index(name="Quantidade")
    )

    # =====================================================
    # ORDENANDO
    # =====================================================

    atividades_diarias = atividades_diarias.sort_values(["Data", "Recurso"])

    # =====================================================
    # FORMATANDO DATA
    # =====================================================

    atividades_diarias["Data Formatada"] = atividades_diarias["Data"].dt.strftime(
        "%d/%m/%Y"
    )

    # =====================================================
    # ORDEM CRONOLOGICA DAS DATAS
    # =====================================================

    ordem_datas = (
        atividades_diarias.sort_values("Data")["Data Formatada"]
        .drop_duplicates()
        .tolist()
    )

    # =====================================================
    # GRAFICO
    # =====================================================

    fig_tecnico_dia = px.bar(
        atividades_diarias,
        x="Recurso",
        y="Quantidade",
        color="Data Formatada",
        barmode="group",
        text="Quantidade",
        category_orders={"Data Formatada": ordem_datas},
        labels={
            "Recurso": "Técnico",
            "Quantidade": "Atividades",
            "Data Formatada": "Data",
        },
    )

    fig_tecnico_dia.update_layout(
        xaxis_title="Técnico",
        yaxis_title="Quantidade de Atividades",
        legend_title="Data",
        height=650,
        bargap=0.15,
        bargroupgap=0.05,
        xaxis=dict(tickangle=-45),
    )

    fig_tecnico_dia.update_traces(textposition="outside")

    st.plotly_chart(fig_tecnico_dia, use_container_width=True)

    # =====================================================
    # 30. TABELA RESUMO DIARIO
    # =====================================================

    st.markdown("### 📋 Quantidade Diária por Técnico")

    tabela_tecnico_dia = atividades_diarias.pivot_table(
        index="Recurso",
        columns="Data Formatada",
        values="Quantidade",
        fill_value=0,
        aggfunc="sum",
    )

    # =====================================================
    # ORDENANDO COLUNAS PELA DATA
    # =====================================================

    colunas_datas = [data for data in ordem_datas if data in tabela_tecnico_dia.columns]

    tabela_tecnico_dia = tabela_tecnico_dia[colunas_datas]

    # =====================================================
    # TOTAL POR TECNICO
    # =====================================================

    tabela_tecnico_dia["TOTAL"] = tabela_tecnico_dia.sum(axis=1)

    # =====================================================
    # ORDENANDO TECNICOS
    # =====================================================

    tabela_tecnico_dia = tabela_tecnico_dia.sort_values("TOTAL", ascending=False)

    # =====================================================
    # MOSTRAR TABELA
    # =====================================================

    st.dataframe(tabela_tecnico_dia, use_container_width=True)


else:

    st.info("Nenhuma atividade com data encontrada " "para os filtros selecionados.")


# =========================================================
# 31. DETALHAMENTO OPERACIONAL
# =========================================================

st.divider()

st.subheader("📋 Detalhamento Operacional")


st.caption(f"{len(df)} registros encontrados.")


df_exibicao = df.copy()


# =========================================================
# FORMATANDO DATA PARA EXIBICAO
# =========================================================

df_exibicao["Data Concluída"] = (
    df_exibicao["Data Concluída"].dt.strftime("%d/%m/%Y").fillna("")
)


# =========================================================
# REMOVENDO COLUNAS TOTALMENTE VAZIAS
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
# EXIBIR TABELA
# =========================================================

if not df_exibicao.empty:

    st.dataframe(df_exibicao, use_container_width=True, hide_index=True, height=500)

else:

    st.warning("Nenhum registro encontrado " "com os filtros selecionados.")


# =========================================================
# 32. DOWNLOAD
# =========================================================

csv = df_exibicao.to_csv(index=False).encode("utf-8-sig")


st.download_button(
    label="⬇️ Baixar dados filtrados",
    data=csv,
    file_name="dados_filtrados.csv",
    mime="text/csv",
)


# =========================================================
# 33. INFORMACOES
# =========================================================

with st.expander("ℹ️ Informações da Base"):

    st.write(f"Total de registros carregados: {len(base)}")

    st.write(
        f"Técnicos cadastrados: "
        f"{base.loc[base['Recurso'] != '', 'Recurso'].nunique()}"
    )

    st.write(f"Registros após filtros: {len(df)}")


# =========================================================
# 34. RODAPE
# =========================================================

st.divider()

st.caption("Dashboard de acompanhamento operacional | TOA e ETA")
