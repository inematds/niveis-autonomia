# Os 5 níveis de autonomia

Autonomia não se dá de graça: se conquista, um nível de cada vez. O nível é de **uma tarefa**, não da IA inteira. A mesma IA pode estar no nível 3 em "organizar arquivos" e no nível 1 em "mandar e-mail para cliente".

Os extremos (0 consulta, 4 gerencia o processo inteiro) vêm do vídeo "5 Níveis de Autonomia da IA que Quase Ninguém Usa" (INEMA TDS). Os níveis 1 a 3 foram escritos neste kit para ficarem medíveis. Se o seu roteiro original nomeia os do meio de outro jeito, troque os nomes aqui e em `medir/autonomia.py` (dicionário `NIVEIS`); a medição não muda.

| Nível | Nome | A IA faz | Você faz | Sinal que o medidor procura |
|---|---|---|---|---|
| 0 | Consulta | Responde. Não usa ferramenta. | Decide e executa tudo. | Nenhuma ferramenta usada. |
| 1 | Sugere | Pesquisa, lê, monta o rascunho ou o plano. Não altera nada. | Aplica a sugestão. | Só leitura, nenhuma alteração. |
| 2 | Faz com aprovação | Altera arquivos e roda comandos, mas cada passo passa por você. | Aprova cada passo (permissão do programa ou conversa passo a passo). | Alterou algo e o modo de permissão pede aprovação, ou há uma mensagem sua para poucas ações. |
| 3 | Faz e avisa | Executa sozinha dentro de limites e avisa ao terminar. | Revisa o resultado depois. | Muitas ações por mensagem sua, sem prompt de aprovação. |
| 4 | Gerencia o processo | Roda o processo inteiro, inclusive efeitos fora da máquina (publicar, enviar, subir). Só chama você na exceção. | Define a regra, olha o relatório, atende a exceção. | No máximo 1 mensagem humana, 15+ ações, ao menos 1 efeito externo; ou rotina sem terminal. |

## Como subir de nível

Suba uma tarefa por vez, e só quando o nível atual ficou chato de tão certo. O critério que usamos no curso da constituição de agentes é por **taxa de acerto e número de execuções**, por exemplo 90% em 50 execuções, 95% em 200, 98% em 500 (confira os números do seu caso, são ponto de partida). Errou feio? Desce um nível naquela tarefa e anota o motivo.

## Como medir

Dois jeitos, o mesmo resultado:

1. **No papel** (`kit/ficha-papel.html`): para cada tarefa que a IA fez, uma linha com data, tarefa, nível, conexão usada e se precisou corrigir. Serve para começar hoje, sem instalar nada, e para quem não usa Claude Code.
2. **Automático** (`medir/autonomia.py`): lê os logs das suas sessões, classifica cada uma em 0 a 4, junta tudo por semana e lista as conexões usadas. Roda sozinho todo dia por um timer.

Papel e programa usam as **mesmas colunas**, então a ficha de papel vira linha do registro quando você quiser.

## O que a medição automática não vê

- Se você aprovou no prompt: só vê o modo de permissão da sessão.
- Chamada de API feita de dentro de um script Python: aparece como `bash:python3`, sem o nome do serviço.
- Outras ferramentas além do Claude Code (Codex etc.): não lê.
- Qualidade: o nível diz **quanta liberdade** a IA teve, não se acertou. Acerto é a coluna "precisou corrigir?" da ficha.
