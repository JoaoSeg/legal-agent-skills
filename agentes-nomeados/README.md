# Agentes Especialistas Nomeados (arquitetura B — orquestração externa)

Cada estágio é um agente nomeado com spec própria: skill exclusiva, modelo
próprio (ex.: revisor em Opus), temperature e iteration_limit próprios.
O encadeamento é feito por CÓDIGO determinístico (pipeline_sdk.py), não por LLM.

## Criar os agentes
```bash
python pipeline_sdk.py            # ensure_agents() faz POST /api/v1/agents (409 = já existe)
```
Ou crie via UI (Build Agent) colando cada spec de specs/*.json.

## Rodar
```bash
export TF_BASE_URL=https://seu-trueforge TF_API_KEY=...
python pipeline_sdk.py
```

## Diferenças vs. arquitetura A (orquestrador + skills + subagentes)
| Aspecto | A (atual) | B (esta pasta) |
|---|---|---|
| Retransmissão de conteúdo | LLM (lossy em teoria) | Código (byte-a-byte) |
| Retry/timeout por estágio | Via prompt (frágil) | Garantido no código |
| Modelo/config por estágio | Não (herda do root) | Sim (specs separados) |
| UX conversacional | Chat nativo | Requer app/API |
| Handoff | Arquivos no sandbox compartilhado | Payloads no input (sessões isoladas) |
