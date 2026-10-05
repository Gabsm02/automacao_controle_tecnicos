import pandas as pd
import os
from datetime import datetime

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
# 3. SELECIONANDO AS COLUNAS NECESSARIAS
# ==========================================

base_toa = base_toa[["Recurso", "Tipo", "Status da Atividade", "Data"]]

base_eta = base_eta[
    ["Recurso", "Status", "Tipo de Atividade", "Data Agendada para Execução"]
]


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
# 5. DESCOBRINDO O DIA DA SEMANA
# ==========================================

dias_semana = {
    "Monday": "seg",
    "Tuesday": "ter",
    "Wednesday": "qua",
    "Thursday": "qui",
    "Friday": "sex",
    "Saturday": "sáb",
    "Sunday": "dom",
}

dia_semana = dias_semana[datetime.now().strftime("%A")]


# ==========================================
# 6. ADICIONANDO ORIGEM E DIA DA SEMANA
# ==========================================

# Base TOA
base_toa["Origem"] = "TOA"
base_toa["Dia Semana"] = dia_semana

# Base ETA
base_eta["Origem"] = "ETA"
base_eta["Dia Semana"] = dia_semana


# ==========================================
# 7. JUNTANDO TOA + ETA
# ==========================================

base_nova = pd.concat([base_toa, base_eta], ignore_index=True)


# ==========================================
# 8. VERIFICANDO SE BASE_FINAL JA EXISTE
# ==========================================

if os.path.exists(arquivo_final):

    print("Base_Final encontrada.")

    # Lendo registros antigos
    base_antiga = pd.read_excel(arquivo_final)

    # Remove as colunas vindas da referencia
    # para atualiza-las novamente
    base_antiga = base_antiga.drop(
        columns=["COORD", "Supervisor", "CLASSIFICACAO"], errors="ignore"
    )

    # Junta registros antigos + novos
    base_final = pd.concat([base_antiga, base_nova], ignore_index=True)

else:

    print("Base_Final ainda nao existe.")
    print("Criando uma nova Base_Final...")

    base_final = base_nova.copy()


# ==========================================
# 9. LENDO A BASE DE REFERENCIA
# ==========================================

base_referencia = pd.read_excel(arquivo_referencia, sheet_name="tbDEPARA")


# ==========================================
# 10. SELECIONANDO AS COLUNAS DO DEPARA
# ==========================================

base_referencia = base_referencia[
    ["Nome", "COORD", "Supervisor", "CLASSIFICACAO"]
].copy()


# ==========================================
# 11. RENOMEANDO NOME PARA RECURSO
# ==========================================

# Na tbDEPARA, "Nome" corresponde ao
# "Recurso" das bases TOA e ETA

base_referencia = base_referencia.rename(columns={"Nome": "Recurso"})


# ==========================================
# 12. TRATANDO A COLUNA RECURSO
# ==========================================

# Converte tudo para texto
# Remove espacos antes/depois
# Converte para maiusculo para facilitar a comparacao

base_final["Recurso"] = base_final["Recurso"].astype(str).str.strip().str.upper()

base_referencia["Recurso"] = (
    base_referencia["Recurso"].astype(str).str.strip().str.upper()
)


# ==========================================
# 13. REMOVENDO DUPLICADOS DO DEPARA
# ==========================================

# Se o mesmo Nome/Recurso aparecer mais de uma
# vez na tbDEPARA, sera mantido o ultimo registro.

base_referencia = base_referencia.drop_duplicates(subset=["Recurso"], keep="last")


# ==========================================
# 14. BUSCANDO COORD, SUPERVISOR E CLASSIFICACAO
# ==========================================

base_final = base_final.merge(base_referencia, on="Recurso", how="left")


# ==========================================
# 15. ORGANIZANDO AS COLUNAS
# ==========================================

# Essas colunas sempre ficarao no final

colunas_finais = ["COORD", "Supervisor", "CLASSIFICACAO"]

outras_colunas = [
    coluna for coluna in base_final.columns if coluna not in colunas_finais
]

base_final = base_final[outras_colunas + colunas_finais]


# ==========================================
# 16. VERIFICANDO RECURSOS NAO ENCONTRADOS
# ==========================================

recursos_nao_encontrados = (
    base_final[base_final["COORD"].isna()]["Recurso"].dropna().unique()
)


quantidade_nao_encontrados = len(recursos_nao_encontrados)


# ==========================================
# 17. SALVANDO A BASE FINAL
# ==========================================

base_final.to_excel(arquivo_final, index=False)


# ==========================================
# 18. RESULTADO
# ==========================================

print()
print("=" * 60)
print("BASE ATUALIZADA COM SUCESSO!")
print("=" * 60)

print(f"Dia da semana: {dia_semana}")

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

print(f"Recursos nao encontrados: " f"{quantidade_nao_encontrados}")

# Mostra quais recursos nao foram encontrados
if quantidade_nao_encontrados > 0:

    print()
    print("Recursos que nao existem na tbDEPARA:")

    for recurso in recursos_nao_encontrados:
        print(f"- {recurso}")

print()
print("=" * 60)
print(f"Arquivo salvo: {arquivo_final}")
print("=" * 60)
