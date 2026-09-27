---
name: validador-aderencia
description: >
  Valida, requisito a requisito, se um documento jurídico em produção está seguindo
  o contexto inicial. Gera a matriz de rastreabilidade com status por requisito
  (ATENDIDO/PARCIAL/NAO_ATENDIDO/CONTRARIADO) e a lista objetiva de correções.
  Use após cada rodada de redação do gerador-documentos-legais, antes da revisão
  jurídica. Dispare quando o usuário pedir "validar aderência", "checar se o
  documento atende o briefing" ou no fluxo automatizado entre geração e revisão.
argument-hint: '[contexto-inicial.json] [documento.md ou mapa de rastreabilidade]'
---

# Validador de Aderência ao Contexto

Audita se o documento entregue pelo gerador cumpre o que foi pedido no contexto
inicial — nem a menos (requisito faltando), nem a mais (conteúdo que contraria
pedidos ou restrições).

## Insumos
1. **Contexto inicial** com requisitos REQ-xx (peso `essencial`/`desejavel`) e restrições.
2. **Documento** (markdown) e, se disponível, o **mapa de rastreabilidade** do gerador.

## Processo
1. **Extraia os requisitos** do contexto. Confirme contagem com o mapa do gerador
   se existir; se o gerador omitiu algum requisito do contexto, é falha imediata.
2. **Para cada requisito, busque evidência textual**: localize o trecho exato do
   documento que o atende e registre `citacao` + `clausula`. Evidência sem citação
   não conta como ATENDIDO.
3. **Classifique cada requisito**:
   - `ATENDIDO` — o documento cobre integralmente o pedido, com evidência.
   - `PARCIAL` — cobre parte; descreva exatamente o que falta.
   - `NAO_ATENDIDO` — sem evidência no documento.
   - `CONTRARIADO` — o documento contém disposição que anula ou contradiz o
     requisito. Cite o trecho conflitante. Este é o status mais grave.
4. **Verifique as restrições** (pedidos negativos): qualquer ocorrência vira achado
   `VIOLACAO_RESTRICAO` com severidade CRITICO.
5. **Checagens de sanidade do mapa**: seções do mapa que não existem no documento;
   requisitos alegados como atendidos sem seção correspondente.
6. **Calcule a cobertura**: `cobertura_essenciais = atendidos_essenciais / total_essenciais`
   e idem para desejáveis. Requisito essencial CONTRARIADO ou NAO_ATENDIDO
   **impede aprovação** em qualquer cenário.

## Critério de devolução ao gerador
Devolve para nova rodada de redação se:
- Algum requisito essencial não está ATENDIDO, **ou**
- Há qualquer VIOLACAO_RESTRICAO, **ou**
- Cobertura de desejáveis < 70%.
A devolução carrega a lista `correcoes_solicitadas` — instruções objetivas,
seção a seção, sem reescrita livre.

## Saída (contrato)
JSON conforme `references/relatorio-validacao.schema.json` (na pasta desta skill):
cobertura geral, tabela de requisitos (id, status, evidência, observação),
violações de restrição e correções solicitadas. Ao final, um veredito curto:
`APROVADO_PARA_REVISAO` ou `DEVOLVIDO_AO_GERADOR (rodada n)`.

## Guardrails
- Seja cético: em caso de dúvida entre PARCIAL e ATENDIDO, classifique PARCIAL.
- Não avalie qualidade jurídica nem redação — só aderência ao contexto
  (conflitos internos são papel do revisor-juridico).
- Nunca altere o documento; produza apenas o relatório.
