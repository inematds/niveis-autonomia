#!/usr/bin/env python3
"""niveis-autonomia: mede, nos logs das sessões de IA, quanto do trabalho é
manual e quanto roda sozinho (níveis 0 a 4) e registra todas as conexões usadas.

Só lê arquivos locais (~/.claude/projects/**/*.jsonl). Não chama API, não envia nada.
O registro fica em registro/ (fora do git): contagens e uma etiqueta curta da tarefa.

Uso:
  autonomia.py varrer   [--desde AAAA-MM-DD] [--raiz DIR] [--registro DIR]
  autonomia.py relatorio [--desde AAAA-MM-DD] [--registro DIR] [--json]
  autonomia.py conexoes  [--registro DIR]
  autonomia.py inventario [--registro DIR]   (o que está configurado x o que foi usado; só nomes)
"""
import argparse, glob, json, os, re, sys, time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

HOME = os.path.expanduser("~")
RAIZ_PADRAO = os.path.join(HOME, ".claude", "projects")
REG_PADRAO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "registro")

NIVEIS = {
    0: "Consulta",
    1: "Sugere",
    2: "Faz com aprovação",
    3: "Faz e avisa",
    4: "Gerencia o processo",
}

# limites das regras (mude aqui, e só aqui, para calibrar)
LIM = {
    "n4_min_acoes": 15,      # ações que mudam algo para contar como processo inteiro
    "n4_max_humano": 1,      # mensagens humanas no máximo
    "n3_razao": 3.0,         # ações por mensagem humana acima disso = faz e avisa
    "headless_n3_min": 1,    # sessão sem humano que agiu pelo menos isso = N3 (N4 se passar de n4_min_acoes)
}

LEITURA = {"Read", "Grep", "Glob", "WebSearch", "WebFetch", "ToolSearch", "TaskList",
           "TaskGet", "TaskOutput", "ListMcpResourcesTool", "ReadMcpResourceTool", "BashOutput"}
ESCRITA = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
DELEGA = {"Agent", "Task"}
LEITURA_SUFIXO = re.compile(r"(^|_)(get|list|read|search|show|query|status|view|fetch|describe|whoami|stats|doctor|find|check|preview)", re.I)

BASH_LEITURA = {"ls", "cat", "head", "tail", "grep", "rg", "find", "wc", "echo", "pwd", "stat",
                "du", "df", "jq", "sort", "uniq", "cut", "tr", "file", "which", "date", "env",
                "printf", "test", "[", "type", "ps", "recall", "projeto", "memoria", "diff", "tree"}
BASH_GIT_LEITURA = {"status", "log", "diff", "show", "branch", "remote", "rev-parse", "ls-files", "grep", "config"}
EXTERNO = re.compile(
    r"(git\s+push|gh\s+(pr|issue|release|repo)\s+(create|merge|close|edit|delete)|gh\s+api\s+.*-X\s*(POST|PUT|PATCH|DELETE)|"
    r"curl\s+[^|;]*(-X\s*(POST|PUT|PATCH|DELETE)|\s-d\s|--data|-F\s)|yt-pubx\s+publicar|fila_es\.py\s+--add|"
    r"scp\s|rsync\s.*:|ssh\s|systemctl\s+(--user\s+)?(start|stop|restart|enable|disable)|rm\s+-r|"
    r"sendMessage|send_message|SEND_FILE|wrangler\s+(deploy|publish)|npm\s+publish|docker\s+push)", re.I)


RUIDO_BASH = BASH_LEITURA | {"for", "do", "done", "if", "then", "fi", "while", "cd", "sed", "awk", "xargs",
                             "timeout", "bash", "sh", "until", "sleep", "pgrep", "kill", "nohup", "set", "export", "source", "mkdir", "cp", "mv", "touch", "chmod"}


def classe_bash(cmd):
    """-> 'leitura' | 'escrita' | 'externo'"""
    if EXTERNO.search(cmd):
        return "externo"
    partes = re.split(r"\s*(?:&&|\|\||;|\|)\s*", cmd.strip())
    ok = True
    for p in partes:
        p = re.sub(r"^\(+|\)+$", "", p.strip())
        p = re.sub(r"^(cd\s+\S+)$", "pwd", p)
        toks = p.split()
        if not toks:
            continue
        while toks and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]):
            toks = toks[1:]
        if not toks:
            continue
        cab = os.path.basename(toks[0])
        if cab == "git":
            sub = next((t for t in toks[1:] if not t.startswith("-")), "")
            if sub not in BASH_GIT_LEITURA:
                ok = False
        elif cab not in BASH_LEITURA:
            ok = False
        if ">" in p and cab not in ("", ):
            if re.search(r"(^|[^2&\d])>{1,2}\s*[^&\s]", p) and "/dev/null" not in p:
                ok = False
    return "leitura" if ok else "escrita"


