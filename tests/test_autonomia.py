import json, os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "medir"))
import autonomia as A


def sessao(pasta, nome, eventos, ent="cli"):
    p = os.path.join(pasta, nome + ".jsonl")
    with open(p, "w") as f:
        for i, e in enumerate(eventos):
            e.setdefault("timestamp", "2026-11-10T10:%02d:00Z" % i)
            e.setdefault("entrypoint", ent); e.setdefault("cwd", "/x/proj")
            f.write(json.dumps(e, separators=(",", ":")) + "\n")
    return p


def u(t): return {"type": "user", "message": {"content": t}}
def a(*tools): return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": n, "input": i} for n, i in tools]}}
def res(): return {"type": "user", "message": {"content": [{"type": "tool_result", "content": "ok"}]}}


class T(unittest.TestCase):
    def setUp(self): self.d = tempfile.mkdtemp()

    def test_al2_pergunta_solta(self):
        r = A.analisar(sessao(self.d, "s0", [u("oi"), {"type": "assistant", "message": {"content": [{"type": "text", "text": "x"}]}}]))
        self.assertEqual(r["nivel"], "AL2")

    def test_al2_poucas_acoes_por_mensagem(self):
        ev = [u("a"), a(("Read", {}), ("Grep", {})), res(), u("b"), a(("Edit", {})), res()]
        self.assertEqual(A.analisar(sessao(self.d, "s1", ev))["nivel"], "AL2")

    def test_al3_cinco_a_catorze_por_mensagem(self):
        ev = [u("faça")] + [x for _ in range(6) for x in (a(("Write", {})), res())]
        self.assertEqual(A.analisar(sessao(self.d, "s3", ev))["nivel"], "AL3")

    def test_al4_quinze_ou_mais_por_mensagem(self):
        ev = [u("rode tudo")] + [x for _ in range(16) for x in (a(("Edit", {})), res())] + [a(("Bash", {"command": "git push origin main"})), res()]
        r = A.analisar(sessao(self.d, "s4", ev))
        self.assertEqual(r["nivel"], "AL4"); self.assertEqual(r["externo"], 1)

    def test_al5_aberta_por_script(self):
        ev = [u("tarefa do timer"), a(("Write", {})), res()]
        self.assertEqual(A.analisar(sessao(self.d, "sh", ev, ent="sdk-cli"))["nivel"], "AL5")

    def test_script_com_3_mensagens_e_conversa(self):
        ev = [u("a"), a(("Write", {})), res(), u("b"), u("c"), a(("Write", {})), res()]
        self.assertEqual(A.analisar(sessao(self.d, "sc3", ev, ent="sdk-cli"))["nivel"], "AL2")

    def test_bot_e_al4(self):
        ev = [u("[Mensagem do usuário via telegram]\nfaz o relatorio"), a(("Write", {})), res()]
        self.assertEqual(A.analisar(sessao(self.d, "sbot", ev, ent="sdk-cli"))["nivel"], "AL4")

    def test_modo_fica_registrado(self):
        ev = [dict(u("faça"), permissionMode="default")] + [x for _ in range(8) for x in (a(("Write", {})), res())]
        r = A.analisar(sessao(self.d, "sm", ev))
        self.assertEqual(r["nivel"], "AL3"); self.assertEqual(r["modo"], "default")

    def test_mesma_regra_do_nivel_ia(self):
        for hum, ac, hl, bot, esp in ((1, 0, False, False, "AL2"), (2, 9, False, False, "AL2"), (2, 10, False, False, "AL3"),
                                      (1, 15, False, False, "AL4"), (2, 1, True, False, "AL5"), (0, 3, False, False, "AL5"),
                                      (5, 1, True, True, "AL4")):
            self.assertEqual(A.nivel_da_sessao(hum, ac, hl, bot), esp, (hum, ac, hl, bot))

    def test_telegram_em_sdk_conta_como_com_pessoa(self):
        ev = [u("[Mensagem do usuário via telegram]\nfaz o relatorio"), a(("Write", {})), res()]
        r = A.analisar(sessao(self.d, "st", ev, ent="sdk-cli"))
        self.assertTrue(r["pessoa"]); self.assertEqual(r["etiqueta"], "faz relatorio")

    def test_al5_fora_da_maquina(self):
        raiz = os.path.join(self.d, "r2", "proj"); os.makedirs(raiz)
        sessao(raiz, "p1", [u("publica"), a(("Bash", {"command": "git push"})), res()], ent="sdk-cli")
        reg = os.path.join(self.d, "reg2")
        class Ar: pass
        ar = Ar(); ar.registro = reg; ar.raiz = os.path.join(self.d, "r2"); ar.desde = None; ar.jobs = 1
        A.cmd_varrer(ar)
        m = A.montar(reg, None)
        self.assertEqual(m["al5_fora_da_maquina"][0]["vezes"], 1); self.assertEqual(m["al5_fora_da_maquina"][0]["efeitos"], 1)

    def test_pipeline_sem_pessoa(self):
        r = A.analisar(sessao(self.d, "sp", [u("você é revisor"), a(("Read", {})), res()], ent="sdk-cli"))
        self.assertFalse(r["pessoa"])

    def test_bash_classes(self):
        self.assertEqual(A.classe_bash("ls -la | head"), "leitura")
        self.assertEqual(A.classe_bash("cd /x && git status"), "leitura")
        self.assertEqual(A.classe_bash("echo oi > arq.txt"), "escrita")
        self.assertEqual(A.classe_bash("python3 run.py"), "escrita")
        self.assertEqual(A.classe_bash("curl -X POST https://a.b/x"), "externo")
        self.assertEqual(A.classe_bash("git push"), "externo")

    def test_conexoes_mcp_e_skill(self):
        ev = [u("x"), a(("mcp__metricool__getScheduledPosts", {}), ("mcp__metricool__createScheduledPost", {}), ("Skill", {"skill": "kling"})), res()]
        r = A.analisar(sessao(self.d, "sc", ev))
        self.assertEqual(r["conexoes"]["mcp:metricool"], 2); self.assertIn("skill:kling", r["conexoes"])
        self.assertEqual(r["externo"], 1)

    def test_varrer_incremental_e_relatorio(self):
        raiz = os.path.join(self.d, "raiz", "proj"); os.makedirs(raiz)
        sessao(raiz, "a1", [u("fazer relatorio semanal"), a(("Edit", {})), res()])
        reg = os.path.join(self.d, "reg")
        class Ar: pass
        ar = Ar(); ar.registro = reg; ar.raiz = os.path.join(self.d, "raiz"); ar.desde = None; ar.jobs = 1
        A.cmd_varrer(ar); A.cmd_varrer(ar)
        self.assertEqual(len(A.carregar(reg)), 1)
        m = A.montar(reg, None)
        self.assertEqual(m["sessoes"], 1); self.assertEqual(m["com_pessoa"]["por_nivel"]["AL2"], 1); self.assertEqual(m["sem_pessoa"]["sessoes"], 0)


if __name__ == "__main__":
    unittest.main()
