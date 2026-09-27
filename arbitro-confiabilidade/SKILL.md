---
name: arbitro-confiabilidade
description: >
  Consolida o relatório de validação de aderência e o relatório de revisão jurídica
  em um PARECER FINAL com score de confiabilidade 0-100, veredito e top riscos.
  Use ao final do pipeline, quando existirem os dois relatórios (validação +
  revisão), ou quando o usuário pedir "qual a confiabilidade deste documento?",
  "o documento está pronto?", "dá para enviar?".
argument-hint: '[relatorio-validacao.json] [relatorio-revisao.json]'
---

# Árbitro de Confiabilidade

Sintetiza as evidências dos agentes anteriores em um juízo calibrado e
explicável sobre o documento. O score é **rastreável**: cada componente cita os
achados que o motivaram.

## Insumos
1. `relatorio-validacao.json` (validador-aderencia).
2. `relatorio-revisao.json` (revisor-juridico).
3. Documento original (para consultas pontuais, não para re-revisar).

## Rubrica (score 0-100)

| Dimensão | Peso | Como calcular |
|---|---|---|
| Aderência ao briefing | 40 | 40 × cobertura de requisitos essenciais; desejáveis somam até +5 de bônus |
| Ausência de conflitos | 30 | 30 − (18 × críticos + 6 × importantes); menor que zero zera a dimensão |
| Consistência interna | 15 | 15 − (6 × achados de referência/número + 3 × ambiguidades importantes) |
| Completude jurídica | 15 | 15 − (5 × cláusula essencial ausente + 2 × verificacoes_pendentes) |

Regras duras:
- Requisito essencial `CONTRARIADO` ou qualquer `VIOLACAO_RESTRICAO` → veredito
  máximo `NECESSITA_REVISAO`, independente do score.
- Score > 95 exige nota explícita `requer_revisao_humana: true` e é reduzido a 95
  até que um revisor humano aprove.
- Nunca emita 100.

## Vereditos
- `APROVADO` (≥ 85 e zero críticos) — pronto para revisão humana final.
- `APROVADO_COM_RESSALVAS` (70-84, ou ≥85 com pendências `[VERIFICAR]`).
- `NECESSITA_REVISAO` (50-69) — devolver ao gerador com os achados priorizados.
- `REJEITADO` (< 50, ou violação de restrição) — recomeçar do briefing.

## Processo
1. Confira a coerência entre relatórios: se o validador devolveu
   (`DEVOLVIDO_AO_GERADOR`), o veredito não pode ser APROVADO — sinalize a
   contradição em vez de calcular normalmente.
2. Aplique a rubrica dimensão a dimensão, citando os ids dos achados usados.
3. Monte o `top_riscos` (máx. 5): os itens que, se não corrigidos, mais reduzem
   a confiabilidade — em linguagem direta.
4. Declare o que NÃO foi avaliado (ex.: veracidade de fatos, vigência de leis
   citadas, capacidade das partes) — a transparência do escopo faz parte do parecer.

## Saída (contrato)
JSON conforme `references/parecer-confiabilidade.schema.json` (na pasta desta skill) + bloco humano:
score, veredito, tabela por dimensão, top riscos, pendências para o humano e o
DISCLAIMER obrigatório: "Parecer automatizado. Não substitui análise de
advogado habilitado."

## Guardrails
- Seja conservador: entre duas notas plausíveis, atribua a menor.
- Não ignore achados para "fechar o score": se um achado não couber na rubrica,
  liste-o em `observacoes` e justifique o impacto dado ou não dado.
