# Guía de verificación antes de terminar

Lee esta guía **cada vez** que estés por decir que algo está terminado, arreglado o que "pasa", antes de hacer commit o abrir un PR, y antes de pasar a la siguiente tarea.

> Combina y adapta `verification-before-completion` y `test-driven-development` de [obra/superpowers](https://github.com/obra/superpowers) (MIT) y `webapp-testing` de [anthropics/skills](https://github.com/anthropics/skills) (Apache 2.0). Ver `CREDITOS.md`.

Contenido:

1. La ley de hierro
2. La puerta de verificación
3. Qué evidencia demuestra qué
4. Escalera de verificación
5. Tests: el ciclo rojo-verde
6. Verificar una web en el navegador real
7. Verificar trabajo delegado
8. Señales de alarma

---

## 1. La ley de hierro

```
NINGUNA AFIRMACIÓN DE ÉXITO SIN EVIDENCIA DE VERIFICACIÓN RECIENTE
```

Si no ejecutaste el comando de verificación **en este momento**, después del último cambio, no puedes afirmar que pasa. Una ejecución anterior no cuenta: el código cambió desde entonces. La confianza no es evidencia.

La regla aplica a cualquier forma de decirlo: "listo", "funciona", "arreglado", "¡perfecto!", "ya quedó", e incluso a insinuarlo.

---

## 2. La puerta de verificación

Antes de afirmar cualquier estado:

1. **Identifica** qué comando o prueba demuestra esa afirmación.
2. **Ejecútalo** completo y desde cero.
3. **Lee** la salida completa: código de salida, cantidad de fallos, advertencias.
4. **Comprueba** si la salida confirma lo que vas a afirmar.
   - Si **no**: informa el estado real con la evidencia.
   - Si **sí**: afirma el resultado **acompañado** de la evidencia.
5. Solo entonces, afírmalo.

Saltarse cualquier paso no es verificar: es suponer.

---

## 3. Qué evidencia demuestra qué

| Afirmación | Requiere | No alcanza |
|---|---|---|
| Los tests pasan | Salida del comando de tests con 0 fallos | Una ejecución anterior, "deberían pasar" |
| El linter está limpio | Salida del linter con 0 errores | Revisar a ojo, haber corrido solo una parte |
| El build funciona | Comando de build con código de salida 0 | Que el linter pase (no compila) |
| El bug está arreglado | Reproducir el síntoma original y ver que ya no ocurre | Haber cambiado el código |
| El test de regresión sirve | Ciclo rojo-verde comprobado (sección 5) | Que el test pase una vez |
| La pantalla funciona | La app ejecutándose y el flujo recorrido de verdad | Que compile y los tests unitarios pasen |
| Se cumplen los requisitos | Relectura del pedido/plan, punto por punto | Que los tests pasen |
| El subagente terminó | El diff real revisado y la verificación repetida | Su reporte de "éxito" |

---

## 4. Escalera de verificación

Ejecuta todo lo que aplique al proyecto, en este orden (los primeros son baratos y atrapan errores tontos rápido):

1. **Formato y linter:** `ruff check`, `eslint`, `npm run lint`...
2. **Tipos:** `tsc --noEmit`, `mypy`, `pyright`...
3. **Tests relacionados** con el cambio.
4. **Suite completa de tests.** "Los otros tests" significa la suite del proyecto, no solo tu archivo. Compara con la línea base tomada antes de empezar: no debe haber fallos nuevos. Cualquier fallo, incluso uno que no causaste, va en el reporte con su nombre.
5. **Build de producción:** `npm run build`, `python -m build`...
6. **Detector anti-estático:** `python <skill>/anti-estatico/detectar_estatico.py <rutas cambiadas>`.
7. **Ejecución real:** levanta la app o corre el programa y recorre el flujo cambiado, incluyendo al menos un caso de error y un caso límite. Revisa la consola y los logs.
8. **Regresión:** recorre también los flujos vecinos identificados en el análisis de impacto.
9. **Requisitos:** relee el pedido original (y el plan), y marca cada punto como cumplido o no.

Si no puedes ejecutar un paso (falta una credencial, una base de datos, un dispositivo), **dilo en el reporte** e indica exactamente qué debe comprobar el usuario y cómo.

---

## 5. Tests: el ciclo rojo-verde

Para lógica nueva y para cada bug, prefiere escribir el test primero:

1. **Rojo:** escribe un test mínimo que describa **un** comportamiento, con nombre claro y código real (sin mocks salvo que sea inevitable).
2. **Comprueba que falla, y por el motivo correcto** (falta la funcionalidad, no un error de tipeo). Si pasa de entrada, estás probando algo que ya existía: corrige el test.
3. **Verde:** escribe el código **mínimo** para que pase. Nada de opciones ni configuraciones "por si acaso".
4. **Comprueba que pasa**, y que el resto de la suite sigue pasando, sin errores ni advertencias nuevas en la salida.
5. **Refactoriza** si hace falta (nombres, duplicación), manteniendo todo en verde.

Si nunca viste fallar el test, no sabes si prueba lo correcto. Para un test de regresión de un bug: escribe el test → pasa con el arreglo → revierte temporalmente el arreglo → **el test debe fallar** → restaura el arreglo → pasa.

Buenos tests:

- Prueban **comportamiento observable**, no detalles internos. Un test que solo verifica que se llamó un mock no prueba nada real.
- Incluyen los casos límite: vacío, nulo, un elemento, muchos, valores negativos o enormes, Unicode, errores de red.
- Son deterministas: sin depender del orden, de la hora real, de la red real ni de esperas fijas.
- Cuando un test falla, se corrige el **código**, no el test, salvo que el test esté demostradamente desactualizado (y entonces se explica por qué).

Excepciones razonables al test primero (consúltalas con el usuario si dudas): prototipos descartables, código generado y archivos de configuración.

---

## 6. Verificar una web en el navegador real

Que compile no significa que la página funcione. Si tu entorno tiene un navegador automatizable (Playwright, extensión de navegador, herramienta de capturas), úsalo.

**Árbol de decisión:**

```
¿Es HTML estático?
├─ Sí → Lee el HTML para identificar selectores y abre el archivo (file://)
└─ No (app dinámica) → ¿El servidor ya está corriendo?
    ├─ No → Levántalo (npm run dev, uvicorn, etc.) y espera a que responda
    └─ Sí → Reconocimiento y luego acción:
        1. Navega y espera a que cargue (networkidle)
        2. Toma una captura o inspecciona el DOM
        3. Identifica los selectores desde lo que realmente se renderizó
        4. Ejecuta las acciones con esos selectores
```

Error típico: inspeccionar el DOM **antes** de que el JavaScript termine de ejecutarse. En apps dinámicas, espera siempre a `networkidle` o a un elemento concreto.

Script mínimo en Python con Playwright:

```python
from playwright.sync_api import sync_playwright

URL = "http://localhost:5173"

with sync_playwright() as p:
    navegador = p.chromium.launch(headless=True)
    pagina = navegador.new_page()
    errores: list[str] = []
    pagina.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
    pagina.on("pageerror", lambda e: errores.append(str(e)))

    pagina.goto(URL)
    pagina.wait_for_load_state("networkidle")
    pagina.screenshot(path="captura-escritorio.png", full_page=True)

    # Recorrer el flujo real con selectores accesibles
    pagina.get_by_role("button", name="Nuevo pedido").click()
    pagina.get_by_label("Cliente").fill("Ana Pérez")
    pagina.get_by_role("button", name="Guardar").click()
    pagina.get_by_text("Pedido creado").wait_for()

    # Persistencia: recargar y comprobar que sigue ahí
    pagina.reload()
    pagina.wait_for_load_state("networkidle")
    assert pagina.get_by_text("Ana Pérez").is_visible()

    # Vista móvil
    pagina.set_viewport_size({"width": 375, "height": 812})
    pagina.screenshot(path="captura-movil.png", full_page=True)

    navegador.close()
    assert not errores, f"Errores en consola: {errores}"
```

Buenas prácticas:

- Selectores por rol, etiqueta o texto (`get_by_role`, `get_by_label`, `get_by_text`): son estables y además comprueban la accesibilidad.
- Navegador siempre en modo `headless` y cerrado al terminar.
- Esperas por condición, nunca `wait_for_timeout` fijo (ver `depuracion/GUIA.md`, sección 9).
- **Mira las capturas** que tomaste: confirma visualmente el diseño en escritorio y en móvil.
- Captura y revisa los errores de consola: una página "que se ve bien" con errores en consola no está bien.

Si no hay herramientas de navegador, como mínimo levanta el servidor, comprueba que responde (`curl` a la página y a los endpoints) y deja al usuario los pasos exactos para comprobarlo a mano.

---

## 7. Verificar trabajo delegado

Si un subagente u otra herramienta hizo parte del trabajo:

1. Lee su reporte, pero **no lo creas**.
2. Revisa el diff real (`git diff` o los archivos).
3. Ejecuta tú la verificación.
4. Informa el estado real, no el reportado.

---

## 8. Señales de alarma

Detente si te descubres:

- Usando "debería", "probablemente", "parece que" para describir el estado.
- Celebrando ("¡Listo!", "¡Perfecto!") antes de verificar.
- A punto de hacer commit o PR sin haber verificado.
- Confiando en una verificación parcial o anterior.
- Pensando "solo esta vez" o "el cambio es tan chico que no hace falta".

| Excusa | Realidad |
|---|---|
| "Ahora debería funcionar" | Ejecuta la verificación. |
| "Estoy seguro" | La seguridad no es evidencia. |
| "El linter pasó" | El linter no compila ni prueba comportamiento. |
| "El agente dijo que funcionó" | Verifícalo tú. |
| "Una verificación parcial alcanza" | Lo parcial no demuestra nada sobre el resto. |
| "El cambio es mínimo" | Los cambios mínimos también rompen cosas. |
