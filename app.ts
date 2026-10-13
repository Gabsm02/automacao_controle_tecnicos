import type { HttpContextContract } from '@ioc:Adonis/Core/HttpContext'
import Database from '@ioc:Adonis/Lucid/Database'
import { DateTime } from 'luxon'

const UFS_VALIDAS = [
  'AL',
  'BA',
  'CE',
  'PB',
  'PE',
  'PI',
  'RN',
  'SE',
] as const

const PRIORIDADES_VALIDAS = [
  'P1',
  'P2',
  'P1+P2',
] as const

const RESPONSABILIDADES_VALIDAS = [
  'Terceira',
  'Regional',
] as const

const ITENS_POR_PAGINA = 25
const QUANTIDADE_MESES_EVOLUCAO = 12
const LIMITE_BUSCA = 200

type UfValida =
  (typeof UFS_VALIDAS)[number]

type PrioridadeValida =
  (typeof PRIORIDADES_VALIDAS)[number]

type ResponsabilidadeValida =
  (typeof RESPONSABILIDADES_VALIDAS)[number]

interface FiltrosCausa {
  uf: string
  ddd: string
  prioridade: string
  responsabilidade: string
  busca: string
  periodo: string
}

interface OpcoesFiltroCausa {
  ignorarPrioridade?: boolean
  ignorarResponsabilidade?: boolean
}

interface RegistroHistorico {
  periodo: string | Date
  total: number | string | null
  terceiraP1: number | string | null
  terceiraP2: number | string | null
  terceiraP3: number | string | null
  terceiraP4: number | string | null
  regionalP1: number | string | null
  regionalP2: number | string | null
  regionalP3: number | string | null
  regionalP4: number | string | null
  regional: string
  uf: string
  ddd: string
}

interface LinhaEvolucao {
  periodo: string
  terceiraP1: number | null
  regionalP1: number | null
  terceiraP2: number | null
  regionalP2: number | null
}

interface LinhaRanking {
  uf: string
  terceiraP1: number | null
  terceiraP2: number | null
  regionalP1: number | null
  regionalP2: number | null
}

interface LinhaRankingDdd {
  ddd: string
  terceiraP1: number | null
  regionalP1: number | null
  terceiraP2: number | null
  regionalP2: number | null
  gapP1: number | null
}

interface LinhaGapUf {
  uf: string
  terceiraP1: number | null
  regionalP1: number | null
  gapP1: number | null
}

interface RegistroCausaAgrupada {
  tipo_falha_rede?: string | null
  responsabilidade?: string | null
  prioridade?: string | null
  total?: number | string | null
}

interface ItemGraficoCausa {
  label: string
  total: number
}

interface RankingUfGrafico {
  uf: string
  terceiraP1: number | null
  regionalP1: number | null
  terceiraP2: number | null
  regionalP2: number | null
}

interface Kpi {
  baseline: number
  mediaTerceira: number | null
  mediaRegional: number | null
}

function normalizarTexto(
  valor: unknown
): string {
  return String(
    valor ?? ''
  ).trim()
}

function normalizarUf(
  valor: unknown
): string {
  const uf =
    normalizarTexto(
      valor
    ).toUpperCase()

  if (!uf) {
    return ''
  }

  return UFS_VALIDAS.includes(
    uf as UfValida
  )
    ? uf
    : ''
}

function normalizarDdd(
  valor: unknown
): string {
  const ddd =
    normalizarTexto(
      valor
    ).replace(
      /\D/g,
      ''
    )

  if (
    !ddd ||
    ddd.length !== 2
  ) {
    return ''
  }

  return ddd
}

function normalizarPrioridade(
  valor: unknown
): string {
  const prioridade =
    normalizarTexto(
      valor
    ).toUpperCase()

  if (!prioridade) {
    return ''
  }

  return PRIORIDADES_VALIDAS.includes(
    prioridade as PrioridadeValida
  )
    ? prioridade
    : ''
}

function normalizarResponsabilidade(
  valor: unknown
): string {
  const valorRecebido =
    normalizarTexto(
      valor
    )

  if (!valorRecebido) {
    return ''
  }

  const responsabilidade =
    RESPONSABILIDADES_VALIDAS.find(
      (
        item:
          ResponsabilidadeValida
      ) =>
        item.toLowerCase() ===
        valorRecebido.toLowerCase()
    )

  return responsabilidade ?? ''
}

function normalizarPagina(
  valor: unknown
): number {
  const pagina =
    Number(valor)

  if (
    !Number.isInteger(
      pagina
    ) ||
    pagina < 1
  ) {
    return 1
  }

  return pagina
}

function normalizarBusca(
  valor: unknown
): string {
  return normalizarTexto(
    valor
  ).slice(
    0,
    LIMITE_BUSCA
  )
}

