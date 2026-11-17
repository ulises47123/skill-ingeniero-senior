# Skill "Ingeniero Senior" (en español)

Skill para asistentes de IA (por ejemplo Claude Code) que impone una forma de trabajo de ingeniero de software senior: plan aprobado antes de tocar código, nada de partes estáticas o simuladas, depuración sistemática y verificación con evidencia antes de dar algo por terminado.

## Contenido

- `ingeniero-senior/SKILL.md`: punto de entrada de la skill y mapa de qué leer según la tarea.
- `planes/`, `depuracion/`, `verificacion/`, `diseno/`, `python/`, `anti-estatico/`: guías por tema.
- `anti-estatico/detectar_estatico.py`: script que detecta datos simulados o interfaces "de mentira".
- `CREDITOS.md` y `licencias/`: material traducido y adaptado de [obra/superpowers](https://github.com/obra/superpowers) (MIT) y [anthropics/skills](https://github.com/anthropics/skills) (Apache 2.0).

## Instalación (Claude Code)

Copiá la carpeta `ingeniero-senior/` a `~/.claude/skills/` (o a `.claude/skills/` dentro de un proyecto).
