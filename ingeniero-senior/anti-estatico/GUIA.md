# Guía anti-estático: todo debe funcionar de verdad

Lee esta guía siempre que construyas o modifiques una pantalla, un flujo o una funcionalidad que alguien va a usar. Al terminar, ejecuta el detector:

```bash
python <carpeta-de-la-skill>/anti-estatico/detectar_estatico.py <carpeta-del-proyecto>
```

Contenido:

1. Qué es "estático" y por qué es tan grave
2. Las 10 formas de entregar algo falso
3. Cómo reemplazar cada una por algo real
4. Estados obligatorios de toda vista con datos
5. Flujos completos de punta a punta
6. Persistencia: lo que el usuario crea no se pierde
7. Cuándo sí se permiten datos de ejemplo
8. El detector automático
9. Prueba de "uso real"
10. Checklist anti-estático

---

## 1. Qué es "estático" y por qué es tan grave

"Estático" es todo lo que **aparenta** funcionar pero no funciona: una interfaz dibujada sobre nada. Un botón que no hace nada, una lista de usuarios que siempre muestra los mismos tres nombres inventados, un total que no suma, un formulario que dice "¡Enviado!" sin enviar nada.

Es el fallo más dañino que puede cometer un agente porque **pasa todas las revisiones superficiales**: compila, se ve bien en una captura y la demo funciona. El usuario lo descubre cuando ya confió en el trabajo, a veces en producción, y entonces tiene que revisar todo lo demás porque ya no sabe qué es real. Una sola parte falsa destruye la confianza en el resto.

La regla: **si en la interfaz parece que algo ocurre, tiene que ocurrir de verdad.** Si no puede ocurrir todavía, la interfaz lo dice.

---

## 2. Las 10 formas de entregar algo falso

| # | Forma | Ejemplo |
|---|---|---|
| 1 | Datos inventados en el componente | `const usuarios = [{nombre: "Juan"}, {nombre: "Ana"}]` dentro de la vista que debería leer de la API |
| 2 | Acción muerta | `<a href="#">`, `onClick={() => {}}`, `onClick={() => console.log("click")}`, `def on_click(): pass` |
| 3 | Éxito simulado | `alert("¡Guardado!")` sin llamar al backend; `setTimeout(() => setEnviado(true), 1000)` |
| 4 | Retorno fijo | `return true`, `return []`, `return {ok: true}` en lugar de la lógica real |
| 5 | Valores calculados escritos a mano | "Total: $1.250" como texto fijo; "Hace 5 minutos" fijo; contador "3 notificaciones" fijo |
| 6 | Configuración hardcodeada | `fetch("http://localhost:3000/api")`, claves de API en el código, IDs de base de datos escritos a mano |
| 7 | Solo el caso feliz | La vista asume que los datos llegan, nunca vacíos, nunca con error, nunca lentos |
| 8 | Estado que se pierde | Lo que el usuario crea vive solo en memoria y desaparece al recargar |
| 9 | Funcionalidad pendiente escondida | `// TODO: conectar con backend` dentro de un flujo presentado como terminado; `raise NotImplementedError` en un camino alcanzable |
| 10 | Contenido de relleno | "Lorem ipsum", imágenes de `placehold.co`/`picsum`, "Usuario Ejemplo", "Producto 1, Producto 2" |

---

## 3. Cómo reemplazar cada una por algo real

### 1. Datos inventados → capa de datos real

- Los datos vienen de una fuente: API, base de datos, archivo, almacenamiento local o estado global. La vista los **pide**; no los contiene.
- Separa el acceso a datos en una capa propia (servicio, repositorio, hook como `usePedidos()`, función `obtener_pedidos()`). Así la vista no cambia si cambia la fuente.
- Si el backend todavía no existe y el usuario no lo pidió, **pregunta o constrúyelo** (aunque sea mínimo: un endpoint, una tabla SQLite, un archivo JSON leído y escrito de verdad). No lo simules en silencio.

### 2. Acción muerta → acción completa

Cada elemento interactivo lleva a algo real: navegar, abrir algo, llamar a una función que cambia el estado o envía datos. Si una acción no está en el alcance, **no pongas el botón**, o ponlo deshabilitado con una explicación visible ("Disponible próximamente"), y dilo en el reporte.

### 3. Éxito simulado → resultado real

La confirmación se muestra **después** de que la operación responde con éxito, y el error se muestra si falla. El patrón:

