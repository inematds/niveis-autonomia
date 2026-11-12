# Autonomy Levels

[![Autonomy Levels](guia/assets/banner-en.jpg)](https://inematds.github.io/niveis-autonomia/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

A kit for measuring how much freedom you’ve given AI for each task, on a scale from 0 (queries only) to 4 (runs the entire process). It’s for people who use AI at work and want to know what they still do by hand and what they can already delegate. You start with a paper form. If you use Claude Code, you can enable automatic logging that reads your own sessions, classifies each one, and records every connection used. Requires Python 3 and, for automatic logging, Claude Code history.

## 📖 User guide

Complete guide (landing page + step-by-step instructions): **https://inematds.github.io/niveis-autonomia/guia/en/**

## The 5 levels

| Level | Name | The AI does | You do |
|---|---|---|---|
| 0 | Queries | Responds | Decides and executes |
| 1 | Suggests | Prepares a draft or plan | Applies it |
| 2 | Acts with approval | Executes step by step | Approves each step |
| 3 | Acts and tells | Executes on its own and tells you | Reviews afterward |
| 4 | Runs the process | Runs everything, calls you only when an exception occurs | Sets the rule and reviews the report |

Details and criteria in [NIVEIS.md](NIVEIS.md) (in Portuguese).

## The process, from start to finish

1. 🧠 **Understand the levels** (10 min): read [NIVEIS.md](NIVEIS.md) (in Portuguese) or the guide.
2. 🧠 **Print the form**: `kit/ficha-papel.html`, landscape A4.
3. 🧠 **Take notes for 5 days**: one line per task (date, task, level, connection, did I correct it?).
4. 🧠 **Wrap up on Friday** (5 min): instructions in [kit/ficha-papel.md](kit/ficha-papel.md) (in Portuguese).
5. ⚙️ **Scan the records**: `python3 medir/autonomia.py varrer --desde AAAA-MM-DD`.
6. ⚙️ **View the report**: `python3 medir/autonomia.py relatorio`.
7. ⚙️ **List the connections**: `python3 medir/autonomia.py conexoes` and `inventario`.
8. ⚙️ **Keep it running**: `sh systemd/instalar.sh` (daily timer at 06:10, writes `registro/ultimo-relatorio.md`).
9. 🧠 **Move a task up one level**: choose the most repeated and safest one; measure again the following week.
10. 🧠 **Move down a level after a mistake**: a task at level 3 or 4 that needed correction more than once in 10 times moves down one level.

🧠 session with the person · ⚙️ script or timer.

## Tests

```bash
python3 -I -m unittest discover -s tests
```

## Privacy

Everything runs locally, without calling an API. The log is stored in `registro/` (outside git). The inventory lists names only, never keys or addresses. The `exemplo/` file contains only aggregated numbers.

## Limits

It can’t see whether you approved in the prompt (only the permission mode); API calls inside scripts appear as `bash:python3`; it doesn’t read Codex; the level measures freedom, not correctness.

---
Part of [INEMA.CLUB](https://inema.club). Open and free content.