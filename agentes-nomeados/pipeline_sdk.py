"""Pipeline multiagente especialistas via orquestracao externa (SDK/HTTP TrueForge).
Padrao secao 5 do manifesto: 1 agente nomeado por estagio; SEU CODIGO encadeia.
Requisitos: pip install requests jsonschema | env: TF_BASE_URL, TF_API_KEY.
NOTA: ajuste os campos de resposta conforme sua versao da API (docs/api/use-agent).
"""
import os, json, time, requests

BASE, KEY = os.environ["TF_BASE_URL"].rstrip("/"), os.environ["TF_API_KEY"]
H = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
MAX_RODADAS = 3

def ensure_agents():
    for estagio in ["legal-gerador", "legal-validador", "legal-revisor", "legal-arbitro"]:
        spec = json.load(open(f"specs/{estagio.replace('legal-', '')}.json"))
        r = requests.post(f"{BASE}/api/v1/agents", headers=H, json={"manifest": spec})
        print(f"[agents] {estagio}: {r.status_code} (201=criado, 409=ja existe)")

def run_stage(agent_name, input_text, timeout=900, retries=2):
    """Abre sessao, roda 1 turno e devolve o output final do agente."""
    s = requests.post(f"{BASE}/api/v1/agent-sessions", headers=H, json={"agent": {"name": agent_name}}).json()
    sid = s.get("session_id") or s.get("id")
    last = None
    for attempt in range(retries + 1):          # retry com backoff — garantia dura que prompt nao da
        try:
            t = requests.post(f"{BASE}/api/v1/agent-sessions/{sid}/turns", headers=H,
                              json={"input": input_text, "stream": False}, timeout=timeout)
            t.raise_for_status()
            out = t.json()
            if out.get("state") == "error":
                raise RuntimeError(f"turn error: {out}")
            return out.get("output", out)       # <-- ajuste ao campo real da sua versao
        except Exception as e:
            last = e; time.sleep(5 * 2 ** attempt)
    raise RuntimeError(f"{agent_name} falhou apos {retries + 1} tentativas: {last}")

def extract(output, marker):
    """Extrai bloco JSON entre markers <<<JSON ... JSON>>> do output do agente."""
    try:
        return json.loads(output.split(f"<<<{marker}")[1].split(f"{marker}>>>")[0])
    except Exception:
        return None

def pipeline(contexto: dict):
    entrada = f"<<<CONTEXTO{json.dumps(contexto, ensure_ascii=False)}CONTEXTO>>>"
    doc, valid = None, None
    for rodada in range(1, MAX_RODADAS + 1):    # loop A1<->A2 com garantia de parada
        print(f"[pipeline] A1 gerador (rodada {rodada})")
        out1 = run_stage("legal-gerador", entrada if doc is None else f"{entrada}\nCORRECOES:\n{valid['correcoes']}")
        doc = extract(out1, "DOCUMENTO") or out1
        print("[pipeline] A2 validador")
        out2 = run_stage("legal-validador", f"{entrada}\n<<<DOCUMENTO{json.dumps(doc, ensure_ascii=False) if not isinstance(doc, str) else doc}DOCUMENTO>>>")
        valid = extract(out2, "RELATORIO")
        if valid and valid.get("decisao", {}).get("veredito") == "APROVADO_PARA_REVISAO":
            break
    print("[pipeline] A3 revisor")
    out3 = run_stage("legal-revisor", f"<<<DOCUMENTO{doc}DOCUMENTO>>>")
    revisao = extract(out3, "RELATORIO")
    print("[pipeline] A4 arbitro")
    out4 = run_stage("legal-arbitro", f"<<<VALIDACAO{json.dumps(valid)}VALIDACAO>>>\n<<<REVISAO{json.dumps(revisao)}REVISAO>>>")
    return {"documento": doc, "validacao": valid, "revisao": revisao, "parecer": out4}

if __name__ == "__main__":
    ensure_agents()
    contexto = json.load(open("contexto-exemplo.json"))
    resultado = pipeline(contexto)
    json.dump(resultado, open("resultado.json", "w"), ensure_ascii=False, indent=2)
    print("[pipeline] OK -> resultado.json")
