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
# 8. MAPEAMENTO DOS TIPOS
# ==========================================

mapeamento_tipos = {
    # --------------------------------------
    # INSTALACAO
    # --------------------------------------
    "Instalação Internet X Light": "Instalação",
    "Instalação Roteador": "Instalação",
    "Instalação SIP": "Instalação",
    "INS SDWAN": "Instalação",
    "Instalação Dados": "Instalação",
    "Instalação Dados Roteador": "Instalação",
    "Instalação DDR": "Instalação",
    "Instalação Internet X": "Instalação",
    # --------------------------------------
    # INTERNO
    # --------------------------------------
    "Almoxarifado": "Interno",
    "Checklist": "Interno",
    "Exame Periódico": "Interno",
    "Manutenção de Veículo": "Interno",
    "Planta Interna": "Interno",
    "Refeição": "Interno",
    "Reunião": "Interno",
    "Treinamento": "Interno",
    "Refeição120": "Interno",
    "Refeição60": "Interno",
    "Refeição90": "Interno",
    "Reunião Interna": "Interno",
    # --------------------------------------
    # MELHORIA
    # --------------------------------------
    "Backbone": "Melhoria",
    "INS Melhoria": "Melhoria",
    "Migração de Acesso": "Melhoria",
    "Migração de rede": "Melhoria",
    "Migração Transmissão": "Melhoria",
    "Instalação DGO": "Melhoria",
    "Instalação DGO (Serviço Duplado)": "Melhoria",
    # --------------------------------------
    # OUTRAS
    # --------------------------------------
    "Ampliação Equipamento": "Outras",
    "Apoio Técnico": "Outras",
    "Ativação Porta Switch": "Outras",
    "Ativação Porta Switch Router": "Outras",
    "Atividade Móvel": "Outras",
    "Facilidade GPON": "Outras",
    "Infra ARD": "Outras",
    "Infra ARD CORP": "Outras",
    "Instalação ARD Novo": "Outras",
    "Migração SW": "Outras",
    "Porta Switch/Router": "Outras",
    "Pré-Ins": "Outras",
    "REQ Atividade": "Outras",
    "Serviço Dados": "Outras",
    "SWT Comissionamento": "Outras",
    "Teste de Rede": "Outras",
    "Viabilidade Técnica": "Outras",
    "Alteração Reinstalação de Linha": "Outras",
    "Antecipação Automatizada": "Outras",
    "Atividade Duplada - Vistoria": "Outras",
    "Atividade Escritório": "Outras",
    # --------------------------------------
    # REFEICAO
    # --------------------------------------
    "Refeição L": "Refeição",
    # --------------------------------------
    # REPARO
    # --------------------------------------
    "Manutenção Corretiva": "Reparo",
    "Manutenção Preventiva": "Reparo",
    "Preventiva CORP": "Reparo",
    "Reparo Dados": "Reparo",
    "Reparo DDR": "Reparo",
    "Reparo Rede": "Reparo",
    "Reparo Roteador": "Reparo",
    "Reparo OSP": "Reparo",
    "REPARO DE CIRCUITO - ROTEADOR/AMBIENTE CLIENTE - ERB": "Reparo",
    "REPARO REDE - ERB / B2B AVANÇADO (SWT)": "Reparo",
    "REPARO REDE - ERB / B2B avançado (SWT) (SERVIÇO DUPLADO)": "Reparo",
    "REPARO REDE ERB - READEQUAÇÃO DE POSTE (SERVIÇO DUPLADO)": "Reparo",
    "REPARO REDE ERB - REPARO EM DGO (SERVIÇO DUPLADO)": "Reparo",
    # --------------------------------------
    # VISTORIA
    # --------------------------------------
    "Testes": "Vistoria",
    "Testes de Portas": "Vistoria",
    "Vistoria": "Vistoria",
    "Vistoria BBN": "Vistoria",
    "Vistoria CORP": "Vistoria",
    "Vistoria VIVO": "Vistoria",
    "VISTORIA/GOLDEN JUMPER/INTEGRAÇÃO CLIENTE": "Vistoria",
    # --------------------------------------
    # ATIVACAO
    # --------------------------------------
    "ATIVAÇÃO CIRCUITO GPON": "Ativação",
    "ATIVAÇÃO CIRCUITO GPON (SERVIÇO DUPLADO)": "Ativação",
    "ATIVAÇÃO DE CIRCUITO - ROTEADOR/AMBIENTE CLIENTE - ERB": "Ativação",
    "Teste RFC (CAMADA 2 e 3)": "Ativação",
    # --------------------------------------
    # CAPACITACAO
    # --------------------------------------
    "INSTALAÇÃO SWA - CAPACITAÇÃO DE SITE": "Capacitação",
    "INSTALAÇÃO SWA - CAPACITAÇÃO DE SITE (SERVIÇO DUPLADO)": "Capacitação",
    # --------------------------------------
    # CONSTRUCAO
    # --------------------------------------
    "Construção de rede para B2B/Site até 300m": "Construção",
    "Construção de rede para B2B/Site até 300m (Serviço Duplado)": "Construção",
    "INS Rede Lançamento": "Construção",
    # --------------------------------------
    # DESLOCAMENTO
    # --------------------------------------
    "DESLOCAMENTO ACIMA DE 100 KM": "Deslocamento",
    # --------------------------------------
    # DESCONEXAO
    # --------------------------------------
    "RETIRADA SWT / ROUTER": "Desconexão",
    "Desconexão de Serviços": "Desconexão",
    "Desconexão Fibra": "Desconexão",
    "Desinstalação Equipamento": "Desconexão",
    "Retirada Dados": "Desconexão",
    "Retirada Dados Roteador": "Desconexão",
    "Retirada DDR": "Desconexão",
    "Retirada Roteador": "Desconexão",
}