function validarPeriodo(
  periodo: unknown
): string | null {
  const valor =
    normalizarTexto(
      periodo
    )

  if (!valor) {
    return null
  }

  if (
    !/^(0[1-9]|1[0-2])\/\d{4}$/.test(
      valor
    )
  ) {
    return null
  }

  const data =
    DateTime.fromFormat(
      valor,
      'MM/yyyy',
      {
        zone: 'utc',
        locale: 'pt-BR',
      }
    )

  if (!data.isValid) {
    return null
  }

  return data.toFormat(
    'MM/yyyy'
  )
}

function converterNumero(
  valor: unknown
): number | null {
  if (
    valor === null ||
    valor === undefined ||
    valor === ''
  ) {
    return null
  }

  if (
    typeof valor === 'string'
  ) {
    const texto =
      valor.trim()

    if (!texto) {
      return null
    }

    const normalizado =
      texto.includes(',') &&
      !texto.includes('.')
        ? texto.replace(
            ',',
            '.'
          )
        : texto

    const numero =
      Number(normalizado)

    return Number.isFinite(
      numero
    )
      ? numero
      : null
  }

  const numero =
    Number(valor)

  return Number.isFinite(
    numero
  )
    ? numero
    : null
}

function converterParaArray<T>(
  valor: unknown
): T[] {
  if (!Array.isArray(valor)) {
    return []
  }

  return valor as T[]
}

function calcularMedia(
  valores: unknown[]
): number | null {
  const numeros =
    valores
      .map(
        (
          valor:
            unknown
        ) =>
          converterNumero(
            valor
          )
      )
      .filter(
        (
          valor:
            number | null
        ): valor is number =>
          valor !== null
      )

  if (
    numeros.length === 0
  ) {
    return null
  }

  const soma =
    numeros.reduce(
      (
        acumulador:
          number,
        valor:
          number
      ) =>
        acumulador +
        valor,
      0
    )

  return (
    soma /
    numeros.length
  )
}

function calcularSoma(
  valores: unknown[]
): number {
  return valores.reduce(
    (
      acumulador:
        number,
      valor:
        unknown
    ) =>
      acumulador +
      (
        converterNumero(
          valor
        ) ?? 0
      ),
    0
  )
}

function formatarChavePeriodo(
  periodo:
    string | Date
): string | null {
  if (
    periodo instanceof Date
  ) {
    const data =
      DateTime.fromJSDate(
        periodo,
        {
          zone: 'utc',
        }
      )

    return data.isValid
      ? data.toFormat(
          'yyyy-MM'
        )
      : null
  }

  const valor =
    normalizarTexto(
      periodo
    )

  if (!valor) {
    return null
  }

  const formatosPermitidos = [
    'yyyy-MM-dd',
    'yyyy-MM-dd HH:mm:ss',
    'yyyy-MM-dd HH:mm:ss.SSS',
    'yyyy-MM',
    'MM/yyyy',
  ]

  for (
    const formato
    of formatosPermitidos
  ) {
    const data =
      DateTime.fromFormat(
        valor,
        formato,
        {
          zone: 'utc',
        }
      )

    if (data.isValid) {
      return data.toFormat(
        'yyyy-MM'
      )
    }
  }

  const dataIso =
    DateTime.fromISO(
      valor,
      {
        zone: 'utc',
      }
    )

  return dataIso.isValid
    ? dataIso.toFormat(
        'yyyy-MM'
      )
    : null
}

function obterIntervaloPeriodo(
  periodo: string
): {
  inicio: string
  fim: string
} | null {
  const periodoValido =
    validarPeriodo(
      periodo
    )

  if (!periodoValido) {
    return null
  }

  const data =
    DateTime.fromFormat(
      periodoValido,
      'MM/yyyy',
      {
        zone: 'utc',
      }
    )

  if (!data.isValid) {
    return null
  }

  return {
    inicio:
      data
        .startOf('month')
        .toFormat(
          'yyyy-MM-dd'
        ),

    fim:
      data
        .plus({
          months: 1,
        })
        .startOf('month')
        .toFormat(
          'yyyy-MM-dd'
        ),
  }
}

