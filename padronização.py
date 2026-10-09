import pandas as pd

# ============================================================
# CONFIGURAÇÕES
# ============================================================

ARQUIVO_ENTRADA = (
    r"C:\Users\40419159\OneDrive - Telefonica\Área de Trabalho\Base_final.xlsx"
)

ARQUIVO_SAIDA = r"C:\Users\40419159\OneDrive - Telefonica\Área de Trabalho\Base_final_com_tipo_padronizado.xlsx"

COLUNA_TIPO = "Tipo"
COLUNA_PADRONIZADA = "Tipo_Padronizado"


# ============================================================
# 1. MAPEAMENTO DOS TIPOS
# ============================================================

MAPEAMENTO_TIPOS = {
    # --------------------------------------------------------
    # INSTALAÇÃO
    # --------------------------------------------------------
    "Instalação Internet X Light": "Instalação",
    "Instalação Roteador": "Instalação",
    "Instalação SIP": "Instalação",
    "INS SDWAN": "Instalação",
    "Instalação Dados": "Instalação",
    "Instalação Dados Roteador": "Instalação",
    "Instalação DDR": "Instalação",
    "Instalação Internet X": "Instalação",
    # --------------------------------------------------------
    # INTERNO
    # --------------------------------------------------------
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
    # --------------------------------------------------------
    # MELHORIA
    # --------------------------------------------------------
    "Backbone": "Melhoria",
    "INS Melhoria": "Melhoria",
    "Migração de Acesso": "Melhoria",
    "Migração de rede": "Melhoria",
    "Migração Transmissão": "Melhoria",
    "Instalação DGO": "Melhoria",
    "Instalação DGO (Serviço Duplado)": "Melhoria",
    # --------------------------------------------------------
    # OUTRAS / OUTRAS
    # --------------------------------------------------------
    "Ampliação Equipamento": "Outras",
    "Apoio Técnico": "OUTRAS",
    "Ativação Porta Switch": "OUTRAS",
    "Ativação Porta Switch Router": "OUTRAS",
    "Atividade Móvel": "OUTRAS",
    "Facilidade GPON": "OUTRAS",
    "Infra ARD": "OUTRAS",
    "Infra ARD CORP": "OUTRAS",
    "Instalação ARD Novo": "OUTRAS",
    "Migração SW": "OUTRAS",
    "Porta Switch/Router": "OUTRAS",
    "Pré-Ins": "OUTRAS",
    "REQ Atividade": "OUTRAS",
    "Serviço Dados": "OUTRAS",
    "SWT Comissionamento": "OUTRAS",
    "Teste de Rede": "OUTRAS",
    "Viabilidade Técnica": "OUTRAS",
    "Alteração Reinstalação de Linha": "Outras",
    "Antecipação Automatizada": "Outras",
    "Atividade Duplada - Vistoria": "OUTRAS",
    "Atividade Escritório": "OUTRAS",
    # --------------------------------------------------------
    # REFEIÇÃO
    # --------------------------------------------------------
    "Refeição L": "Refeição",
    # --------------------------------------------------------
    # REPARO
    # --------------------------------------------------------
    "Manutenção Corretiva": "Reparo",
    "Manutenção Preventiva": "Reparo",
    "Preventiva CORP": "Reparo",
    "Reparo Dados": "Reparo",
    "Reparo DDR": "Reparo",
    "Reparo Rede": "REPARO",
    "Reparo Roteador": "Reparo",
    "Reparo OSP": "Reparo",
    "REPARO DE CIRCUITO - ROTEADOR/AMBIENTE CLIENTE - ERB": "Reparo",
    "REPARO REDE - ERB / B2B AVANÇADO (SWT)": "Reparo",
    "REPARO REDE - ERB / B2B avançado (SWT) (SERVIÇO DUPLADO)": "Reparo",
    "REPARO REDE ERB - READEQUAÇÃO DE POSTE (SERVIÇO DUPLADO)": "Reparo",
    "REPARO REDE ERB - REPARO EM DGO (SERVIÇO DUPLADO)": "Reparo",
    # --------------------------------------------------------
    # VISTORIA
    # --------------------------------------------------------
    "Testes": "Vistoria",
    "Testes de Portas": "Vistoria",
    "Vistoria": "Vistoria",
    "Vistoria BBN": "Vistoria",
    "Vistoria CORP": "Vistoria",
    "Vistoria VIVO": "Vistoria",
    "VISTORIA/GOLDEN JUMPER/INTEGRAÇÃO CLIENTE": "Vistoria",
    # --------------------------------------------------------
    # ATIVAÇÃO
    # --------------------------------------------------------
    "ATIVAÇÃO CIRCUITO GPON": "Ativação",
    "ATIVAÇÃO CIRCUITO GPON (SERVIÇO DUPLADO)": "Ativação",
    "ATIVAÇÃO DE CIRCUITO - ROTEADOR/AMBIENTE CLIENTE - ERB": "Ativação",
    "Teste RFC (CAMADA 2 e 3)": "Ativação",
    # --------------------------------------------------------
    # CAPACITAÇÃO
    # --------------------------------------------------------
    "INSTALAÇÃO SWA - CAPACITAÇÃO DE SITE": "Capacitação",
    "INSTALAÇÃO SWA - CAPACITAÇÃO DE SITE (SERVIÇO DUPLADO)": "Capacitação",
    # --------------------------------------------------------
    # CONSTRUÇÃO
    # --------------------------------------------------------
    "Construção de rede para B2B/Site até 300m": "Construção",
    "Construção de rede para B2B/Site até 300m (Serviço Duplado)": "Construção",
    "INS Rede Lançamento": "Construção",
    # --------------------------------------------------------
    # DESLOCAMENTO
    # --------------------------------------------------------
    "DESLOCAMENTO ACIMA DE 100 KM": "Deslocamento",
    # --------------------------------------------------------
    # DESCONEXÃO
    # --------------------------------------------------------
    "RETIRADA SWT / ROUTER": "Desconexão",
    "Desconexão de Serviços": "Desconexão",
    "Desconexão Fibra": "Desconexão",
    "Desinstalação Equipamento": "Desconexão",
    "Retirada Dados": "Desconexão",
    "Retirada Dados Roteador": "Desconexão",
    "Retirada DDR": "Desconexão",
    "Retirada Roteador": "Desconexão",
}


