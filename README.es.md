# Niveles de autonomía

[![Niveles de autonomía](guia/assets/banner-es.jpg)](https://inematds.github.io/niveis-autonomia/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

Kit para medir cuánta libertad le diste a la IA en cada tarea, en una escala de 0 (solo consulta) a 4 (gestiona todo el proceso). Sirve para quienes usan IA en el trabajo y quieren saber qué todavía hacen a mano y qué ya pueden delegar. Empiezas con una ficha en papel; quienes usan Claude Code activan un registro automático que lee las sesiones, clasifica cada una y anota todas las conexiones utilizadas. Necesitas Python 3 y, para el registro automático, el historial de Claude Code.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/niveis-autonomia/guia/es/**

## Los 5 niveles

| Nivel | Nombre | La IA hace | Tú haces |
|---|---|---|---|
| 0 | Consulta | Responde | Decide y ejecuta |
| 1 | Sugiere | Prepara un borrador o plan | Lo aplica |
| 2 | Actúa con aprobación | Ejecuta paso a paso | Aprueba cada paso |
| 3 | Actúa y avisa | Ejecuta por su cuenta y avisa | Revisa después |
| 4 | Gestiona el proceso | Lo ejecuta todo, solo te llama cuando hay una excepción | Define la regla y revisa el informe |

Detalles y criterios en [NIVEIS.md](NIVEIS.md) (en portugués).

## El proceso, de principio a fin

1. 🧠 **Entender los niveles** (10 min): lee [NIVEIS.md](NIVEIS.md) (en portugués) o la guía.
2. 🧠 **Imprimir la ficha**: `kit/ficha-papel.es.html`, A4 horizontal.
3. 🧠 **Anotar durante 5 días**: una línea por tarea (fecha, tarea, nivel, conexión, ¿corregí?).
4. 🧠 **Cerrar el viernes** (5 min): sigue la guía en [kit/ficha-papel.md](kit/ficha-papel.md) (en portugués).
5. ⚙️ **Revisar los registros**: `python3 medir/autonomia.py varrer --desde AAAA-MM-DD`.
6. ⚙️ **Ver el informe**: `python3 medir/autonomia.py relatorio`.
7. ⚙️ **Listar las conexiones**: `python3 medir/autonomia.py conexoes` e `inventario`.
8. ⚙️ **Dejarlo en ejecución**: `sh systemd/instalar.sh` (temporizador diario a las 06:10, guarda `registro/ultimo-relatorio.md`).
9. 🧠 **Subir de nivel una tarea**: elige la más repetida y segura; vuelve a medir la semana siguiente.
10. 🧠 **Bajar de nivel cuando haya errores**: si corriges más de 1 de cada 10 veces una tarea de nivel 3 o 4, bájala un nivel.

🧠 sesión con la persona · ⚙️ script o temporizador.

## Pruebas

```bash
python3 -I -m unittest discover -s tests
```

## Privacidad

Todo se ejecuta localmente, sin llamar a ninguna API. El registro queda en `registro/` (fuera de git). El inventario solo enumera nombres, nunca claves ni direcciones. El archivo `exemplo/` solo contiene cifras agregadas.

## Límites

No detecta si aprobaste en el prompt (solo el modo de permisos); las llamadas a API dentro de scripts aparecen como `bash:python3`; no lee Codex; el nivel mide la libertad, no si el resultado es correcto.

---
Parte de [INEMA.CLUB](https://inema.club). Contenido abierto y gratuito.