def cabeca_bash(cmd):
    p = re.split(r"\s*(?:&&|\|\||;|\|)\s*", cmd.strip())[-1 if cmd.strip().startswith("cd ") else 0]
    toks = [t for t in re.sub(r"^\(+", "", p).split() if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t)]
    if not toks:
        return None
    cab = os.path.basename(toks[0])
    if cab == "git" and len(toks) > 1:
        return "git"
    return cab[:40]


MARCA_TG = "[Mensagem do usuário via telegram]"


def texto_humano(msg):
    c = msg.get("content")
    if isinstance(c, str):
        t = c
    elif isinstance(c, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
            return None
        t = " ".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    else:
        return None
    t = t.strip()
    if not t or t.startswith(("<local-command", "<command-", "Caveat:", "<system-reminder", "[Request interrupted")):
        return None
    return t


def assinatura(texto):
    t = re.sub(r"https?://\S+", "URL", texto.lower())
    t = re.sub(r"[0-9]+", "N", t)
    t = re.sub(r"[^a-zà-ú ]", " ", t)
    pal = [w for w in t.split() if len(w) > 2][:6]
    return " ".join(pal)


def nivel_da_sessao(humano, leitura, escrita, externo, headless, modo=None):
    """0 consulta · 1 sugere · 2 faz com aprovação · 3 faz e avisa · 4 gerencia o processo.
    modo = permissionMode do log: default/plan/acceptEdits = o programa pede aprovação;
    auto/bypassPermissions = não pede."""
    acoes = escrita + externo
    if leitura + acoes == 0:
        return 0
    if acoes == 0:
        return 1
    if humano <= LIM["n4_max_humano"] and acoes >= LIM["n4_min_acoes"] and externo >= 1:
        return 4
    if headless and humano <= LIM["n4_max_humano"]:
        return 4 if acoes >= LIM["n4_min_acoes"] else 3
    if not headless and modo in ("default", "plan", "acceptEdits"):
        return 2
    razao = acoes / max(humano, 1)
    return 3 if razao > LIM["n3_razao"] else 2


def analisar(caminho):
    """Lê uma sessão e devolve o resumo (ou None)."""
    sid = os.path.splitext(os.path.basename(caminho))[0]
    humano = leitura = escrita = externo = delega = 0
    ent = None
    cwd = None
    t0 = t1 = None
    conex = Counter()
    primeira = None
    modos = Counter()
    telegram = False
    try:
        with open(caminho, "r", errors="replace") as f:
            for linha in f:
                if '"type":"user"' not in linha and '"type":"assistant"' not in linha and '"entrypoint"' not in linha:
                    continue
                if '"permissionMode":"' in linha:
                    i = linha.find('"permissionMode":"') + 18
                    modos[linha[i:i + 30].split('"')[0]] += 1
                try:
                    d = json.loads(linha)
                except Exception:
                    continue
                if ent is None and d.get("entrypoint"):
                    ent = d["entrypoint"]
                if cwd is None and d.get("cwd"):
                    cwd = d["cwd"]
                ts = d.get("timestamp")
                if ts:
                    t0 = t0 or ts
                    t1 = ts
                tp = d.get("type")
                if tp == "user" and not d.get("isMeta") and not d.get("isSidechain"):
                    t = texto_humano(d.get("message", {}))
                    if t:
                        if MARCA_TG in t:
                            telegram = True
                            t = t.split(MARCA_TG, 1)[1].strip()
                        humano += 1
                        if primeira is None:
                            primeira = t
                elif tp == "assistant":
                    msg = d.get("message", {})
                    for b in msg.get("content", []) if isinstance(msg.get("content"), list) else []:
                        if not isinstance(b, dict) or b.get("type") != "tool_use":
                            continue
                        nome = b.get("name", "")
                        inp = b.get("input", {}) or {}
                        if nome == "Bash":
                            cmd = str(inp.get("command", ""))
                            c = classe_bash(cmd)
                            if c == "leitura": leitura += 1
                            elif c == "externo": externo += 1
                            else: escrita += 1
                            h = cabeca_bash(cmd)
                            if h and h not in RUIDO_BASH:
                                conex["bash:" + h] += 1
                            for m in re.findall(r"https?://([A-Za-z0-9.-]+)", cmd)[:3]:
                                conex["host:" + m.lower()] += 1
                        elif nome.startswith("mcp__"):
                            partes = nome.split("__")
                            srv = partes[1] if len(partes) > 1 else "?"
                            acao = partes[-1]
                            conex["mcp:" + srv] += 1
                            if LEITURA_SUFIXO.search(acao): leitura += 1
                            else: externo += 1
                        elif nome in ESCRITA:
                            escrita += 1
                        elif nome in DELEGA:
                            delega += 1
                            conex["agente:" + str(inp.get("subagent_type", "geral"))[:30]] += 1
                        elif nome == "Skill":
                            conex["skill:" + str(inp.get("skill", "?"))[:40]] += 1
                            leitura += 1
                        elif nome in LEITURA:
                            leitura += 1
                            if nome in ("WebSearch", "WebFetch"):
                                conex["web:" + nome] += 1
                                u = str(inp.get("url", ""))
                                m = re.match(r"https?://([A-Za-z0-9.-]+)", u)
                                if m:
                                    conex["host:" + m.group(1).lower()] += 1
                        else:
                            escrita += 1
    except OSError:
        return None
    if humano == 0 and leitura + escrita + externo == 0:
        return None
    pessoa = (ent or "") in ("cli", "") or telegram
    headless = not pessoa
    # modo mais restrito visto na sessão (se algum momento pediu aprovação, conta)
    ordem = ["default", "plan", "acceptEdits", "auto", "bypassPermissions"]
    modo = next((m for m in ordem if m in modos), None)
    nv = nivel_da_sessao(humano, leitura, escrita, externo, headless, modo)
    return {
        "sid": sid, "tam": os.path.getsize(caminho), "ini": t0, "fim": t1,
        "projeto": os.path.basename(cwd) if cwd else None, "entrada": ent or "?",
        "pessoa": pessoa, "modo": modo, "humano": humano, "leitura": leitura, "escrita": escrita, "externo": externo,
        "delega": delega, "nivel": nv, "etiqueta": assinatura(primeira or ""),
        "conexoes": dict(conex), "fonte": "claude",
    }


def listar(raiz, desde):
    lim = time.mktime(time.strptime(desde, "%Y-%m-%d")) if desde else 0
    out = []
    for p in glob.glob(os.path.join(raiz, "*", "*.jsonl")):
        try:
            if os.path.getmtime(p) >= lim:
                out.append(p)
        except OSError:
            pass
    return sorted(out)


def carregar(reg):
    arq = os.path.join(reg, "sessoes.jsonl")
    d = {}
    if os.path.exists(arq):
        with open(arq) as f:
            for l in f:
                try:
                    r = json.loads(l)
                    d[r["sid"]] = r
                except Exception:
                    pass
    return d


def cmd_varrer(a):
    os.makedirs(a.registro, exist_ok=True)
    antigos = carregar(a.registro)
    todos = listar(a.raiz, a.desde)
    novos = [p for p in todos
             if os.path.splitext(os.path.basename(p))[0] not in antigos
             or antigos[os.path.splitext(os.path.basename(p))[0]]["tam"] != os.path.getsize(p)]
    t = time.time()
    with ProcessPoolExecutor(max_workers=a.jobs) as ex:
        for r in ex.map(analisar, novos, chunksize=8):
            if r:
                antigos[r["sid"]] = r
    arq = os.path.join(a.registro, "sessoes.jsonl")
    tmp = arq + ".tmp"
    with open(tmp, "w") as f:
        for r in sorted(antigos.values(), key=lambda x: x.get("ini") or ""):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, arq)
    print(f"varridos {len(novos)} de {len(todos)} arquivos em {time.time()-t:.0f}s; registro tem {len(antigos)} sessões")


