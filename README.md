# Níveis de autonomia

[![Níveis de autonomia](guia/assets/banner.jpg)](https://inematds.github.io/niveis-autonomia/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

Kit para medir quanta liberdade você deu à IA em cada tarefa, numa escala de 0 (só consulta) a 4 (gerencia o processo inteiro). Serve para quem usa IA no trabalho e quer saber o que ainda faz na mão e o que já pode entregar. Você começa com uma ficha de papel; quem usa o Claude Code liga um registro automático que lê as próprias sessões, classifica cada uma e anota toda conexão usada. Precisa de Python 3 e, para o registro automático, de histórico do Claude Code.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/niveis-autonomia/guia/**

## Os 5 níveis

| Nível | Nome | A IA faz | Você faz |
|---|---|---|---|
| 0 | Consulta | Responde | Decide e executa |
| 1 | Sugere | Monta rascunho ou plano | Aplica |
| 2 | Faz com aprovação | Executa, passo a passo | Aprova cada passo |
| 3 | Faz e avisa | Executa sozinha e avisa | Revisa depois |
| 4 | Gerencia o processo | Roda tudo, só chama na exceção | Define a regra e olha o relatório |

Detalhe e critérios em [NIVEIS.md](NIVEIS.md).

## O processo, do início ao fim

1. 🧠 **Entender os níveis** (10 min): leia [NIVEIS.md](NIVEIS.md) ou o guia.
2. 🧠 **Imprimir a ficha**: `kit/ficha-papel.html` (também `.en.html` e `.es.html`), A4 deitado.
3. 🧠 **Anotar por 5 dias**: uma linha por tarefa (data, tarefa, nível, conexão, corrigi?).
4. 🧠 **Fechar a sexta (5 min)**: roteiro em [kit/ficha-papel.md](kit/ficha-papel.md).
5. ⚙️ **Varrer os registros**: `python3 medir/autonomia.py varrer --desde AAAA-MM-DD`.
6. ⚙️ **Ver o relatório**: `python3 medir/autonomia.py relatorio`.
7. ⚙️ **Listar as conexões**: `python3 medir/autonomia.py conexoes` e `inventario`.
8. ⚙️ **Deixar rodando**: `sh systemd/instalar.sh` (timer diário às 06:10, grava `registro/ultimo-relatorio.md`).
9. 🧠 **Subir uma tarefa de nível**: a mais repetida e mais segura; medir de novo na semana seguinte.
10. 🧠 **Descer quando errar**: tarefa nos níveis 3 ou 4 corrigida mais de 1 vez em 10 volta um nível.

🧠 sessão com a pessoa · ⚙️ script ou timer.

## Testes

```bash
python3 -I -m unittest discover -s tests
```

## Privacidade

Tudo roda local, sem chamar API. O registro fica em `registro/` (fora do git). O inventário lista só nomes, nunca chaves nem endereços. O arquivo `exemplo/` traz só números agregados.

## Limites

Não vê se você aprovou no prompt (só o modo de permissão); chamadas de API dentro de scripts aparecem como `bash:python3`; não lê o Codex; o nível mede liberdade, não acerto.

---
Parte do [INEMA.CLUB](https://inema.club). Conteúdo aberto e gratuito.