function aplicarFiltrosCausa(
  query: any,
  filtros: FiltrosCausa,
  opcoes:
    OpcoesFiltroCausa = {}
): any {
  if (filtros.uf) {
    query.where(
      'uf',
      filtros.uf
    )
  }

  if (filtros.ddd) {
    query.where(
      'ddd',
      filtros.ddd
    )
  }

  if (
    filtros.prioridade &&
    !opcoes
      .ignorarPrioridade
  ) {
    query.where(
      'prioridade',
      filtros.prioridade
    )
  }

  if (
    filtros.responsabilidade &&
    !opcoes
      .ignorarResponsabilidade
  ) {
    query.where(
      'responsabilidade',
      filtros.responsabilidade
    )
  }

  if (filtros.busca) {
    const termoBusca =
      `%${filtros.busca}%`

    query.where(
      (
        subQuery:
          any
      ) => {
        subQuery
          .where(
            'evento',
            'like',
            termoBusca
          )
          .orWhere(
            'municipio',
            'like',
            termoBusca
          )
          .orWhere(
            'sigla',
            'like',
            termoBusca
          )
          .orWhere(
            'ddd',
            'like',
            termoBusca
          )
          .orWhere(
            'tipo_falha_rede',
            'like',
            termoBusca
          )
          .orWhere(
            'justificativas',
            'like',
            termoBusca
          )
          .orWhere(
            'descricao_justificativa',
            'like',
            termoBusca
          )
      }
    )
  }

  if (
    filtros.periodo
  ) {
    const intervalo =
      obterIntervaloPeriodo(
        filtros.periodo
      )

    if (intervalo) {
      query
        .where(
          'dia',
          '>=',
          intervalo.inicio
        )
        .where(
          'dia',
          '<',
          intervalo.fim
        )
    }
  }

  return query
}

function extrairContagem(
  resultado: unknown
): number {
  const linhas =
    converterParaArray<{
      total?:
        string |
        number |
        null
    }>(
      resultado
    )

  if (
    linhas.length === 0
  ) {
    return 0
  }

  return (
    converterNumero(
      linhas[0]?.total
    ) ?? 0
  )
}

function semaforoP1(
  valor:
    number | null
): string {
  if (valor === null) {
    return '#94a3b8'
  }

  if (valor >= 80) {
    return '#63D600'
  }

  if (valor >= 75) {
    return '#FFB428'
  }

  return '#EB3C7D'
}

function semaforoP2(
  valor:
    number | null
): string {
  if (valor === null) {
    return '#94a3b8'
  }

  if (valor >= 70) {
    return '#63D600'
  }

  if (valor >= 65) {
    return '#FFB428'
  }

  return '#EB3C7D'
}

function criarQueryHistoricoBase(
  conn: any
): any {
  return conn
    .from(
      'baseline_historico'
    )
    .select(
      'periodo',
      'total',
      'regional',
      'uf',
      'ddd',

      conn.raw(
        'media_p1 AS terceiraP1'
      ),

      conn.raw(
        'media_p2 AS terceiraP2'
      ),

      conn.raw(
        'media_p3 AS terceiraP3'
      ),

      conn.raw(
        'media_p4 AS terceiraP4'
      ),

      conn.raw(
        'media_p1_regional AS regionalP1'
      ),

      conn.raw(
        'media_p2_regional AS regionalP2'
      ),

      conn.raw(
        'media_p3_regional AS regionalP3'
      ),

      conn.raw(
        'media_p4_regional AS regionalP4'
      )
    )
    .where(
      'regional',
      'NE'
    )
}

function aplicarNivelHistorico(
  query: any,
  uf: string
): any {
  if (uf) {
    query.where(
      'ddd',
      uf
    )

    return query
  }

  query.where(
    'ddd',
    'NE'
  )

  return query
}

function montarEvolucao(
  registrosEvolucao:
    RegistroHistorico[],
  periodoRef:
    string | null
): LinhaEvolucao[] {
  const historicoPorPeriodo =
    new Map<
      string,
      RegistroHistorico[]
    >()

  for (
    const registro
    of registrosEvolucao
  ) {
    const chavePeriodo =
      formatarChavePeriodo(
        registro.periodo
      )

    if (!chavePeriodo) {
      continue
    }

    const existentes =
      historicoPorPeriodo.get(
        chavePeriodo
      ) ?? []

    existentes.push(
      registro
    )

    historicoPorPeriodo.set(
      chavePeriodo,
      existentes
    )
  }

  let chaves =
    Array.from(
      historicoPorPeriodo.keys()
    ).sort(
      (
        periodoA:
          string,
        periodoB:
          string
      ) =>
        periodoA.localeCompare(
          periodoB
        )
    )

  if (periodoRef) {
    const limite =
      DateTime.fromFormat(
        periodoRef,
        'MM/yyyy',
        {
          zone: 'utc',
        }
      ).toFormat(
        'yyyy-MM'
      )

    chaves =
      chaves.filter(
        (
          chave:
            string
        ) =>
          chave <= limite
      )
  }

  chaves =
    chaves.slice(
      -QUANTIDADE_MESES_EVOLUCAO
    )

  return chaves.map(
    (
      chave:
        string
    ): LinhaEvolucao => {
      const registros =
        historicoPorPeriodo.get(
          chave
        ) ?? []

      const periodoFormatado =
        DateTime.fromFormat(
          chave,
          'yyyy-MM',
          {
            zone: 'utc',
          }
        ).toFormat(
          'MM/yyyy'
        )

      return {
        periodo:
          periodoFormatado,

        terceiraP1:
          calcularMedia(
            registros.map(
              (
                registro:
                  RegistroHistorico
              ) =>
                registro
                  .terceiraP1
            )
          ),

        regionalP1:
          calcularMedia(
            registros.map(
              (
                registro:
                  RegistroHistorico
              ) =>
                registro
                  .regionalP1
            )
          ),

        terceiraP2:
          calcularMedia(
            registros.map(
              (
                registro:
                  RegistroHistorico
              ) =>
                registro
                  .terceiraP2
            )
          ),

        regionalP2:
          calcularMedia(
            registros.map(
              (
                registro:
                  RegistroHistorico
              ) =>
                registro
                  .regionalP2
            )
          ),
      }
    }
  )
}