# ============================================================
# 2. LER A BASE
# ============================================================

print("Lendo a Base_final...")

df = pd.read_excel(ARQUIVO_ENTRADA, sheet_name=0)


# ============================================================
# 3. VERIFICAR SE A COLUNA TIPO EXISTE
# ============================================================

if COLUNA_TIPO not in df.columns:
    raise ValueError(
        f'A coluna "{COLUNA_TIPO}" não foi encontrada na Base_final.\n'
        f"Colunas disponíveis:\n{list(df.columns)}"
    )


# ============================================================
# 4. FUNÇÃO PARA PADRONIZAR O TIPO
# ============================================================

# Criamos também uma versão normalizada do dicionário.
# Isso evita problemas com diferenças entre maiúsculas e
# minúsculas e espaços antes/depois do texto.

mapeamento_normalizado = {
    str(tipo).strip().casefold(): padronizado
    for tipo, padronizado in MAPEAMENTO_TIPOS.items()
}


def padronizar_tipo(valor):
    """
    Recebe o valor da coluna Tipo e retorna o Tipo_Padronizado.
    """

    # Se a célula estiver vazia
    if pd.isna(valor):
        return ""

    # Remove espaços extras
    valor_limpo = str(valor).strip()

    # Procura no mapeamento
    valor_padronizado = mapeamento_normalizado.get(valor_limpo.casefold())

    # Se encontrou
    if valor_padronizado is not None:
        return valor_padronizado

    # Se não encontrou no mapeamento
    return "NÃO MAPEADO"


# ============================================================
# 5. CRIAR A NOVA COLUNA
# ============================================================

df[COLUNA_PADRONIZADA] = df[COLUNA_TIPO].apply(padronizar_tipo)


# ============================================================
# 6. SALVAR A NOVA BASE
# ============================================================

df.to_excel(ARQUIVO_SAIDA, index=False, engine="openpyxl")


# ============================================================
# 7. MOSTRAR RESULTADO
# ============================================================

print("\n========================================")
print("PROCESSAMENTO CONCLUÍDO")
print("========================================")

print(f"\nNova coluna criada: {COLUNA_PADRONIZADA}")

print(f"\nBase salva em:\n{ARQUIVO_SAIDA}")

print(f"\nQuantidade total de registros: {len(df)}")


# ============================================================
# 8. VERIFICAR TIPOS QUE NÃO FORAM MAPEADOS
# ============================================================

nao_mapeados = (
    df.loc[df[COLUNA_PADRONIZADA] == "NÃO MAPEADO", COLUNA_TIPO]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)


if len(nao_mapeados) > 0:

    print("\n========================================")
    print("ATENÇÃO - TIPOS NÃO MAPEADOS")
    print("========================================")

    print(
        f"\nForam encontrados {len(nao_mapeados)} "
        "tipos diferentes sem correspondência:"
    )

    for tipo in sorted(nao_mapeados):
        print(f" - {tipo}")

else:

    print("\nTodos os tipos foram mapeados com sucesso!")
