# Guía de depuración sistemática

Lee esta guía ante cualquier problema técnico: un bug, un test que falla, un build roto, un comportamiento inesperado, un problema de rendimiento o de integración. **Especialmente** cuando hay prisa, cuando "el arreglo parece obvio" o cuando ya probaste algo que no funcionó: son justo los momentos en que adivinar resulta más tentador y más caro.

> Adaptado y traducido de `systematic-debugging` de [obra/superpowers](https://github.com/obra/superpowers) (licencia MIT). Ver `CREDITOS.md`.

Contenido:

1. La ley de hierro
2. Fase 1: investigar la causa raíz
3. Fase 2: analizar patrones
4. Fase 3: hipótesis y prueba
5. Fase 4: implementar el arreglo
6. La regla de los intentos fallidos
7. Técnica: rastrear hacia atrás
8. Técnica: defensa en profundidad
9. Técnica: esperar la condición, no el tiempo
10. Señales de alarma y excusas comunes
11. Cuando de verdad no hay causa raíz

---

## 1. La ley de hierro

```
NINGÚN ARREGLO SIN INVESTIGAR ANTES LA CAUSA RAÍZ
```

Si no completaste la fase 1, no puedes proponer un arreglo. Arreglar síntomas es fracasar, aunque el síntoma desaparezca: la causa sigue ahí y aparecerá en otro lugar, normalmente rompiendo algo que funcionaba. La depuración sistemática **es más rápida** que el ensayo y error, incluso en emergencias.

---

## 2. Fase 1: investigar la causa raíz

Antes de intentar **cualquier** arreglo:

1. **Lee los mensajes de error con atención.** No saltes errores ni advertencias. Lee la traza completa: archivos, números de línea, códigos de error. A menudo contienen la solución exacta.
2. **Reproduce de forma confiable.** ¿Cuáles son los pasos exactos? ¿Ocurre siempre? Si no puedes reproducirlo, reúne más datos; no adivines.
3. **Revisa los cambios recientes.** ¿Qué cambió que pudo causarlo? `git diff`, commits recientes, dependencias nuevas, cambios de configuración o de entorno.
4. **En sistemas con varios componentes, reúne evidencia en cada frontera.** Cuando el flujo pasa por varias capas (frontend → API → servicio → base de datos, o CI → build → despliegue), **antes de proponer arreglos** agrega instrumentación temporal: registra qué datos entran y salen de cada componente y si la configuración y las variables de entorno llegan a cada capa. Ejecuta una vez, mira **dónde** se rompe y solo entonces investiga ese componente.
5. **Rastrea el flujo de datos.** Si el error aparece en lo profundo de la pila, sigue el valor malo hacia atrás hasta su origen (sección 7).

**Criterio para pasar a la fase 2:** entiendes **qué** falla y **por qué**.

---

## 3. Fase 2: analizar patrones

1. **Busca ejemplos que funcionan:** código parecido en el mismo proyecto que sí anda bien.
2. **Compara con la referencia:** si estás implementando un patrón o usando una librería, lee la documentación o la implementación de referencia **completa**, no por encima.
3. **Enumera las diferencias** entre lo que funciona y lo que no, por pequeñas que sean. No asumas que "eso no puede importar".
4. **Entiende las dependencias:** qué otros componentes, configuración y entorno necesita, y qué supuestos hace.

---

## 4. Fase 3: hipótesis y prueba

Método científico:

1. **Una sola hipótesis, por escrito:** "Creo que X es la causa raíz porque Y". Específica, no vaga.
2. **Pruébala con el cambio más pequeño posible**, una variable a la vez. No arregles varias cosas a la vez: si funciona, no sabrás cuál fue; si no, no sabrás cuál empeoró.
3. **Verifica antes de seguir.** ¿Funcionó? Pasa a la fase 4. ¿No funcionó? **Revierte ese cambio** y formula una hipótesis **nueva**; no apiles más arreglos encima.
4. **Si no sabes, dilo:** "No entiendo X". No finjas. Investiga más o pregunta al usuario.

---

## 5. Fase 4: implementar el arreglo

1. **Crea un caso que falle:** la reproducción más simple posible, como test automático si hay framework, o como script si no. Debe existir **antes** del arreglo.
2. **Implementa un solo arreglo** dirigido a la causa raíz. Nada de "ya que estoy" ni refactors mezclados.
3. **Verifica:** el test nuevo pasa, ningún otro test se rompió (suite completa) y el síntoma original desapareció en la app real. Comprueba que el test detecta el bug: revierte temporalmente el arreglo, el test debe fallar; restáuralo, debe pasar.
4. **Busca el mismo patrón** en el resto del código: el mismo error suele estar repetido.
5. **Considera la defensa en profundidad** (sección 8) para que el bug sea estructuralmente imposible.

---

## 6. La regla de los intentos fallidos

- **Después de 2 intentos fallidos:** detente. Revierte los intentos y vuelve a la fase 1 con la información nueva. No sigas probando variaciones: así es como se rompen otras cosas.
- **Después de 3 intentos fallidos:** el problema probablemente **no** es una hipótesis equivocada sino una **arquitectura equivocada**. Señales: cada arreglo revela un problema nuevo en otro lugar, los arreglos exigen una "refactorización masiva" o cada arreglo crea síntomas nuevos. **No intentes un cuarto arreglo.** Explica al usuario lo que sabes, lo que no, y discutan si el enfoque o el patrón de fondo son correctos.

---

## 7. Técnica: rastrear hacia atrás

Los bugs suelen manifestarse lejos de su origen (un archivo creado en la carpeta equivocada, una base de datos abierta con la ruta equivocada). El instinto es arreglar donde aparece el error; eso es tratar el síntoma.

1. **Observa el síntoma:** `Error: no existe el archivo config/app.json`.
2. **Encuentra la causa inmediata:** qué línea lo provoca.
3. **Pregunta quién la llamó y con qué valor**, y sube un nivel: `cargarConfig(ruta)` ← `iniciarApp(opciones)` ← `main()`.
4. **Sigue subiendo** hasta encontrar dónde nace el valor malo (por ejemplo, una ruta vacía que se resuelve contra el directorio actual).
5. **Arregla en el origen.**

Si no puedes rastrear a mano, agrega instrumentación **antes** de la operación problemática: los valores de entrada, el directorio actual, las variables de entorno relevantes y la pila de llamadas (`new Error().stack` en JS, `traceback.print_stack()` en Python). En tests, escribe a `stderr` (`console.error`, `print(..., file=sys.stderr)`), porque los loggers a veces están silenciados. Quita la instrumentación al terminar.

Si algo aparece durante los tests y no sabes qué test lo provoca, ejecútalos de uno en uno (o por bisección) hasta encontrar el primero que lo causa.

---

## 8. Técnica: defensa en profundidad

Cuando un bug se debió a datos inválidos, validar en un solo lugar parece suficiente, pero otro camino de código, un refactor o un mock pueden saltarse esa validación. Valida en cada capa por la que pasan los datos, para que el bug sea **imposible**, no solo "arreglado":

| Capa | Propósito | Ejemplo |
|---|---|---|
| 1. Entrada | Rechazar lo obviamente inválido en el borde (API, formulario, CLI) | "La carpeta no puede estar vacía", "no existe", "no es una carpeta" |
| 2. Lógica de negocio | Comprobar que el dato tiene sentido para *esta* operación | "Se requiere el ID del proyecto para iniciar el espacio de trabajo" |
| 3. Guardas de entorno | Impedir operaciones peligrosas en ciertos contextos | En tests, negarse a escribir fuera de la carpeta temporal |
| 4. Instrumentación | Dejar contexto para investigar si todo lo demás falla | Log con los valores y la pila antes de la operación peligrosa |

Usa esto con criterio: es para datos que pueden causar daño real (borrar, escribir, cobrar, enviar), no para cada parámetro de cada función.

---

## 9. Técnica: esperar la condición, no el tiempo

Los tests y el código "inestables" (a veces pasan, a veces no) suelen adivinar tiempos con esperas fijas: `sleep(2)`, `setTimeout(..., 500)`, `waitForTimeout(1000)`. Pasan en una máquina rápida y fallan con carga o en CI.

**Espera la condición real que te importa:**

```ts
// Mal: adivinar cuánto tarda
await new Promise((r) => setTimeout(r, 500));
expect(obtenerResultado()).toBeDefined();

// Bien: esperar a que ocurra (con un límite)
await esperarA(() => obtenerResultado() !== undefined, { timeoutMs: 5000 });
expect(obtenerResultado()).toBeDefined();
```

```python
def esperar_a(condicion, timeout=5.0, intervalo=0.05):
    limite = time.monotonic() + timeout
    while time.monotonic() < limite:
        if condicion():
            return
        time.sleep(intervalo)
    raise TimeoutError("La condición no se cumplió a tiempo")
```

En Playwright usa las esperas por condición (`expect(locator).toBeVisible()`, `page.wait_for_selector`, `wait_for_response`), no `wait_for_timeout`. Una espera fija solo es correcta cuando lo que pruebas **es** el tiempo (un debounce, un intervalo), y en ese caso se documenta por qué.

---

## 10. Señales de alarma y excusas comunes

Si te descubres pensando esto, **detente y vuelve a la fase 1**:

- "Un arreglo rápido por ahora y después investigo."
- "Pruebo a cambiar X a ver si funciona."
- "Meto varios cambios y corro los tests."
- "Me salto el test, lo verifico a mano."
- "Seguramente es X, lo arreglo."
- "No lo entiendo del todo, pero esto podría funcionar."
- Proponer soluciones antes de haber seguido el flujo de datos.
- "Un intento más" (cuando ya llevas dos).

Señales del usuario de que vas mal: "¿Eso no está pasando?" (asumiste sin verificar), "¿Eso nos va a mostrar...?" (debiste reunir evidencia), "Deja de adivinar", "¿Estamos atascados?".

| Excusa | Realidad |
|---|---|
| "Es simple, no necesito el proceso" | Los problemas simples también tienen causa raíz, y el proceso es rápido para ellos. |
| "Es una emergencia, no hay tiempo" | La depuración sistemática es más rápida que el ensayo y error. |
| "Primero pruebo esto y después investigo" | El primer arreglo marca el camino. Hazlo bien desde el principio. |
| "Escribo el test después de confirmar el arreglo" | Un arreglo sin test no se sostiene. |
| "Varios arreglos a la vez ahorran tiempo" | No puedes saber cuál funcionó y causas bugs nuevos. |
| "Veo el problema, lo arreglo" | Ver el síntoma no es entender la causa. |

---

## 11. Cuando de verdad no hay causa raíz

Si la investigación muestra que el problema es realmente del entorno, de tiempos o de un servicio externo:

1. Documenta lo que investigaste.
2. Implementa el manejo adecuado (reintento con límite, timeout, mensaje de error claro).
3. Agrega logs o métricas para investigar si vuelve a pasar.

Pero desconfía: la gran mayoría de los casos de "no hay causa raíz" son investigaciones incompletas.
