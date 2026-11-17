# Guía para escribir planes de implementación

Lee esta guía para cualquier tarea mediana o grande (ver la sección 2 de `SKILL.md`), antes de tocar código. El plan se muestra al usuario y **se espera su aprobación** antes de implementar.

> Adapta ideas de `writing-plans` y `brainstorming` de [obra/superpowers](https://github.com/obra/superpowers) (MIT). Ver `CREDITOS.md`.

Contenido:

1. Para qué sirve un plan
2. Antes del plan: entender y elegir el enfoque
3. Comprobar el alcance
4. Mapa de archivos
5. Tamaño correcto de cada tarea
6. Plantilla de plan
7. Qué contiene un buen paso
8. Autorrevisión del plan
9. Presentar el plan y ejecutarlo

---

## 1. Para qué sirve un plan

Un plan es **el conjunto de decisiones que alguien que no conoce el proyecto no podría tomar solo**: qué archivos, qué nombres y firmas, qué valores, qué tests demuestran cada parte y en qué orden se hace para que el sistema nunca quede roto. Escríbelo como si lo fuera a implementar un ingeniero competente que nunca vio este código ni este pedido.

Un plan evita los tres fallos más caros: resolver el problema equivocado (el usuario lo corrige antes de que escribas código), descubrir a mitad de camino que el enfoque no sirve, y romper cosas por no haber visto qué dependía de qué.

---

## 2. Antes del plan: entender y elegir el enfoque

1. **Explora el código** (fase 2 de `SKILL.md`): estructura, convenciones, qué existe ya y cómo se prueba.
2. **Aclara lo que bloquea**, de a una pregunta por vez y, cuando se pueda, con opciones concretas para elegir.
3. **Si hay más de una forma razonable de hacerlo, propón 2 o 3 enfoques** con sus ventajas, desventajas y tu recomendación, y deja que el usuario elija. Ejemplo: "A) guardar en `localStorage` (rápido, pero solo en este navegador), B) agregar una tabla en la base de datos actual (recomendado: los datos se comparten y no se pierden), C) servicio externo (más trabajo, solo si ya lo usan)".
4. Aplica **YAGNI** sin piedad: quita del alcance todo lo que no se pidió y no hace falta.

---

## 3. Comprobar el alcance

Si el pedido abarca varios subsistemas independientes (por ejemplo, "una app con usuarios, pagos, panel de administración y notificaciones"), **propón dividirlo** en varios planes, uno por subsistema, cada uno capaz de producir software que funciona y se puede probar por sí solo. Un plan gigante es un plan que nadie revisa de verdad.

---

## 4. Mapa de archivos

Antes de definir tareas, enumera qué archivos se crean o modifican y de qué es responsable cada uno. Aquí se fijan las decisiones de diseño:

- Unidades con límites claros e interfaces bien definidas; cada archivo con una responsabilidad.
- Archivos pequeños y enfocados antes que archivos enormes que hacen de todo: se razonan mejor y se editan con menos errores.
- Lo que cambia junto vive junto: divide por responsabilidad, no por capa técnica.
- En proyectos existentes, **sigue los patrones establecidos**. No reestructures por tu cuenta; si un archivo que vas a tocar está inmanejable, proponer dividirlo como parte del plan es razonable.

---

## 5. Tamaño correcto de cada tarea

Una tarea es la unidad más pequeña que tiene su propio ciclo de prueba y que un revisor podría aprobar o rechazar por separado. Incluye la configuración, el andamiaje y la documentación dentro de la tarea que los necesita. **Cada tarea termina con algo que se puede probar de forma independiente y deja el sistema funcionando.**

Cada paso dentro de una tarea es **una acción con un resultado comprobable**:

- "Escribir el test que falla" → paso.
- "Ejecutarlo y comprobar que falla" → paso.
- "Implementar el código mínimo" → paso.
- "Ejecutar los tests y comprobar que pasan" → paso.

---

## 6. Plantilla de plan

````markdown
# Plan: <nombre de la funcionalidad>

**Objetivo:** <una frase: qué se construye y cómo se sabrá que está bien>

**Contexto encontrado:** <cómo funciona hoy; archivos y piezas relevantes; qué se reutiliza>

**Enfoque:** <2-3 frases sobre la solución y por qué; alternativas descartadas y por qué>

**Tecnologías:** <lenguaje, framework, librerías clave>

**Diseño (si hay interfaz):** <paleta, tipografía, wireframe ASCII y principios, según diseno/GUIA.md>

## Restricciones globales
- <requisitos que aplican a todo: versiones, dependencias permitidas, convenciones, plataformas>

## Impacto y riesgos
- <qué depende de lo que se toca y cómo se protege>
- <cambios de contrato (API, esquema, tipos) y cómo se manejan>
- <riesgos de datos y cómo volver atrás>

## Casos que más pueden fallar
- <las 3-5 entradas o situaciones que el pedido no menciona pero que un usuario real va a provocar (vacío, error de red, doble clic, datos enormes, permisos) y el comportamiento esperado; cada una con su test en la tarea correspondiente>

## Mapa de archivos
- Crear: `ruta/exacta/archivo.ext` — responsabilidad
- Modificar: `ruta/exacta/otro.ext` — qué cambia
- Tests: `tests/ruta/test_archivo.ext`

---

### Tarea 1: <componente>

**Archivos:** <crear / modificar / tests>

**Interfaces:**
- Usa: <firmas exactas de tareas anteriores>
- Produce: <nombres, parámetros y tipos que usarán tareas posteriores>

- [ ] Paso 1: escribir el test `test_<comportamiento>` que verifica <aserción concreta con valores>
- [ ] Paso 2: ejecutar `<comando>` → esperado: FALLA por <motivo>
- [ ] Paso 3: implementar `<firma exacta>` en `<archivo>`
- [ ] Paso 4: ejecutar `<comando>` → esperado: PASA, y la suite completa sigue en verde
- [ ] Paso 5: <verificación en la app real, si aplica>

### Tarea 2: ...

---

## Fuera de alcance
- <lo que explícitamente no se hace>

## Dudas y supuestos
- <lo que necesita confirmación del usuario>
````

---

## 7. Qué contiene un buen paso

Un paso está bien escrito cuando quien lo implementa solo puede hacer **una** cosa razonable a partir de él. Debe ser inequívoco, no exhaustivo:

- **Paso de test:** el nombre del test y sus aserciones con los valores exactos.
- **Paso de código:** la firma exacta (nombre, parámetros, tipo de retorno) y el archivo. El cuerpo solo se escribe si es un algoritmo que la firma y los tests no determinan.
- **Paso de verificación:** el comando y la salida que significa éxito.
- **Referencia a otra tarea:** se apoya en su bloque de interfaces; no se repite su código.

Dos fallos opuestos:

- **Demasiado vago:** "manejar casos límite", "agregar validación apropiada", "escribir tests", "TBD", una función que ninguna tarea define. Eso no decide nada.
- **Demasiado detallado:** un plan más largo que el código que describe ya escribió el código en vez de planificarlo.

---

## 8. Autorrevisión del plan

Al terminar, relee el pedido con ojos frescos y revisa el plan contra él:

1. **Cobertura:** ¿cada requisito del pedido tiene una tarea que lo implementa? Si falta alguno, agrega la tarea.
2. **Pasos:** ¿algún paso no decide nada (vago) o transcribe código que la firma y el test ya determinan (exceso)? Corrígelo.
3. **Consistencia de tipos y nombres:** ¿las firmas y nombres usados en tareas posteriores coinciden con los definidos antes? `limpiarCapas()` en la tarea 3 y `limpiarTodasLasCapas()` en la tarea 7 es un bug.
4. **Casos que más pueden fallar:** ¿cada uno tiene su test en alguna tarea?
5. **Impacto:** ¿cada cosa que depende de lo que se modifica está protegida o verificada?
6. **Orden:** ¿después de cada tarea el sistema compila y funciona?
7. **Proporción:** ¿el plan es razonable frente al tamaño del pedido?

Corrige en el mismo plan; no hace falta otra ronda de revisión.

---

## 9. Presentar el plan y ejecutarlo

1. Muestra el plan al usuario (si el proyecto lo prefiere, guárdalo también en un archivo, por ejemplo `docs/planes/AAAA-MM-DD-<nombre>.md`).
2. Pregunta explícitamente: "¿El plan refleja lo que quieres? ¿Apruebo y empiezo?". **No implementes hasta tener la aprobación.**
3. Al ejecutar, sigue las tareas en orden, marca cada paso al completarlo y verifica al final de cada tarea (no solo al final de todo).
4. Si la realidad obliga a desviarse del plan, detente, explica qué encontraste y, si el cambio es significativo, vuelve a pedir aprobación.
5. Al terminar, vuelve a leer el plan y confirma, punto por punto, qué se cumplió (`verificacion/GUIA.md`).
