# Legal Agent Skills — Pipeline de Documentos Legais para TrueForge

4 skills no formato nativo do TrueForge (Agent Skills / `SKILL.md` git-backed):
um pipeline de geração, validação de aderência, revisão adversarial e parecer
de confiabilidade de documentos jurídicos.

```
gerador-documentos-legais/   A1 — redige o documento a partir do contexto inicial
validador-aderencia/         A2 — valida requisito a requisito (matriz de rastreabilidade)
revisor-juridico/            A3 — conflitos, inconsistências, redlines severificadas
arbitro-confiabilidade/      A4 — score 0-95 explicável + veredito
```

Cada pasta é uma skill autônoma (sparse-clonável): contém seu `SKILL.md` e os
schemas JSON de que precisa em `references/`.

## Integração no TrueForge

### 1. Publique o repositório
Faça push desta pasta para um repo GitHub/GitLab (ex.: `sua-org/legal-agent-skills`).
O TrueForge faz **sparse clone por subdiretório** — cada skill é clonada
individualmente, então a estrutura acima já está no formato correto.

### 2. Registre as skills (Settings → Skills)
Para cada uma das 4 pastas, registre uma skill:
- **URL**: `https://github.com/sua-org/legal-agent-skills`
- **Path**: `gerador-documentos-legais` (etc.)
- **Ref**: uma tag ou SHA de commit (fixe a versão em produção).

Alternativa para self-hosted: adicione entradas equivalentes em
`packages/trueforge/catalog/skill-catalog.yaml` para aparecerem como presets:

```yaml
  - type: git
    name: gerador-documentos-legais
    url: https://github.com/sua-org/legal-agent-skills
    path: gerador-documentos-legais
    ref: v1.0.0
    description: Redige documentos jurídicos a partir de um contexto inicial estruturado, com rastreabilidade REQ-xx.
```

> Nomes de skill: letras, números, `.`, `_`, `-` (máx. 64) — já compatíveis.
> Skills exigem **sandbox habilitado** no agente.

### 3. Crie o agente orquestrador (Build Agent ou API)
Um único agente com as 4 skills anexadas e subagentes dinâmicos. O corpo do
trabalho mora nas skills; as `instructions` só definem o protocolo do pipeline:

```json
{
  "model": { "name": "anthropic/claude-sonnet-4-6", "params": { "temperature": 0.2 } },
  "instructions": "Você orquestra o pipeline de documentos legais. Para cada solicitação: (1) monte/valide o contexto inicial com o usuário; (2) execute o protocolo A1→A2→A3→A4 usando create_sub_agent, um subagente por estágio, na ordem e com as regras das skills; (3) em caso de DEVOLVIDO_AO_GERADOR, repita A1→A2 (máx. 3 rodadas); (4) encerre sempre com o parecer do A4 e o documento final. Nunca pule o A2 ou o A3.",
  "skills": [
    { "name": "gerador-documentos-legais" },
    { "name": "validador-aderencia" },
    { "name": "revisor-juridico" },
    { "name": "arbitro-confiabilidade" }
  ],
  "config": {
    "sandbox": { "enabled": true },
    "ask_user_questions": { "enabled": true },
    "dynamic_sub_agents": { "enabled": true },
    "context_management": {
      "compaction": { "enabled": true, "trigger": { "type": "input_tokens", "value": 80000 } },
      "large_tool_response": { "enabled": true }
    },
    "iteration_limit": 50
  }
}
```

Por que funciona bem no TrueForge:
- **Subagentes dinâmicos** → cada estágio (A1-A4) roda em contexto isolado e
  devolve só o resultado; os relatórios JSON não poluem o contexto raiz.
- **Ask-user-questions** → o A1 usa isso quando faltam dados essenciais do briefing.
- **Compaction + large_tool_response** → documentos longos não estouram o contexto.
- **iteration_limit** → cota de segurança para o loop A1↔A2.

### 4. (Opcional) 4 agentes separados encadeados via SDK
Se quiser traces, aprovações e versionamento independentes por estágio, crie
um agente por papel (mesma receita: 1 skill + sandbox) e encadeie com o SDK
(`@truefoundry/trueforge-sdk`), passando os JSONs de saída de um como entrada
do próximo. Vantagem: auditoria por estágio; desvantagem: orquestração manual.

## Fluxo de mensagens (handoffs)

```
contexto-inicial.json ──► A1 ──► documento + mapa REQ-xx + pendências
                          ▲                        │
                          │ DEVOLVIDO + correções  ▼
                          └────────────────── A2 (relatorio-validacao.json)
                                                   │ APROVADO_PARA_REVISAO
                                                   ▼
                                    A3 (relatorio-revisao.json)
                                                   │
                                                   ▼
                                    A4 (parecer-confiabilidade.json)
```

## Disclaimer
Ferramenta de apoio à redação e triagem. Não substitui análise, assinatura e
responsabilidade de advogado habilitado.