# ==========================================
# 9. NORMALIZANDO O MAPEAMENTO
# ==========================================

mapeamento_normalizado = {
    str(tipo).strip().casefold(): valor for tipo, valor in mapeamento_tipos.items()
}


# ==========================================
# 10. FUNCAO PARA PADRONIZAR O TIPO
# ==========================================


def padronizar_tipo(valor):

    if pd.isna(valor):
        return ""

    valor_limpo = str(valor).strip()

    if valor_limpo == "":
        return ""

    resultado = mapeamento_normalizado.get(valor_limpo.casefold())

    if resultado is not None:
        return resultado

    return "NÃO MAPEADO"


# ==========================================
# 11. CRIANDO TIPO_PADRONIZADO
# SOMENTE NOS NOVOS REGISTROS
# ==========================================

base_toa["Tipo_Padronizado"] = base_toa["Tipo"].apply(padronizar_tipo)


base_eta["Tipo_Padronizado"] = base_eta["Tipo"].apply(padronizar_tipo)


# ==========================================
# 12. ORGANIZANDO A ORDEM DAS COLUNAS
# ==========================================

ordem_colunas = [
    "Recurso",
    "Tipo",
    "Status",
    "Data Concluída",
    "Origem",
    "Dia Semana",
    "Tipo_Padronizado",
]


base_toa = base_toa[ordem_colunas]

base_eta = base_eta[ordem_colunas]


# ==========================================
# 13. JUNTANDO TOA + ETA
# ==========================================

base_nova = pd.concat([base_toa, base_eta], ignore_index=True)


# ==========================================
# 14. VERIFICANDO TIPOS NAO MAPEADOS
# SOMENTE NOS NOVOS REGISTROS
# ==========================================

tipos_nao_mapeados = (
    base_nova.loc[base_nova["Tipo_Padronizado"] == "NÃO MAPEADO", "Tipo"]
    .dropna()
    .astype(str)
    .str.strip()
    .drop_duplicates()
    .tolist()
)


quantidade_tipos_nao_mapeados = len(tipos_nao_mapeados)


# ==========================================
# 15. VERIFICANDO SE BASE_FINAL JA EXISTE
# ==========================================

if os.path.exists(arquivo_final):

    print("Base_Final encontrada.")

    base_antiga = pd.read_excel(arquivo_final)

    # Remove somente as informações do DEPARA.
    # Elas serão preenchidas novamente.

    base_antiga = base_antiga.drop(
        columns=["COORD", "Supervisor", "CLASSIFICACAO"], errors="ignore"
    )

    # ======================================
    # GARANTINDO TIPO_PADRONIZADO
    # NA BASE ANTIGA
    # ======================================

    if "Tipo_Padronizado" not in base_antiga.columns:

        base_antiga["Tipo_Padronizado"] = base_antiga["Tipo"].apply(padronizar_tipo)

    # ======================================
    # CORRIGINDO DATA DA BASE ANTIGA
    # ======================================

    if "Data Concluída" in base_antiga.columns:

        base_antiga["Data Concluída"] = pd.to_datetime(
            base_antiga["Data Concluída"], errors="coerce", dayfirst=True
        )

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
# 16. TRATANDO A COLUNA RECURSO
# ANTES DAS EXCLUSOES
# ==========================================

base_final["Recurso"] = (
    base_final["Recurso"].fillna("").astype(str).str.strip().str.upper()
)


# ==========================================
# 17. IGNORANDO TECNICOS ESPECIFICOS
# ==========================================

tecnicos_ignorar = [
    "FABRICIO BARBOSA DE OLIVEIRA ANDRADE",
    "LUIZ BARRETO NOBRE NETO",
    "ROBERTO SOARES DE BRITO",
]


