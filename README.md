# Níveis de autonomia

[![Níveis de autonomia](guia/assets/banner.jpg)](https://inematds.github.io/niveis-autonomia/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

Kit para medir quanta liberdade você deu à IA em cada tarefa, na escada **AL1 a AL5**: do AL1 (você faz sozinho) ao AL5 (a IA roda sozinha, com horário, regra e alarme). É a mesma escada do kit [nivel-ia](https://inematds.github.io/nivel-ia/guia/); este aqui olha a liberdade: modo de permissão, o que a IA mexeu fora da máquina e onde precisa existir o gatilho de chamar humano. Serve para quem usa IA no trabalho e quer saber o que ainda faz na mão e o que já pode entregar. Você começa com uma ficha de papel; quem usa o Claude Code liga um registro automático que lê as próprias sessões, classifica cada uma e anota toda conexão usada. Precisa de Python 3 e, para o registro automático, de histórico do Claude Code.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/niveis-autonomia/guia/**

🎬 Vídeo: https://www.youtube.com/watch?v=IBnQDJF2eXw

## A escada AL1 a AL5

| Degrau | Nome | A IA faz | Você faz |
|---|---|---|---|
| AL1 | Você faz sozinho | Nada | Tudo |
| AL2 | A IA ajuda | Responde e sugere | Decide e executa |
| AL3 | A IA colabora | Trabalha junto, passo a passo | Conduz cada passo |
| AL4 | A IA conduz, você revisa | Prepara tudo | Confere antes de sair |
| AL5 | A IA roda sozinha | Roda o processo com horário, regra e alarme | Lê o resumo e atende a exceção |

**AL5 tem gatilho de chamar humano?** Tem, e precisa ter: o alarme chama você quando a tarefa sai da regra. O relatório lista as sessões AL5 que mexeram fora da máquina (publicaram, enviaram, subiram) para você conferir se cada uma tem regra, teto e alarme.

Detalhe e critérios em [NIVEIS.md](NIVEIS.md).

## O processo, do início ao fim

1. 🧠 **Entender a escada** (10 min): leia [NIVEIS.md](NIVEIS.md) ou o guia.
2. 🧠 **Imprimir a ficha**: `kit/ficha-papel.html` (também `.en.html` e `.es.html`), A4 deitado.
3. 🧠 **Anotar por 5 dias**: uma linha por tarefa (data, tarefa, degrau AL1 a AL5, conexão, corrigi?, erro grave?).
4. 🧠 **Fechar a sexta (5 min)**: roteiro em [kit/ficha-papel.md](kit/ficha-papel.md).
5. ⚙️ **Varrer os registros**: `python3 medir/autonomia.py varrer --desde AAAA-MM-DD`.
6. ⚙️ **Ver o relatório**: `python3 medir/autonomia.py relatorio` (degraus por semana, tarefas repetidas, AL5 que mexeu fora da máquina).
7. ⚙️ **Listar as conexões**: `python3 medir/autonomia.py conexoes` e `inventario`.
8. ⚙️ **Deixar rodando**: `sh systemd/instalar.sh` (timer diário às 06:10, grava `registro/ultimo-relatorio.md`).
9. 🧠 **Conferir o gatilho de chamar humano**: cada linha de "AL5 que mexeu fora da máquina" precisa de regra, teto e alarme.
10. 🧠 **Subir uma tarefa um degrau**: a mais repetida e mais segura, pelo critério do [NIVEIS.md](NIVEIS.md); medir de novo na semana seguinte.
11. 🧠 **Descer quando errar**: 1 erro grave ou 3 correções grandes nas últimas 10 vezes → volta um degrau. Tarefa crítica para no AL4.

🧠 sessão com a pessoa · ⚙️ script ou timer.

## Testes

```bash
python3 -I -m unittest discover -s tests
```

## Privacidade

Tudo roda local, sem chamar API. O registro fica em `registro/` (fora do git). O inventário lista só nomes, nunca chaves nem endereços. O arquivo `exemplo/` traz só números agregados.

## Limites

Não vê se você aprovou no prompt (só o modo de permissão); chamadas de API dentro de scripts aparecem como `bash:python3`; não lê o Codex (o [nivel-ia](https://inematds.github.io/nivel-ia/guia/) lê); AL1 só existe na ficha; o degrau mede liberdade, não acerto.

---
Parte do [INEMA.CLUB](https://inema.club). Conteúdo aberto e gratuito.
