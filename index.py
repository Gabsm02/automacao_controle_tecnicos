import pandas as pd
import os

# ==========================================
# 1. CONFIGURACOES DOS ARQUIVOS
# ==========================================

arquivo_toa = "BASE TOA.xlsx"
arquivo_eta = "BASE ETA.xlsx"
arquivo_referencia = "tbDEPARA.xlsx"
arquivo_final = "Base_Final.xlsx"


# ==========================================
# 2. LENDO AS BASES TOA E ETA
# ==========================================

base_toa = pd.read_excel(arquivo_toa, sheet_name="Page 1")

base_eta = pd.read_excel(arquivo_eta, sheet_name="Page 1")


# ==========================================
# 3. SELECIONANDO AS COLUNAS
# ==========================================

base_toa = base_toa[["Recurso", "Tipo", "Status da Atividade", "Data"]].copy()


base_eta = base_eta[
    ["Recurso", "Status", "Tipo de Atividade", "Data Agendada para Execução"]
].copy()


# ==========================================
# 4. RENOMEANDO AS COLUNAS
# ==========================================

base_toa = base_toa.rename(
    columns={"Status da Atividade": "Status", "Data": "Data Concluída"}
)


base_eta = base_eta.rename(
    columns={
        "Tipo de Atividade": "Tipo",
        "Data Agendada para Execução": "Data Concluída",
    }
)


# ==========================================
# 5. TRATANDO AS DATAS
# ==========================================

base_toa["Data Concluída"] = pd.to_datetime(
    base_toa["Data Concluída"], errors="coerce", dayfirst=True
)


base_eta["Data Concluída"] = pd.to_datetime(
    base_eta["Data Concluída"], errors="coerce", dayfirst=True
)


# ==========================================
# 6. CALCULANDO O DIA DA SEMANA
# ==========================================

dias_semana = {
    0: "seg",
    1: "ter",
    2: "qua",
    3: "qui",
    4: "sex",
    5: "sáb",
    6: "dom",
}


base_toa["Dia Semana"] = base_toa["Data Concluída"].dt.dayofweek.map(dias_semana)


base_eta["Dia Semana"] = base_eta["Data Concluída"].dt.dayofweek.map(dias_semana)


# ==========================================
# 7. ADICIONANDO A ORIGEM
# ==========================================

base_toa["Origem"] = "TOA"

base_eta["Origem"] = "ETA"


# ==========================================
# 8. ORGANIZANDO A ORDEM DAS COLUNAS
# ==========================================

ordem_colunas = ["Recurso", "Tipo", "Status", "Data Concluída", "Origem", "Dia Semana"]


base_toa = base_toa[ordem_colunas]


base_eta = base_eta[ordem_colunas]


# ==========================================
# 9. JUNTANDO TOA + ETA
# ==========================================

base_nova = pd.concat([base_toa, base_eta], ignore_index=True)


# ==========================================
# 10. VERIFICANDO SE BASE_FINAL JA EXISTE
# ==========================================

if os.path.exists(arquivo_final):

    print("Base_Final encontrada.")

    base_antiga = pd.read_excel(arquivo_final)

    # Remove as colunas da base de referencia
    # pois serao preenchidas novamente
    base_antiga = base_antiga.drop(
        columns=["COORD", "Supervisor", "CLASSIFICACAO"], errors="ignore"
    )

    # ======================================
    # CORRIGINDO DATA DA BASE ANTIGA
    # ======================================

    if "Data Concluída" in base_antiga.columns:

        base_antiga["Data Concluída"] = pd.to_datetime(
            base_antiga["Data Concluída"], errors="coerce", dayfirst=True
        )

        # Recalcula o dia da semana
        # usando a data real de cada registro
        base_antiga["Dia Semana"] = base_antiga["Data Concluída"].dt.dayofweek.map(
            dias_semana
        )

    # ======================================
    # JUNTANDO ANTIGOS + NOVOS
    # ======================================

    base_final = pd.concat([base_antiga, base_nova], ignore_index=True)


else:

    print("Base_Final ainda não existe.")
    print("Criando uma nova Base_Final...")

    base_final = base_nova.copy()


# ==========================================
# 11. LENDO A BASE DE REFERENCIA
# ==========================================

base_referencia = pd.read_excel(arquivo_referencia, sheet_name="tbDEPARA")