function montarRanking(
  registros:
    RegistroHistorico[]
): LinhaRanking[] {
  const rankingPorUf =
    new Map<
      string,
      RegistroHistorico[]
    >()

  for (
    const registro
    of registros
  ) {
    const uf =
      normalizarUf(
        registro.uf
      )

    if (!uf) {
      continue
    }

    const existentes =
      rankingPorUf.get(
        uf
      ) ?? []

    existentes.push(
      registro
    )

    rankingPorUf.set(
      uf,
      existentes
    )
  }

  return Array.from(
    rankingPorUf.entries()
  )
    .map(
      ([
        uf,
        registrosUf,
      ]): LinhaRanking => ({
        uf,

        terceiraP1:
          calcularMedia(
            registrosUf.map(
              (
                registro:
                  RegistroHistorico
              ) =>
                registro
                  .terceiraP1
            )
          ),

        terceiraP2:
          calcularMedia(
            registrosUf.map(
              (
                registro:
                  RegistroHistorico
              ) =>
                registro
                  .terceiraP2
            )
          ),

        regionalP1:
          calcularMedia(
            registrosUf.map(
              (
                registro:
                  RegistroHistorico
              ) =>
                registro
                  .regionalP1
            )
          ),

        regionalP2:
          calcularMedia(
            registrosUf.map(
              (
                registro:
                  RegistroHistorico
              ) =>
                registro
                  .regionalP2
            )
          ),
      })
    )
    .sort(
      (
        itemA:
          LinhaRanking,
        itemB:
          LinhaRanking
      ) => {
        const valorA =
          itemA.terceiraP1 ?? -1

        const valorB =
          itemB.terceiraP1 ?? -1

        if (
          valorA !== valorB
        ) {
          return valorB - valorA
        }

        return itemA.uf.localeCompare(
          itemB.uf
        )
      }
    )
}

function montarItensGrafico(
  resultado: unknown,
  campo:
    'tipo_falha_rede' |
    'responsabilidade' |
    'prioridade'
): ItemGraficoCausa[] {
  const linhas =
    converterParaArray<
      RegistroCausaAgrupada
    >(
      resultado
    )

  return linhas
    .map(
      (
        item:
          RegistroCausaAgrupada
      ): ItemGraficoCausa => ({
        label:
          normalizarTexto(
            item[campo]
          ) ||
          'Não informado',

        total:
          converterNumero(
            item.total
          ) ?? 0,
      })
    )
    .filter(
      (
        item:
          ItemGraficoCausa
      ) =>
        item.total > 0
    )
}