def semana(iso):
    try:
        return time.strftime("%G-S%V", time.strptime(iso[:10], "%Y-%m-%d"))
    except Exception:
        return "?"


def dominante(r):
    """conexão que mais pesa na sessão (ignora host e web), para agrupar tarefas repetidas"""
    cs = [(v, k) for k, v in r["conexoes"].items() if not k.startswith(("host:", "web:"))]
    return max(cs)[1] if cs else "sem conexão"


def bloco(sess):
    n = len(sess)
    por_nivel = Counter(r["nivel"] for r in sess)
    acoes_nivel = defaultdict(int)
    for r in sess:
        acoes_nivel[r["nivel"]] += r["escrita"] + r["externo"]
    tot = sum(acoes_nivel.values()) or 1
    por_sem = defaultdict(Counter)
    for r in sess:
        por_sem[semana(r.get("ini") or "")][r["nivel"]] += 1
    grupos = defaultdict(lambda: {"n": 0, "nivel_soma": 0, "acoes": 0})
    for r in sess:
        if r["escrita"] + r["externo"] > 0:
            g = grupos[(r.get("projeto") or "?", dominante(r))]
            g["n"] += 1; g["nivel_soma"] += r["nivel"]; g["acoes"] += r["escrita"] + r["externo"]
    rep = sorted(({"projeto": k[0], "conexao": k[1], "vezes": v["n"], "nivel_medio": round(v["nivel_soma"] / v["n"], 1),
                   "acoes": v["acoes"]} for k, v in grupos.items() if v["n"] >= 3), key=lambda x: -x["vezes"])[:15]
    return {
        "sessoes": n,
        "por_nivel": {str(k): por_nivel.get(k, 0) for k in range(5)},
        "pct_sessoes": {str(k): round(100 * por_nivel.get(k, 0) / max(n, 1), 1) for k in range(5)},
        "pct_acoes": {str(k): round(100 * acoes_nivel.get(k, 0) / tot, 1) for k in range(5)},
        "semanas": {s: {str(k): c.get(k, 0) for k in range(5)} for s, c in sorted(por_sem.items())},
        "tarefas_repetidas": rep,
    }