```js
async function guardar(datos) {
  setEstado({ tipo: "guardando" });
  try {
    const res = await fetch(`${API_URL}/pedidos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });
    if (!res.ok) throw new Error(await mensajeDeError(res));
    const creado = await res.json();
    setEstado({ tipo: "exito", pedido: creado });
  } catch (err) {
    setEstado({ tipo: "error", mensaje: err.message });
  }
}
```

### 4. Retorno fijo → lógica real

Si una función todavía no puede implementarse, que **falle de forma explícita y visible** (`throw new Error("Pago no implementado: falta la credencial del proveedor")`) en vez de devolver un éxito falso. Un error ruidoso se detecta en minutos; un éxito falso, en producción.

### 5. Valores fijos → valores derivados

Totales, contadores, fechas relativas, nombres del usuario, cantidades en el carrito: se **calculan** a partir de los datos. Si cambias un dato, todo lo que depende de él cambia solo.

### 6. Configuración hardcodeada → configuración externa

- URLs, puertos, claves y flags en variables de entorno (`import.meta.env.VITE_API_URL`, `process.env.X`, `os.environ` / `pydantic-settings`).
- Un `.env.example` documenta todas las claves; la app falla al arrancar, con un mensaje claro, si falta una obligatoria.
- Textos que se repiten y constantes de negocio (impuestos, límites) en un único módulo de constantes o configuración.

### 7. Solo caso feliz → todos los estados

Ver sección 4.

### 8. Estado volátil → persistencia

Ver sección 6.

### 9. TODO escondido → pendiente declarado

Un `TODO` está permitido solo si **no** está en un flujo que el usuario va a usar como terminado y **además** se menciona en el reporte final. Si está en un flujo real, se implementa.

### 10. Relleno → contenido real o realista

Usa el contenido real del proyecto. Si no lo hay, escribe texto realista del tema (no "Lorem ipsum") y marca en el reporte qué textos o imágenes debe reemplazar el usuario.

---

## 4. Estados obligatorios de toda vista con datos

Modela el estado de forma explícita, no con varios booleanos sueltos que pueden contradecirse (`cargando = true` y `error = "..."` a la vez):

```ts
type Estado<T> =
  | { tipo: "cargando" }
  | { tipo: "vacio" }
  | { tipo: "error"; mensaje: string }
  | { tipo: "listo"; datos: T };
```

| Estado | Qué debe ver el usuario |
|---|---|
| **Cargando** | Indicador o skeleton con la forma del contenido final; sin saltos de layout; acciones de envío deshabilitadas para evitar doble envío. |
| **Vacío** | Explicación y la acción para empezar ("Todavía no hay pedidos. Crea el primero"). Distinto de "sin resultados para esta búsqueda" (que ofrece limpiar filtros). |
| **Error** | Qué falló en lenguaje claro, botón de reintentar, y el resto de la página sigue usable. El detalle técnico va al log, no a la pantalla. |
| **Listo / éxito** | Los datos; tras una acción, confirmación visible y la interfaz actualizada (la fila nueva aparece, el contador sube). |
| **Parcial** | Si una parte falla, el resto se muestra igual. |
| **Sin permiso / sin sesión** | Redirección o mensaje adecuado, nunca una pantalla rota. |

Además: **tiempo de espera** en las peticiones, cancelación de peticiones obsoletas (si el usuario cambia de filtro rápido, que no gane la respuesta vieja) y protección contra doble envío.

---

## 5. Flujos completos de punta a punta

Antes de implementar, enumera el ciclo de vida completo de cada entidad y de cada flujo, y confirma con el usuario qué partes entran en el alcance:

- **Entidades:** crear, ver lista, ver detalle, editar, eliminar (con confirmación), buscar/filtrar/paginar si la lista puede crecer.
- **Autenticación:** registro, login, logout, sesión expirada, recuperar contraseña, rutas protegidas, qué ve un usuario sin permisos.
- **Formularios:** validación en cliente **y** servidor, errores por campo, conservar lo escrito si falla, confirmación al terminar.
- **Navegación:** cada enlace lleva a una página que existe; la URL refleja el estado (filtros, página, pestaña) para poder recargar o compartir; botón atrás del navegador funciona; página 404.
- **Archivos:** subir (con límite de tamaño y tipos), mostrar progreso, manejar el error, poder borrar.

Recorre cada flujo como lo haría un usuario real, en la app ejecutándose, antes de darlo por terminado.

---

## 6. Persistencia: lo que el usuario crea no se pierde

- Todo dato que el usuario crea o modifica sobrevive a una recarga de la página y a un reinicio de la app, salvo que sea explícitamente temporal.
- Elige la persistencia según el caso: base de datos en el servidor para datos compartidos o importantes; `localStorage`/`IndexedDB` solo para preferencias o borradores de un usuario en un dispositivo (y envuelto en `try/catch`, porque puede fallar); archivo para apps de escritorio o scripts.
- Después de guardar, la interfaz refleja lo que **quedó guardado** (la respuesta del servidor), no lo que el cliente supone.
- Si usas actualizaciones optimistas, revierte el cambio visual si el servidor falla y avisa al usuario.

---

## 7. Cuándo sí se permiten datos de ejemplo

Solo en estos casos, y siempre **aislados y declarados**:

- El usuario pidió expresamente una maqueta, prototipo o demo.
- Datos semilla (`seed`) para desarrollo, cargados en la base de datos real con un script, no escritos en los componentes.
- Fixtures de tests, dentro de la carpeta de tests.
- Mocks de servicios externos en desarrollo (por ejemplo con MSW), activados por una variable de entorno y nunca en producción.

En todos los casos: viven en su propia carpeta (`mocks/`, `seed/`, `fixtures/`, `tests/`), nunca dentro de componentes de producción, y el reporte final lo dice.

---

## 8. El detector automático

`anti-estatico/detectar_estatico.py` busca en el código los patrones más comunes de la sección 2 (enlaces `#`, handlers vacíos, `TODO`, "Lorem ipsum", URLs de `localhost`, posibles secretos, `except`/`catch` vacíos, silenciadores de errores, datos mock en código de producción, imágenes de relleno y más).

