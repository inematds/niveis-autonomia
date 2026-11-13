# A escada de autonomia: AL1 a AL5

Autonomia não se dá de graça: se conquista, um degrau de cada vez. O degrau é de **uma tarefa**, não da IA inteira. A mesma IA pode estar no AL5 em "traduzir legendas" e no AL2 em "responder cliente".

É a mesma escada do kit [nivel-ia](https://inematds.github.io/nivel-ia/guia/) e do [relogio-2027](https://inematds.github.io/relogio-2027/guia/). O nivel-ia mede **em que degrau está o seu trabalho** (horas por tarefa). Este kit mede **quanta liberdade você deu à IA**: o degrau de cada sessão, o modo de permissão, o que ela mexeu fora da máquina e todas as conexões que usou.

| Degrau | Nome | A IA faz | Você faz | Sinal que o medidor procura |
|---|---|---|---|---|
| **AL1** | Você faz sozinho | Nada. A IA não entra. | Tudo. | Não aparece no log: só na ficha de papel. |
| **AL2** | A IA ajuda | Responde, pesquisa, sugere. | Decide e executa. | Conversa com menos de 5 ações da IA por mensagem sua. |
| **AL3** | A IA colabora | Trabalha junto, passo a passo. | Conduz cada passo. | 5 a 14 ações da IA por mensagem sua. |
| **AL4** | A IA conduz, você revisa | Prepara tudo, inclusive o que sai para fora. | Confere antes de sair. | 15 ou mais ações por mensagem sua, ou pedido seu feito pelo bot (Telegram). |
| **AL5** | A IA roda sozinha | Roda o processo inteiro, com horário, regra e alarme. Tarefa crítica não chega aqui (para no AL4). | Define a regra, lê o resumo, atende a exceção. | Sessão aberta por script, bot ou timer (`claude -p`) com até 2 mensagens humanas. |

Na dúvida, três perguntas sobre a tarefa:
1. **A IA entrou?** Não → AL1.
2. **Quem fez o trabalho?** Você, com a resposta dela → AL2. Os dois, passo a passo → AL3. Ela, e você conferiu antes de sair → AL4.
3. **Você estava lá?** Não, rodou sozinha → AL5.

## AL5 tem gatilho de chamar humano?

**Tem, e precisa ter.** "Sozinha" não é "sem dono". No AL5 a IA roda com **horário, regra e alarme**, e o alarme é o gatilho que chama a pessoa: quando a tarefa sai da regra (erro, número fora do normal, caso que ela nunca viu, algo crítico), o sistema para e avisa você. Fora disso, você só lê o resumo. AL5 sem gatilho de chamar humano é o AL5 perigoso.

Por isso o relatório tem a seção **"AL5 que mexeu fora da máquina"**: sessões que rodaram sozinhas e publicaram, enviaram ou subiram algo. Para cada uma, confira três coisas: a regra está escrita, existe teto (quantidade, valor, tempo) e existe um alarme que chama você na exceção.

## Como subir de degrau

Uma tarefa por vez, **um degrau por vez**, e só quando o degrau atual ficou chato de tão certo. Quem decide é você. Anote na ficha, a cada vez, se precisou corrigir (`n` não · `p` pequena · `g` grande) e se houve erro grave (`s`/`n`). Só contam as vezes do degrau atual: quando você sobe ou desce, a conta daquela tarefa recomeça.

| Subir para | Critério (ponto de partida; ajuste ao risco da sua tarefa) |
|---|---|
| AL1 → AL2 | Sem critério: é só começar a perguntar. |
| AL2 → AL3 | No máximo 1 correção grande nas últimas 10 vezes. |
| AL3 → AL4 | No máximo 2 correções grandes em 20 vezes. |
| AL4 → AL5 | No máximo 2 correções grandes em 50 vezes, nenhum erro grave, e o gatilho de chamar humano funcionando. |

**Descer:** 1 erro grave ou 3 correções grandes nas últimas 10 vezes → volta um degrau naquela tarefa e anota o motivo. **Tarefa crítica** (publicar, cliente, pagamento, servidor, e-mail) para no AL4: a IA prepara, você confere antes de sair.

São os mesmos números do kit nivel-ia (`ESCADA.md`), para os dois kits darem a mesma resposta.

## Como medir

Dois jeitos, o mesmo resultado:

1. **No papel** (`kit/ficha-papel.html`): para cada tarefa, uma linha com data, tarefa, degrau (AL1 a AL5), conexão usada, corrigi? e erro grave?. Serve para começar hoje, sem instalar nada, para quem não usa Claude Code e para o que você faz sem IA (AL1).
2. **Automático** (`medir/autonomia.py`): lê os logs das suas sessões, põe cada uma num degrau (AL2 a AL5), junta tudo por semana, lista as conexões usadas e as sessões AL5 que mexeram fora da máquina. Roda sozinho todo dia por um timer.

## O que a medição automática não vê

- AL1: o que você faz sem IA não deixa log. Só a ficha conta.
- Se você aprovou no prompt: só vê o modo de permissão da sessão.
- Chamada de API feita de dentro de um script Python: aparece como `bash:python3`, sem o nome do serviço.
- Outras ferramentas além do Claude Code (Codex etc.): não lê. O nivel-ia lê o Codex.
- Se existe o alarme: o medidor mostra **onde** o gatilho de chamar humano precisa existir; se ele existe, só você confere.
- Qualidade: o degrau diz **quanta liberdade** a IA teve, não se acertou. Acerto é a coluna "corrigi?" da ficha.