def montar(reg, desde):
    sess = [r for r in carregar(reg).values() if not desde or (r.get("ini") or "")[:10] >= desde]
    com = [r for r in sess if r.get("pessoa", True)]
    sem = [r for r in sess if not r.get("pessoa", True)]
    conex = defaultdict(lambda: {"usos": 0, "sessoes": 0, "nivel_max": 0, "nivel_soma": 0, "sem_pessoa": 0})
    for r in sess:
        for k, v in r["conexoes"].items():
            c = conex[k]
            c["usos"] += v; c["sessoes"] += 1
            c["nivel_max"] = max(c["nivel_max"], r["nivel"]); c["nivel_soma"] += r["nivel"]
            if not r.get("pessoa", True): c["sem_pessoa"] += 1
    modos = Counter(r.get("modo") or "?" for r in com)
    por_proj = defaultdict(Counter)
    for r in sess:
        por_proj[r.get("projeto") or "?"][r["nivel"]] += 1
    return {
        "sessoes": len(sess),
        "com_pessoa": bloco(com),
        "sem_pessoa": bloco(sem),
        "modo_de_permissao_com_pessoa": dict(modos),
        "projetos_top": {p: dict(c) for p, c in sorted(por_proj.items(), key=lambda kv: -sum(kv[1].values()))[:10]},
        "conexoes": sorted(({"nome": k, **v} for k, v in conex.items()), key=lambda x: -x["usos"]),
    }


def tabela(b):
    print("| Nível | Sessões | % sessões | % das ações que mudam algo |\n|---|---|---|---|")
    for k in range(5):
        print(f"| {k} {NIVEIS[k]} | {b['por_nivel'][str(k)]} | {b['pct_sessoes'][str(k)]}% | {b['pct_acoes'][str(k)]}% |")


def cmd_relatorio(a):
    m = montar(a.registro, a.desde)
    if a.json:
        print(json.dumps(m, ensure_ascii=False, indent=2)); return
    print(f"# Níveis de autonomia: {m['sessoes']} sessões" + (f" desde {a.desde}" if a.desde else ""))
    for nome, chave in (("Com você na conversa (terminal ou Telegram)", "com_pessoa"), ("Sem ninguém na conversa (rotinas, timers, pipelines)", "sem_pessoa")):
        b = m[chave]
        print(f"\n## {nome}: {b['sessoes']} sessões\n")
        tabela(b)
        print("\nPor semana (sessões por nível 0/1/2/3/4):")
        for s, c in b["semanas"].items():
            print(f"- {s}: " + " / ".join(str(c[str(k)]) for k in range(5)))
    print("\n## Modo de permissão nas sessões com você\n" + ", ".join(f"{k}: {v}" for k, v in sorted(m["modo_de_permissao_com_pessoa"].items(), key=lambda kv: -kv[1])))
    print("\n## Tarefas que você ainda faz com a IA, repetidas 3+ vezes (projeto + conexão principal)")
    for c in m["com_pessoa"]["tarefas_repetidas"]:
        print(f"- {c['vezes']}x, nível médio {c['nivel_medio']}: {c['projeto']} via {c['conexao']}")
    print("\n## Tarefas que já rodam sem você, repetidas 3+ vezes")
    for c in m["sem_pessoa"]["tarefas_repetidas"]:
        print(f"- {c['vezes']}x, nível médio {c['nivel_medio']}: {c['projeto']} via {c['conexao']}")
    print("\n## Conexões mais usadas")
    for c in m["conexoes"][:20]:
        print(f"- {c['nome']}: {c['usos']} usos em {c['sessoes']} sessões ({c['sem_pessoa']} sem você), nível médio {c['nivel_soma']/c['sessoes']:.1f}, máximo {c['nivel_max']}")
    print("\nLimites: o nível vem de sinais do log (mensagens humanas, tipo de ação, modo de permissão, se rodou sem terminal). "
          "Só lê o Claude Code; Codex e chamadas de API feitas dentro de um script ficam fora.")


