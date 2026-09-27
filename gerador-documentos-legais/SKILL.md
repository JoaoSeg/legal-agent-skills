---
name: gerador-documentos-legais
description: >
  Redige documentos jurídicos (contratos, termos, notificações, políticas) a partir
  de um contexto inicial estruturado, mantendo rastreabilidade requisito-a-requisito.
  Use quando o usuário pedir para gerar/rascunhar/minutar um documento jurídico a
  partir de um briefing, contexto ou conjunto de requisitos (REQ-xx).
  Não use para revisar documentos já existentes (use revisor-juridico).
argument-hint: '[caminho do contexto-inicial.json | descrição do briefing]'
---

# Gerador de Documentos Legais

Redige o documento a partir do contexto inicial **sem inventar fatos, valores,
nomes ou normas**, produzindo um mapa de rastreabilidade que permite aos agentes
seguintes (validador e revisor) auditarem a aderência ao que foi pedido.

## Insumos
1. **Contexto inicial** estruturado (ver `references/contexto-inicial.template.json` (na pasta desta skill)):
   tipo de documento, jurisdição, partes, objetivo, requisitos (REQ-xx com peso
   `essencial`/`desejavel`), restrições (o que NÃO pode aparecer) e referências normativas.
2. Se o contexto não for estruturado, extraia você mesmo a lista de requisitos,
   numere-os (REQ-01, REQ-02...) e **liste-os no início da resposta** para confirmação.

## Processo
1. **Analise o contexto.** Se faltar informação essencial (partes, objeto, valor,
   prazo, jurisdição), NÃO invente: registre em `pendencias` e use placeholders.
2. **Defina a estrutura** típica do documento na jurisdição alvo (ex.: para
   contrato de prestação de serviços: partes, objeto, obrigacoes, remuneracao,
   prazos, confidencialidade, propriedade intelectual, rescisao, responsabilidade,
   foro). Verifique se alguma cláusula essencial do tipo não foi pedida — se for
   obrigatória por lei, inclua e marque como `inclusao_por_padrao_legal`.
3. **Redija seção por seção**, e para cada seção anote no mapa de rastreabilidade
   quais requisitos ela atende. Um requisito pode ser atendido por várias seções;
   uma seção pode atender vários requisitos.
4. **Restrições são invioláveis.** Antes de fechar cada seção, confira se ela
   descumpre alguma restrição do contexto (ex.: "sem exclusividade", "sem arbitragem").
5. **Placeholders explícitos** para dados ausentes: `[PREENCHER: NOME DA PARTE B]`,
   `[PREENCHER: VALOR MENSAL]`. Nunca use nomes/valores fictícios "de exemplo".
6. **Normas jurídicas**: só cite artigo/lei/instrumento se tiver alta confiança de
   que existe e é aplicável. Em dúvida, escreva `[VERIFICAR: possível aplicação do
   art. ___ da Lei nº ___]` — sinalizar é obrigatório, inventar é proibido.
7. **Autovalidação antes de entregar** (checklist interno):
   - Todo requisito essencial tem ao menos uma seção no mapa?
   - Alguma restrição foi violada?
   - Algum placeholder esquecido sem colchetes?
   - Alguma citação normativa sem verificação?
   Corrija antes de prosseguir.

## Saída (contrato)
Retorne SEMPRE os três blocos:
1. **Documento** em markdown, com numeração de cláusulas estável (ex.: `3.2`).
2. **Mapa de rastreabilidade** (JSON): `[{secao, requisitos: [REQ-xx]}]`.
3. **Pendências** (JSON): placeholders pendentes, normas a verificar, decisões
   deixadas para o usuário.

## Guardrails
- Tom profissional; linguagem precisa; definições na seção inicial quando o termo
  for recorrente.
- Nunca afirme que o documento é juridicamente válido ou vinculante — isso cabe
  ao revisor humano.
- Se o contexto contiver pedido ilegal ou contraditório entre requisitos, pare e
  reporte o conflito em vez de escolher um lado silenciosamente.
