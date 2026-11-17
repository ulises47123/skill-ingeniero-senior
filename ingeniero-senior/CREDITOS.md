# Créditos y licencias

Esta skill es original en su estructura, reglas y textos en español, e incorpora material **traducido y adaptado** de dos proyectos de código abierto. Las licencias completas están en `licencias/`.

## obra/superpowers

- Repositorio: https://github.com/obra/superpowers (commit `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`)
- Autor: Jesse Vincent
- Licencia: MIT (`licencias/superpowers-MIT.txt`)
- Material usado:
  - `skills/systematic-debugging` (incluye `root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md`) → `depuracion/GUIA.md`
  - `skills/verification-before-completion` y `skills/test-driven-development` → `verificacion/GUIA.md`
  - `skills/writing-plans` y `skills/brainstorming` → `planes/GUIA.md`
- Cambios: traducción al español, fusión de varias skills en guías por tema, ajuste de la regla de intentos fallidos (2 para replantear, 3 para cuestionar la arquitectura), eliminación de referencias a otras skills de superpowers y adaptación de la plantilla de plan.

## anthropics/skills

- Repositorio: https://github.com/anthropics/skills (commit `ca45fc496a3436251f191354091d557da31c15b5`)
- Autor: Anthropic
- Licencia: Apache 2.0 (`licencias/anthropic-skills-Apache-2.0.txt`)
- Material usado:
  - `skills/frontend-design` → secciones 2, 6, 8, 10, 11 y 14 de `diseno/GUIA.md`
  - `skills/webapp-testing` → sección 6 de `verificacion/GUIA.md`
- Cambios: traducción al español, integración con un sistema de tokens, accesibilidad, estados de interacción, GUI de escritorio y checklist propios, y reescritura de los ejemplos de Playwright.

## Material propio

`SKILL.md`, `anti-estatico/` (guía y `detectar_estatico.py`), `python/GUIA.md`, `diseno/plantilla-tokens.css` y el resto de `diseno/GUIA.md` son contenido original de esta skill.
