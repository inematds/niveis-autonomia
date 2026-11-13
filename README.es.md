# Niveles de autonomía

[![Niveles de autonomía](guia/assets/banner-es.jpg)](https://inematds.github.io/niveis-autonomia/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

Kit para medir cuánta libertad le diste a la IA en cada tarea, en la escala **AL1 a AL5**: desde AL1 (lo haces por tu cuenta) hasta AL5 (la IA funciona sola, con horario, reglas y alarma). Es la misma escala del kit [nivel-ia](https://inematds.github.io/nivel-ia/guia/); este kit se enfoca en la libertad: el modo de permisos, lo que la IA hizo fuera de la máquina y dónde debe existir el mecanismo para llamar a una persona. Sirve para quienes usan IA en el trabajo y quieren saber qué todavía hacen a mano y qué ya pueden delegar. Empiezas con una ficha de papel; quienes usan Claude Code pueden activar un registro automático que lee sus propias sesiones, clasifica cada una y anota todas las conexiones utilizadas. Necesitas Python 3 y, para el registro automático, el historial de Claude Code.

## 📖 Guía de uso

Guía completa (página de presentación + paso a paso): **https://inematds.github.io/niveis-autonomia/guia/es/**

## La escala AL1 a AL5

| Nivel | Nombre | La IA hace | Tú haces |
|---|---|---|---|
| AL1 | Lo haces por tu cuenta | Nada | Todo |
| AL2 | La IA ayuda | Responde y sugiere | Decide y ejecuta |
| AL3 | La IA colabora | Trabaja contigo, paso a paso | Guía cada paso |
| AL4 | La IA guía, tú revisas | Prepara todo | Revisa antes de que se realice |
| AL5 | La IA funciona sola | Ejecuta el proceso con horario, reglas y alarma | Lee el resumen y atiende las excepciones |

**¿AL5 tiene un mecanismo para llamar a una persona?** Sí, y debe tenerlo: la alarma te llama cuando la tarea se sale de las reglas. El informe enumera las sesiones AL5 que hicieron algo fuera de la máquina (publicaron, enviaron, subieron) para que revises si cada una tiene reglas, límites y alarma.

Detalles y criterios en [NIVEIS.md](NIVEIS.md).

## El proceso, de principio a fin

1. 🧠 **Entender la escala** (10 min): lee [NIVEIS.md](NIVEIS.md) o la guía.
2. 🧠 **Imprimir la ficha**: `kit/ficha-papel.html` (también `.en.html` y `.es.html`), A4 horizontal.
3. 🧠 **Anotar durante 5 días**: una línea por tarea (fecha, tarea, nivel AL1 a AL5, conexión, ¿corregí?, ¿error grave?).
4. 🧠 **Cerrar el viernes** (5 min): guía en [kit/ficha-papel.md](kit/ficha-papel.md).
5. ⚙️ **Recorrer los registros**: `python3 medir/autonomia.py varrer --desde AAAA-MM-DD`.
6. ⚙️ **Ver el informe**: `python3 medir/autonomia.py relatorio` (niveles por semana, tareas repetidas, sesiones AL5 que hicieron algo fuera de la máquina).
7. ⚙️ **Enumerar las conexiones**: `python3 medir/autonomia.py conexoes` e `inventario`.
8. ⚙️ **Dejarlo funcionando**: `sh systemd/instalar.sh` (temporizador diario a las 06:10, guarda `registro/ultimo-relatorio.md`).
9. 🧠 **Revisar el mecanismo para llamar a una persona**: cada línea de «AL5 que hizo algo fuera de la máquina» necesita reglas, límites y alarma.
10. 🧠 **Subir una tarea un nivel**: la más repetida y segura, según el criterio de [NIVEIS.md](NIVEIS.md); vuelve a medir la semana siguiente.
11. 🧠 **Bajar un nivel cuando haya errores**: 1 error grave o 3 correcciones importantes en las últimas 10 veces → baja un nivel. Las tareas críticas se quedan en AL4.

🧠 sesión con la persona · ⚙️ script o temporizador.

## Pruebas

```bash
python3 -I -m unittest discover -s tests
```

## Privacidad

Todo se ejecuta localmente, sin llamar a ninguna API. El registro queda en `registro/` (fuera de git). El inventario solo enumera nombres, nunca claves ni direcciones. El archivo `exemplo/` solo contiene números agregados.

## Límites

No detecta si aprobaste en el prompt (solo el modo de permisos); las llamadas a API dentro de scripts aparecen como `bash:python3`; no lee Codex (el [nivel-ia](https://inematds.github.io/nivel-ia/guia/) sí lo hace); AL1 solo existe en la ficha; el nivel mide libertad, no exactitud.

---
Parte de [INEMA.CLUB](https://inema.club). Contenido abierto y gratuito.