quantidade_antes_exclusao = len(base_final)


base_final = base_final[~base_final["Recurso"].isin(tecnicos_ignorar)].copy()


quantidade_registros_ignorados = quantidade_antes_exclusao - len(base_final)


# Reorganiza os índices após a exclusão
base_final = base_final.reset_index(drop=True)


# ==========================================
# 18. LENDO A BASE DE REFERENCIA
# ==========================================

base_referencia = pd.read_excel(arquivo_referencia, sheet_name="tbDEPARA")


# ==========================================
# 19. SELECIONANDO AS COLUNAS DO DEPARA
# ==========================================

base_referencia = base_referencia[
    ["Nome", "COORD", "Supervisor", "CLASSIFICACAO"]
].copy()


# ==========================================
# 20. RENOMEANDO NOME PARA RECURSO
# ==========================================

# Na tbDEPARA:
# Nome = Recurso das bases TOA e ETA

base_referencia = base_referencia.rename(columns={"Nome": "Recurso"})


# ==========================================
# 21. TRATANDO RECURSO DO DEPARA
# ==========================================

base_referencia["Recurso"] = (
    base_referencia["Recurso"].fillna("").astype(str).str.strip().str.upper()
)


# ==========================================
# 22. REMOVENDO RECURSOS VAZIOS DO DEPARA
# ==========================================

base_referencia = base_referencia[base_referencia["Recurso"] != ""]


# ==========================================
# 23. REMOVENDO DUPLICADOS DO DEPARA
# ==========================================

base_referencia = base_referencia.drop_duplicates(subset=["Recurso"], keep="last")


# ==========================================
# 24. BUSCANDO INFORMACOES NA tbDEPARA
# ==========================================

base_final = base_final.merge(base_referencia, on="Recurso", how="left")


# ==========================================
# 25. ORGANIZANDO AS COLUNAS FINAIS
# ==========================================

colunas_finais = ["COORD", "Supervisor", "CLASSIFICACAO", "Tipo_Padronizado"]


outras_colunas = [
    coluna for coluna in base_final.columns if coluna not in colunas_finais
]


base_final = base_final[outras_colunas + colunas_finais]


# ==========================================
# 26. VERIFICANDO RECURSOS NAO ENCONTRADOS
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
# 27. GARANTINDO QUE DATA CONTINUE COMO DATA
# ==========================================

base_final["Data Concluída"] = pd.to_datetime(
    base_final["Data Concluída"], errors="coerce", dayfirst=True
)


# ==========================================
# 28. SALVANDO A BASE FINAL
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
# 29. RESULTADO
# ==========================================

print()

print("=" * 60)

print("BASE ATUALIZADA COM SUCESSO!")

print("=" * 60)


# ==========================================
# REGISTROS ADICIONADOS
# ==========================================

print()

print("REGISTROS ADICIONADOS")

print("-" * 60)


print(f"TOA: {len(base_toa)}")

print(f"ETA: {len(base_eta)}")

print(f"Total novos: {len(base_nova)}")


# ==========================================
# TECNICOS IGNORADOS
# ==========================================

print()

print("TECNICOS IGNORADOS")

print("-" * 60)


for tecnico in tecnicos_ignorar:

    print(f"- {tecnico}")


print()

print(
    "Registros removidos dos técnicos ignorados: " f"{quantidade_registros_ignorados}"
)


# ==========================================
# BASE FINAL
# ==========================================

print()

print("BASE FINAL")

print("-" * 60)


print(f"Total de registros: {len(base_final)}")


# ==========================================
# DEPARA
# ==========================================

print()

print("DEPARA")

print("-" * 60)


print(f"Recursos não encontrados: " f"{quantidade_nao_encontrados}")


if quantidade_nao_encontrados > 0:

    print()

    print("Recursos que não existem na tbDEPARA:")

    for recurso in recursos_nao_encontrados:

        print(f"- {recurso}")


# ==========================================
# TIPO PADRONIZADO
# ==========================================

print()

print("TIPO PADRONIZADO")

print("-" * 60)


print(f"Tipos novos não mapeados: " f"{quantidade_tipos_nao_mapeados}")


if quantidade_tipos_nao_mapeados > 0:

    print()

    print("Tipos que precisam ser adicionados " "ao mapeamento:")

    for tipo in sorted(tipos_nao_mapeados):

        print(f"- {tipo}")

else:

    print("Todos os novos tipos foram " "mapeados com sucesso!")


# ==========================================
# 30. FINAL
# ==========================================

print()

print("=" * 60)

print(f"Arquivo salvo: {arquivo_final}")

print("Formato das datas: DD/MM/AAAA")

print("=" * 60)