export default class GuardiaoBaselineController {
  public async index({
    request,
    view,
    response,
  }: HttpContextContract) {
    const conn =
      Database.connection(
        'mysql'
      )

    const pagina =
      normalizarPagina(
        request.input(
          'page',
          1
        )
      )

    const filtros:
      FiltrosCausa = {
      uf:
        normalizarUf(
          request.input(
            'uf',
            ''
          )
        ),

      ddd:
        normalizarDdd(
          request.input(
            'ddd',
            ''
          )
        ),

      prioridade:
        normalizarPrioridade(
          request.input(
            'prioridade',
            ''
          )
        ),

      responsabilidade:
        normalizarResponsabilidade(
          request.input(
            'responsabilidade',
            ''
          )
        ),

      busca:
        normalizarBusca(
          request.input(
            'busca',
            ''
          )
        ),

      periodo: '',
    }

    const periodoRecebido =
      normalizarTexto(
        request.input(
          'periodo',
          ''
        )
      )

    const periodoInformado =
      validarPeriodo(
        periodoRecebido
      )

    if (
      periodoRecebido &&
      !periodoInformado
    ) {
      return response
        .status(422)
        .send({
          success: false,

          message:
            'Período inválido. Informe no formato MM/AAAA.',
        })
    }

    try {
      const ultimoPeriodoRegistro =
        await conn
          .from(
            'baseline_historico'
          )
          .select(
            'periodo'
          )
          .whereNotNull(
            'periodo'
          )
          .whereRaw(`
            TRIM(periodo) <> ''
          `)
          .orderByRaw(`
            STR_TO_DATE(
              TRIM(periodo),
              '%m/%Y'
            ) DESC
          `)
          .first()

      const periodoMaisRecente =
        validarPeriodo(
          ultimoPeriodoRegistro
            ?.periodo
        )

      const periodoRef =
        periodoInformado ??
        periodoMaisRecente

      filtros.periodo =
        periodoRef ?? ''

      const queryCausas =
        aplicarFiltrosCausa(
          conn
            .from(
              'causa_ofensora'
            )
            .select(
              'id',
              'evento',
              'tipo_falha_rede',
              'uf',
              'municipio',
              'dia',
              'ddd',
              'prioridade',
              'sigla',
              'responsabilidade',
              'justificativas',
              'descricao_justificativa',
              'atualizado_em',

              conn.raw(`
                DATE_FORMAT(
                  dia,
                  '%d/%m/%Y'
                ) AS dia_formatado
              `),

              conn.raw(`
                DATE_FORMAT(
                  atualizado_em,
                  '%d/%m/%Y %H:%i:%s'
                ) AS atualizado_em_formatado
              `)
            )
            .orderBy(
              'dia',
              'desc'
            )
            .orderBy(
              'evento',
              'desc'
            ),
          filtros
        )

      const queryTotalTerceira =
        aplicarFiltrosCausa(
          conn.from(
            'causa_ofensora'
          ),
          filtros,
          {
            ignorarResponsabilidade:
              true,
          }
        )
          .where(
            'responsabilidade',
            'Terceira'
          )
          .count(
            '* as total'
          )

      const queryTotalRegional =
        aplicarFiltrosCausa(
          conn.from(
            'causa_ofensora'
          ),
          filtros,
          {
            ignorarResponsabilidade:
              true,
          }
        )
          .where(
            'responsabilidade',
            'Regional'
          )
          .count(
            '* as total'
          )

      const queryTotalP1 =
        aplicarFiltrosCausa(
          conn.from(
            'causa_ofensora'
          ),
          filtros,
          {
            ignorarPrioridade:
              true,
          }
        )
          .where(
            'prioridade',
            'P1'
          )
          .count(
            '* as total'
          )

      const queryTotalP2 =
        aplicarFiltrosCausa(
          conn.from(
            'causa_ofensora'
          ),
          filtros,
          {
            ignorarPrioridade:
              true,
          }
        )
          .where(
            'prioridade',
            'P2'
          )
          .count(
            '* as total'
          )

      const queryTotalP1P2 =
        aplicarFiltrosCausa(
          conn.from(
            'causa_ofensora'
          ),
          filtros,
          {
            ignorarPrioridade:
              true,
          }
        )
          .where(
            'prioridade',
            'P1+P2'
          )
          .count(
            '* as total'
          )

      const queryCausasPorTipoFalha =
        aplicarFiltrosCausa(
          conn.from(
            'causa_ofensora'
          ),
          filtros
        )
          .select(
            'tipo_falha_rede'
          )
          .count(
            '* as total'
          )
          .whereNotNull(
            'tipo_falha_rede'
          )
          .whereRaw(`
            TRIM(tipo_falha_rede) <> ''
          `)
          .groupBy(
            'tipo_falha_rede'
          )
          .orderByRaw(`
            COUNT(*) DESC
          `)
          .limit(10)

      const queryCausasPorResponsabilidade =
        aplicarFiltrosCausa(
          conn.from(
            'causa_ofensora'
          ),
          filtros,
          {
            ignorarResponsabilidade:
              true,
          }
        )
          .select(
            'responsabilidade'
          )
          .count(
            '* as total'
          )
          .whereIn(
            'responsabilidade',
            [
              'Terceira',
              'Regional',
            ]
          )
          .groupBy(
            'responsabilidade'
          )
          .orderByRaw(`
            COUNT(*) DESC
          `)

      const queryCausasPorPrioridade =
        aplicarFiltrosCausa(
          conn.from(
            'causa_ofensora'
          ),
          filtros,
          {
            ignorarPrioridade:
              true,
          }
        )
          .select(
            'prioridade'
          )
          .count(
            '* as total'
          )
          .whereIn(
            'prioridade',
            [
              'P1',
              'P2',
              'P1+P2',
            ]
          )
          .groupBy(
            'prioridade'
          )

      const queryHistoricoMes =
        aplicarNivelHistorico(
          criarQueryHistoricoBase(
            conn
          ),
          filtros.uf
        )

      if (periodoRef) {
        queryHistoricoMes.whereRaw(
          `
            TRIM(periodo) = ?
          `,
          [
            periodoRef,
          ]
        )
      }

      const queryEvolucao =
        aplicarNivelHistorico(
          criarQueryHistoricoBase(
            conn
          ),
          filtros.uf
        )
          .whereNotNull(
            'periodo'
          )
          .whereRaw(`
            TRIM(periodo) <> ''
          `)
          .orderByRaw(`
            STR_TO_DATE(
              TRIM(periodo),
              '%m/%Y'
            ) ASC
          `)

      if (periodoRef) {
        queryEvolucao.whereRaw(
          `
            STR_TO_DATE(
              TRIM(periodo),
              '%m/%Y'
            ) <= STR_TO_DATE(
              ?,
              '%m/%Y'
            )
          `,
          [
            periodoRef,
          ]
        )
      }

      const queryRankingUf =
        criarQueryHistoricoBase(
          conn
        )
          .whereIn(
            'uf',
            filtros.uf
              ? [
                  filtros.uf,
                ]
              : [
                  ...UFS_VALIDAS,
                ]
          )
          .whereRaw(`
            TRIM(ddd) = TRIM(uf)
          `)

      if (periodoRef) {
        queryRankingUf.whereRaw(
          `
            TRIM(periodo) = ?
          `,
          [
            periodoRef,
          ]
        )
      }

      const queryRankingDdd =
        criarQueryHistoricoBase(
          conn
        )
          .whereRaw(`
            TRIM(ddd) REGEXP '^[0-9]{2}$'
          `)

      if (filtros.uf) {
        queryRankingDdd.where(
          'uf',
          filtros.uf
        )
      }

      if (filtros.ddd) {
        queryRankingDdd.where(
          'ddd',
          filtros.ddd
        )
      }

      if (periodoRef) {
        queryRankingDdd.whereRaw(
          `
            TRIM(periodo) = ?
          `,
          [
            periodoRef,
          ]
        )
      }

      const resultados =
        await Promise.all([
          queryCausas.paginate(
            pagina,
            ITENS_POR_PAGINA
          ),

          queryTotalTerceira,
          queryTotalRegional,
          queryTotalP1,
          queryTotalP2,
          queryTotalP1P2,
          queryHistoricoMes,
          queryEvolucao,
          queryRankingUf,
          queryRankingDdd,
          queryCausasPorTipoFalha,
          queryCausasPorResponsabilidade,
          queryCausasPorPrioridade,
        ])

      const causas =
        resultados[0]

      const resultadoTerceira =
        resultados[1]

      const resultadoRegional =
        resultados[2]

      const resultadoP1 =
        resultados[3]

      const resultadoP2 =
        resultados[4]

      const resultadoP1P2 =
        resultados[5]

      const registrosMes =
        converterParaArray<
          RegistroHistorico
        >(
          resultados[6]
        )

      const registrosEvolucao =
        converterParaArray<
          RegistroHistorico
        >(
          resultados[7]
        )

      const registrosRankingUf =
        converterParaArray<
          RegistroHistorico
        >(
          resultados[8]
        )

      const registrosRankingDdd =
        converterParaArray<
          RegistroHistorico
        >(
          resultados[9]
        )

      causas.baseUrl(
        '/guardiao-baseline'
      )

      causas.queryString({
        uf:
          filtros.uf,

        ddd:
          filtros.ddd,

        prioridade:
          filtros.prioridade,

        responsabilidade:
          filtros.responsabilidade,

        busca:
          filtros.busca,

        periodo:
          periodoRef ?? '',
      })

      const paginaAtual =
        Number(
          causas.currentPage || 1
        )

      const ultimaPagina =
        Number(
          causas.lastPage || 1
        )

      const paginaInicial =
        Math.max(
          1,
          paginaAtual - 2
        )

      const paginaFinal =
        Math.min(
          ultimaPagina,
          paginaAtual + 2
        )

      const baselineMes =
        calcularSoma(
          registrosMes.map(
            (
              registro:
                RegistroHistorico
            ) =>
              registro.total
          )
        )

      const kpiP1: Kpi = {
        baseline:
          baselineMes,

        mediaTerceira:
          calcularMedia(
            registrosMes.map(
              (
                registro:
                  RegistroHistorico
              ) =>
                registro
                  .terceiraP1
            )
          ),

        mediaRegional:
          calcularMedia(
            registrosMes.map(
              (
                registro:
                  RegistroHistorico
              ) =>
                registro
                  .regionalP1
            )
          ),
      }

      const kpiP2: Kpi = {
        baseline:
          baselineMes,

        mediaTerceira:
          calcularMedia(
            registrosMes.map(
              (
                registro:
                  RegistroHistorico
              ) =>
                registro
                  .terceiraP2
            )
          ),

        mediaRegional:
          calcularMedia(
            registrosMes.map(
              (
                registro:
                  RegistroHistorico
              ) =>
                registro
                  .regionalP2
            )
          ),
      }

      const gapRegional =
        kpiP1.mediaTerceira !== null &&
        kpiP1.mediaRegional !== null
          ? Number(
              (
                kpiP1.mediaTerceira -
                kpiP1.mediaRegional
              ).toFixed(1)
            )
          : null

      const evolucao =
        montarEvolucao(
          registrosEvolucao,
          periodoRef
        )

      const ranking =
        montarRanking(
          registrosRankingUf
        )

      const rankingUfGrafico:
        RankingUfGrafico[] =
        ranking.map(
          (
            item:
              LinhaRanking
          ): RankingUfGrafico => ({
            uf:
              item.uf,

            terceiraP1:
              item.terceiraP1,

            regionalP1:
              item.regionalP1,

            terceiraP2:
              item.terceiraP2,

            regionalP2:
              item.regionalP2,
          })
        )

      const gapUfRegional:
        LinhaGapUf[] =
        ranking
          .map(
            (
              item:
                LinhaRanking
            ): LinhaGapUf => {
              const gapP1 =
                item.terceiraP1 !== null &&
                item.regionalP1 !== null
                  ? Number(
                      (
                        item.terceiraP1 -
                        item.regionalP1
                      ).toFixed(1)
                    )
                  : null

              return {
                uf:
                  item.uf,

                terceiraP1:
                  item.terceiraP1,

                regionalP1:
                  item.regionalP1,

                gapP1,
              }
            }
          )
          .sort(
            (
              itemA:
                LinhaGapUf,
              itemB:
                LinhaGapUf
            ) =>
              Math.abs(
                itemB.gapP1 ?? 0
              ) -
              Math.abs(
                itemA.gapP1 ?? 0
              )
          )

      const rankingPorDdd =
        new Map<
          string,
          RegistroHistorico[]
        >()

      for (
        const registro
        of registrosRankingDdd
      ) {
        const ddd =
          normalizarDdd(
            registro.ddd
          )

        if (!ddd) {
          continue
        }

        const existentes =
          rankingPorDdd.get(
            ddd
          ) ?? []

        existentes.push(
          registro
        )

        rankingPorDdd.set(
          ddd,
          existentes
        )
      }

      const rankingDdd:
        LinhaRankingDdd[] =
        Array.from(
          rankingPorDdd.entries()
        )
          .map(
            ([
              ddd,
              registros,
            ]): LinhaRankingDdd => {
              const terceiraP1 =
                calcularMedia(
                  registros.map(
                    (
                      registro:
                        RegistroHistorico
                    ) =>
                      registro
                        .terceiraP1
                  )
                )

              const regionalP1 =
                calcularMedia(
                  registros.map(
                    (
                      registro:
                        RegistroHistorico
                    ) =>
                      registro
                        .regionalP1
                  )
                )

              const terceiraP2 =
                calcularMedia(
                  registros.map(
                    (
                      registro:
                        RegistroHistorico
                    ) =>
                      registro
                        .terceiraP2
                  )
                )

              const regionalP2 =
                calcularMedia(
                  registros.map(
                    (
                      registro:
                        RegistroHistorico
                    ) =>
                      registro
                        .regionalP2
                  )
                )

              const gapP1 =
                terceiraP1 !== null &&
                regionalP1 !== null
                  ? Number(
                      (
                        terceiraP1 -
                        regionalP1
                      ).toFixed(1)
                    )
                  : null

              return {
                ddd,
                terceiraP1,
                regionalP1,
                terceiraP2,
                regionalP2,
                gapP1,
              }
            }
          )
          .sort(
            (
              itemA:
                LinhaRankingDdd,
              itemB:
                LinhaRankingDdd
            ) => {
              const valorA =
                itemA.terceiraP1 ?? -1

              const valorB =
                itemB.terceiraP1 ?? -1

              if (
                valorA !== valorB
              ) {
                return valorB - valorA
              }

              return itemA.ddd.localeCompare(
                itemB.ddd
              )
            }
          )

      const rankingUfRegional =
        [
          ...ranking,
        ]
          .filter(
            (
              item:
                LinhaRanking
            ) =>
              item.regionalP1 !== null
          )
          .sort(
            (
              itemA:
                LinhaRanking,
              itemB:
                LinhaRanking
            ) => {
              const valorA =
                itemA.regionalP1 ?? -1

              const valorB =
                itemB.regionalP1 ?? -1

              if (
                valorA !== valorB
              ) {
                return valorB - valorA
              }

              return itemA.uf.localeCompare(
                itemB.uf
              )
            }
          )

      const melhorUf =
        rankingUfRegional.length > 0
          ? rankingUfRegional[0].uf
          : '-'

      const ufCritica =
        rankingUfRegional.length > 0
          ? rankingUfRegional[
              rankingUfRegional.length - 1
            ].uf
          : '-'

      const rankingDddRegional =
        [
          ...rankingDdd,
        ]
          .filter(
            (
              item:
                LinhaRankingDdd
            ) =>
              item.regionalP1 !== null
          )
          .sort(
            (
              itemA:
                LinhaRankingDdd,
              itemB:
                LinhaRankingDdd
            ) => {
              const valorA =
                itemA.regionalP1 ?? -1

              const valorB =
                itemB.regionalP1 ?? -1

              if (
                valorA !== valorB
              ) {
                return valorB - valorA
              }

              return itemA.ddd.localeCompare(
                itemB.ddd
              )
            }
          )

      const melhorDdd =
        rankingDddRegional.length > 0
          ? rankingDddRegional[0].ddd
          : '-'

      const dddCritico =
        rankingDddRegional.length > 0
          ? rankingDddRegional[
              rankingDddRegional.length -
              1
            ].ddd
          : '-'

      const totalTerceira =
        extrairContagem(
          resultadoTerceira
        )

      const totalRegional =
        extrairContagem(
          resultadoRegional
        )

      const totalP1 =
        extrairContagem(
          resultadoP1
        )

      const totalP2 =
        extrairContagem(
          resultadoP2
        )

      const totalP1P2 =
        extrairContagem(
          resultadoP1P2
        )

      const causasPorTipoFalha =
        montarItensGrafico(
          resultados[10],
          'tipo_falha_rede'
        )

      const causasPorResponsabilidade =
        montarItensGrafico(
          resultados[11],
          'responsabilidade'
        )

      const ordemPrioridade =
        new Map<
          string,
          number
        >([
          [
            'P1',
            1,
          ],
          [
            'P2',
            2,
          ],
          [
            'P1+P2',
            3,
          ],
        ])

      const causasPorPrioridade =
        montarItensGrafico(
          resultados[12],
          'prioridade'
        ).sort(
          (
            itemA:
              ItemGraficoCausa,
            itemB:
              ItemGraficoCausa
          ) =>
            (
              ordemPrioridade.get(
                itemA.label
              ) ?? 99
            ) -
            (
              ordemPrioridade.get(
                itemB.label
              ) ?? 99
            )
        )

      return view.render(
        'guardiao-baseline/index',
        {
          causas,

          paginaAtual,
          ultimaPagina,
          paginaInicial,
          paginaFinal,

          filtros: {
            ...filtros,

            periodo:
              periodoRef ?? '',
          },

          periodoRef,

          ufSelecionada:
            filtros.uf,

          ufsValidas: [
            ...UFS_VALIDAS,
          ],

          prioridadesValidas: [
            ...PRIORIDADES_VALIDAS,
          ],

          responsabilidadesValidas: [
            ...RESPONSABILIDADES_VALIDAS,
          ],

          totalTerceira,
          totalRegional,
          totalP1,
          totalP2,
          totalP1P2,

          kpiP1,
          kpiP2,

          corP1Terceira:
            semaforoP1(
              kpiP1.mediaTerceira
            ),

          corP1Regional:
            semaforoP1(
              kpiP1.mediaRegional
            ),

          corP2Terceira:
            semaforoP2(
              kpiP2.mediaTerceira
            ),

          corP2Regional:
            semaforoP2(
              kpiP2.mediaRegional
            ),

          corP1:
            semaforoP1(
              kpiP1.mediaTerceira
            ),

          corP2:
            semaforoP2(
              kpiP2.mediaTerceira
            ),

          evolucao,
          ranking,
          rankingDdd,
          rankingUfGrafico,

          rankingDddGrafico:
            rankingDdd,

          gapRegional,
          gapUfRegional,

          causasPorTipoFalha,
          causasPorResponsabilidade,
          causasPorPrioridade,

          melhorUf,
          ufCritica,
          melhorDdd,
          dddCritico,
        }
      )
    } catch (
      error:
        unknown
    ) {
      console.error(
        '[GuardiaoBaselineController.index]',
        error
      )

      const mensagemErro =
        error instanceof Error
          ? error.message
          : String(error)

      return response
        .status(500)
        .send({
          success: false,

          message:
            'Erro ao carregar os dados do Guardião Baseline.',

          error:
            process.env.NODE_ENV ===
            'development'
              ? mensagemErro
              : undefined,
        })
    }
  }
}