def cmd_conexoes(a):
    m = montar(a.registro, None)
    por_tipo = defaultdict(list)
    for c in m["conexoes"]:
        por_tipo[c["nome"].split(":")[0]].append(c)
    for tipo, lst in sorted(por_tipo.items()):
        print(f"\n## {tipo} ({len(lst)})")
        for c in lst[:30]:
            print(f"- {c['nome'].split(':',1)[1]}: {c['usos']} usos, nível máx {c['nivel_max']}")


def inventario_configurado():
    """Só NOMES do que está configurado nesta máquina. Nunca lê nem imprime valores (chaves, tokens, URLs)."""
    inv = {"mcp": set(), "skill": set(), "timer": set(), "hook": set()}
    for arq in (os.path.join(HOME, ".claude.json"), os.path.join(HOME, ".claude", "settings.json"), os.path.join(HOME, ".mcp.json")):
        try:
            d = json.load(open(arq))
        except Exception:
            continue
        inv["mcp"] |= set((d.get("mcpServers") or {}).keys())
        for ev in (d.get("hooks") or {}):
            inv["hook"].add(ev)
    for pasta in (os.path.join(HOME, ".claude", "skills"),):
        if os.path.isdir(pasta):
            inv["skill"] |= {n for n in os.listdir(pasta) if not n.startswith(".")}
    try:
        import subprocess
        out = subprocess.run(["systemctl", "--user", "list-timers", "--all", "--no-legend", "--no-pager"],
                             capture_output=True, text=True, timeout=15).stdout
        for l in out.splitlines():
            m = re.search(r"(\S+)\.timer", l)
            if m: inv["timer"].add(m.group(1))
    except Exception:
        pass
    return inv


def cmd_inventario(a):
    inv = inventario_configurado()
    usados = defaultdict(int)
    for c in montar(a.registro, None)["conexoes"]:
        tipo, nome = c["nome"].split(":", 1)
        usados[(tipo, nome)] += c["usos"]
    print("# Inventário: configurado x usado (só nomes)")
    for tipo, rot in (("mcp", "Servidores MCP"), ("skill", "Skills")):
        conf = inv[tipo]
        usou = {n for (t, n) in usados if t == tipo}
        if tipo == "mcp":
            usou_cfg = {n for n in conf if any(u == n or u.endswith(n) or n in u for u in usou)}
        else:
            usou_cfg = conf & usou
        print(f"\n## {rot}: {len(conf)} configurados, {len(usou_cfg)} com uso registrado")
        print("Sem nenhum uso registrado (candidatos a tirar ou a ensinar a usar): " + (", ".join(sorted(conf - usou_cfg)[:40]) or "nenhum"))
    print(f"\n## Timers do usuário: {len(inv['timer'])}\n" + ", ".join(sorted(inv["timer"])[:60]))
    print(f"\n## Eventos de hook configurados: {', '.join(sorted(inv['hook'])) or 'nenhum'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    for nome, fn in (("varrer", cmd_varrer), ("relatorio", cmd_relatorio), ("conexoes", cmd_conexoes), ("inventario", cmd_inventario)):
        p = sp.add_parser(nome)
        p.add_argument("--desde"); p.add_argument("--raiz", default=RAIZ_PADRAO)
        p.add_argument("--registro", default=os.path.abspath(REG_PADRAO))
        p.add_argument("--jobs", type=int, default=4); p.add_argument("--json", action="store_true")
        p.set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