# ==========================================
# 12. SELECIONANDO AS COLUNAS DO DEPARA
# ==========================================

base_referencia = base_referencia[
    ["Nome", "COORD", "Supervisor", "CLASSIFICACAO"]
].copy()


# ==========================================
# 13. RENOMEANDO NOME PARA RECURSO
# ==========================================

# Na tbDEPARA:
# Nome = Recurso das bases TOA e ETA

base_referencia = base_referencia.rename(columns={"Nome": "Recurso"})


# ==========================================
# 14. TRATANDO A COLUNA RECURSO
# ==========================================

base_final["Recurso"] = (
    base_final["Recurso"].fillna("").astype(str).str.strip().str.upper()
)


base_referencia["Recurso"] = (
    base_referencia["Recurso"].fillna("").astype(str).str.strip().str.upper()
)


# ==========================================
# 15. REMOVENDO RECURSOS VAZIOS DO DEPARA
# ==========================================

base_referencia = base_referencia[base_referencia["Recurso"] != ""]


# ==========================================
# 16. REMOVENDO DUPLICADOS DO DEPARA
# ==========================================

base_referencia = base_referencia.drop_duplicates(subset=["Recurso"], keep="last")


# ==========================================
# 17. BUSCANDO INFORMACOES NA tbDEPARA
# ==========================================

base_final = base_final.merge(base_referencia, on="Recurso", how="left")


# ==========================================
# 18. ORGANIZANDO AS COLUNAS FINAIS
# ==========================================

colunas_finais = ["COORD", "Supervisor", "CLASSIFICACAO"]


outras_colunas = [
    coluna for coluna in base_final.columns if coluna not in colunas_finais
]


base_final = base_final[outras_colunas + colunas_finais]


# ==========================================
# 19. VERIFICANDO RECURSOS NAO ENCONTRADOS
# ==========================================

recursos_nao_encontrados = (
    base_final.loc[
        base_final["COORD"].isna() & (base_final["Recurso"] != ""), "Recurso"
    ]
    .drop_duplicates()
    .tolist()
)


quantidade_nao_encontrados = len(recursos_nao_encontrados)


# ==========================================
# 20. GARANTINDO QUE DATA CONTINUE COMO DATA
# ==========================================

base_final["Data Concluída"] = pd.to_datetime(
    base_final["Data Concluída"], errors="coerce", dayfirst=True
)


# ==========================================
# 21. SALVANDO A BASE FINAL
# ==========================================

with pd.ExcelWriter(
    arquivo_final,
    engine="openpyxl",
    date_format="DD/MM/YYYY",
    datetime_format="DD/MM/YYYY",
) as writer:

    # Salva os dados
    base_final.to_excel(writer, index=False, sheet_name="Base")

    # Acessa a aba criada
    planilha = writer.sheets["Base"]

    # ======================================
    # DESCOBRINDO A COLUNA DA DATA
    # ======================================

    coluna_data = base_final.columns.get_loc("Data Concluída") + 1

    # ======================================
    # FORMATANDO AS DATAS NO EXCEL
    # ======================================

    for linha in range(2, len(base_final) + 2):

        celula = planilha.cell(row=linha, column=coluna_data)

        celula.number_format = "DD/MM/YYYY"


# ==========================================
# 22. RESULTADO
# ==========================================

print()

print("=" * 60)

print("BASE ATUALIZADA COM SUCESSO!")

print("=" * 60)


print()

print("REGISTROS ADICIONADOS")

print("-" * 60)


print(f"TOA: {len(base_toa)}")


print(f"ETA: {len(base_eta)}")


print(f"Total novos: {len(base_nova)}")


print()

print("BASE FINAL")

print("-" * 60)


print(f"Total de registros: {len(base_final)}")


print()

print("DEPARA")

print("-" * 60)


print(f"Recursos não encontrados: " f"{quantidade_nao_encontrados}")


# ==========================================
# 23. MOSTRANDO RECURSOS NAO ENCONTRADOS
# ==========================================

if quantidade_nao_encontrados > 0:

    print()

    print("Recursos que não existem na tbDEPARA:")

    for recurso in recursos_nao_encontrados:

        print(f"- {recurso}")


print()

print("=" * 60)

print(f"Arquivo salvo: {arquivo_final}")

print("Formato das datas: DD/MM/AAAA")

print("=" * 60)
