# Regras de Negócio — FUNDEB-VAAR & ICMS Educacional (Minas Gerais)

Este documento consolida as regras de cálculo implementadas no projeto "Uai Sô",
extraídas de `calculadora/formulas.py`, `calculadora/calc_vaar.py` e `utils/config.py`.
Serve como base de conhecimento para o chatbot responder perguntas conceituais
sobre como os indicadores e repasses são calculados.

## ICMS Educacional (Lei 24.431/2023, MG)

O ICMS Educacional é a parcela do ICMS estadual (10% do total, conforme a
Lei Robin Hood — Lei 18.030/2009 — e regulamentada pela Lei 24.431/2023)
distribuída aos municípios de Minas Gerais com base no desempenho educacional.

### Índice de Qualidade Educacional (IQE)

Calculado por município a partir de quatro subíndices, com pesos fixos definidos
no Anexo II da Lei 24.431/2023:

```
IQE(i) = IRAP(i) × 0,50 + IRE(i) × 0,20 + IAE(i) × 0,15 + IGE(i) × 0,15
```

Onde:
- **IRAP** — Índice de Desempenho Escolar (peso 50%)
- **IRE** — Índice de Rendimento Escolar (peso 20%)
- **IAE** — Índice de Atendimento Educacional (peso 15%)
- **IGE** — Índice de Gestão Escolar (peso 15%)

O IQE resulta em um valor no intervalo [0, 1].

### Índice de Educação do Município (IE)

Representa a participação proporcional do município no rateio do ICMS Educação:

```
IE(i) = IQE(i) / Σ IQE(i)
```

Onde Σ IQE(i) é a soma do IQE de todos os 853 municípios de MG.

### Valor do repasse ICMS Educação

```
Repasse_ICMS(i) = IE(i) × Total_ICMS_Educação_MG
```

O `Total_ICMS_Educação_MG` é o montante estadual anual destinado à educação
(10% do ICMS total do estado), atualizado ano a ano com base em dados da SEF-MG.

## VAAR — Complementação do FUNDEB (Lei 14.113/2020)

O VAAR (Valor Anual por Aluno Resultante) é uma complementação federal do FUNDEB
distribuída aos municípios que apresentarem melhoria em indicadores educacionais
E que atendam a condicionalidades legais.

### Coeficiente VAAR

```
CoefVAAR(i) = ΔIndicador_mun(i) / Σ ΔIndicador_rede
```

Onde `ΔIndicador_mun` é a melhoria do indicador educacional do município em
relação ao ano-base, e `Σ ΔIndicador_rede` é a soma dessas melhorias entre
todos os municípios **habilitados** do estado. Municípios não habilitados
recebem coeficiente 0.

### Valor do repasse VAAR

```
ValorVAAR(i) = CoefVAAR(i) × Total_VAAR_MG
```

### Condicionalidades para habilitação ao VAAR (Art. 14, §1º, Lei 14.113/2020)

Um município só participa do rateio do VAAR se atender simultaneamente a:

| Condicionalidade | Critério |
|---|---|
| I | Gestores escolares selecionados por mérito/desempenho |
| II | Participação ≥ 80% dos alunos no SAEB |
| III | Redução de desigualdades socioeconômicas e raciais |
| IV | Lei estadual de ICMS Educação vigente (≥ 10%) |
| V | Currículo alinhado à BNCC aprovado |

Se um município não atender a alguma condicionalidade, ou não apresentar
melhoria em nenhum indicador, ele é marcado como **inabilitado** e recebe
coeficiente VAAR igual a zero — o motivo padrão registrado é
"Não apresentou melhoria em nenhum dos indicadores" quando aplicável.

## Base legal (resumo)

- **EC 108/2020** — Emenda Constitucional que criou o novo FUNDEB permanente e
  fundamenta constitucionalmente a complementação VAAR e o ICMS Educacional.
- **Lei 14.113/2020** — Regulamenta o novo FUNDEB; o Art. 14 trata especificamente
  da complementação VAAR, suas condicionalidades e forma de cálculo.
- **Lei 18.030/2009 ("Lei Robin Hood")** — Lei mineira que distribui parte do
  ICMS aos municípios de MG com base em critérios sociais, ambientais e
  educacionais.
- **Lei 24.431/2023** — Lei mineira específica do ICMS Educacional; define a
  fórmula do IQE e do IE (Anexos II e III) e destina 10% do ICMS à educação.

> Observação: este resumo descreve como as leis foram interpretadas e
> implementadas no projeto Uai Sô. Para o texto oficial e integral das normas,
> consulte os portais oficiais (planalto.gov.br, almg.gov.br). Não é
> aconselhamento jurídico.