```bash
# Escanear todo el proyecto
python anti-estatico/detectar_estatico.py ./mi-proyecto

# Solo los archivos que cambiaste (pásalos explícitamente)
python anti-estatico/detectar_estatico.py src/pages/Pedidos.tsx src/api/pedidos.ts

# Salida JSON
python anti-estatico/detectar_estatico.py ./mi-proyecto --json

# Ver también los avisos de severidad baja
python anti-estatico/detectar_estatico.py ./mi-proyecto --todo
```

Devuelve código de salida 1 si encuentra hallazgos de severidad alta. Solo usa la biblioteca estándar de Python.

**Cómo interpretar el resultado:** el detector es una red, no un juez. Cada hallazgo se **resuelve** (se reemplaza por algo real) o se **justifica** en el reporte ("`localhost` en `vite.config.ts` es el proxy de desarrollo, correcto"). No basta con que el detector salga limpio: muchos casos de la sección 2 (éxito simulado, solo caso feliz, estado que se pierde) no se detectan con patrones y solo los descubre la prueba de la sección 9.

---

## 9. Prueba de "uso real"

Con la aplicación ejecutándose de verdad:

1. Haz clic en **cada** botón, enlace y elemento del menú de las pantallas que tocaste. ¿Todos hacen algo?
2. Crea un dato, **recarga la página**: ¿sigue ahí? Edítalo y bórralo.
3. Envía cada formulario vacío, con datos inválidos y con datos válidos.
4. Corta la red o apaga el backend (o simula un error 500): ¿la interfaz lo dice y permite reintentar?
5. Mira la pantalla sin datos (base vacía) y con muchos datos.
6. Cambia un dato de origen (en la base o la API): ¿la interfaz muestra el valor nuevo, o había algo fijo?
7. Revisa la consola del navegador y los logs del servidor: sin errores.

Si tienes herramientas de navegador automatizado (Playwright, extensión de navegador), úsalas para esta prueba y guarda capturas. Ver `verificacion/GUIA.md`.

---

## 10. Checklist anti-estático

- [ ] Ninguna vista contiene datos inventados; todo sale de una fuente real a través de una capa de datos.
- [ ] Cada botón, enlace y menú hace algo real, o está deshabilitado con explicación y reportado.
- [ ] Ninguna confirmación de éxito se muestra sin que la operación haya tenido éxito.
- [ ] Totales, contadores y fechas se calculan; no hay valores que deberían cambiar escritos a mano.
- [ ] URLs, claves y constantes de negocio salen de configuración; existe `.env.example`.
- [ ] Toda vista con datos tiene estados de carga, vacío, error y éxito.
- [ ] Los flujos están completos de punta a punta (o lo que falta está acordado y reportado).
- [ ] Lo que el usuario crea persiste tras recargar.
- [ ] Sin "Lorem ipsum" ni imágenes de relleno, salvo maqueta pedida y declarada.
- [ ] Ejecuté `detectar_estatico.py` y resolví o justifiqué cada hallazgo.
- [ ] Hice la prueba de "uso real" de la sección 9.
