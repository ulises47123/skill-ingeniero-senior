# Guía de diseño de interfaces (GUI)

Lee esta guía siempre que la tarea tenga una interfaz: página web, app, dashboard, componente, formulario, landing, rediseño o GUI de escritorio. Una interfaz no está terminada porque "funciona": tiene que entenderse sin explicaciones, verse intencional, funcionar en cualquier pantalla y poder usarse con teclado y lector de pantalla.

Contenido:

1. Primero, respeta lo que ya existe
2. Proceso de diseño en dos pasadas
3. Sistema de tokens
4. Tipografía
5. Color
6. Layout y responsive
7. Componentes y estados de interacción
8. Movimiento
9. Accesibilidad
10. Textos de la interfaz (microcopy)
11. Señales de diseño genérico "hecho por IA"
12. Rendimiento visual
13. GUI de escritorio
14. Autocrítica y checklist final

---

## 1. Primero, respeta lo que ya existe

Antes de diseñar nada, busca en el proyecto:

- Un sistema de diseño, librería de componentes (shadcn/ui, MUI, Chakra, Vuetify, Bootstrap, etc.) o archivo de tokens/tema.
- Variables CSS, configuración de Tailwind, fuentes ya cargadas, iconos ya usados.
- Pantallas existentes que puedas usar como referencia de estilo.

**Si existe, se usa y se extiende; no se reemplaza.** Una pantalla nueva que no se parece al resto de la app es un bug de diseño. Las indicaciones explícitas del usuario sobre estilo ganan siempre, incluso si piden algo que esta guía desaconseja.

Solo cuando no hay nada previo (proyecto nuevo o rediseño pedido) aplicas la dirección visual completa de la sección 2.

---

## 2. Proceso de diseño en dos pasadas

### Paso 0: anclarse en el tema

Antes de elegir colores, define en una frase cada uno: **qué es** el producto o tema, **para quién** es y **cuál es su tarea principal**. Si el pedido no lo dice, propón tú una respuesta concreta y confírmala. Las decisiones visuales distintivas salen del mundo del tema (su industria, materiales, vocabulario): un juguete para niñas de 8 a 11 años y un dashboard para analistas financieros no pueden verse parecidos. Usa contenido real del tema en todo el diseño, nunca "Lorem ipsum".

### Pasada 1: plan de diseño compacto

Escribe (en el plan, antes de codificar):

- **Color:** paleta base de 4 a 6 valores hex con nombre y rol (fondo, superficie, texto, texto secundario, acento, borde) más los semánticos (éxito, error, aviso, información).
- **Tipografía:** familias elegidas y su rol, y la escala de tamaños.
- **Layout:** el concepto en una frase y un wireframe ASCII de las pantallas principales. Indica la alineación (izquierda, centrada).
- **Principios:** 2 o 3 frases sobre qué hace única a esta interfaz y dónde va a estar el único elemento memorable.

Ejemplo de wireframe:

```
+------------------------------------------------+
| Logo        Buscar [______________]   Avatar v |
+----------+-------------------------------------+
| Filtros  |  Pedidos (128)          [+ Nuevo]   |
| [ ] Hoy  |  +--------------------------------+ |
| [ ] Pend |  | #1042  Ana P.   $120   Pagado  | |
|          |  | #1041  Luis M.  $80    Pend.   | |
|          |  +--------------------------------+ |
|          |  < 1 2 3 ... >                      |
+----------+-------------------------------------+
```

### Revisión del plan

Antes de construir, compara el plan con el pedido: si alguna parte es lo que habrías hecho para *cualquier* página parecida, en lugar de una decisión para *esta*, cámbiala y explica qué cambiaste y por qué. Revisa también la lista de la sección 11.

### Pasada 2: construir y criticar

Construye siguiendo el plan revisado. Mientras construyes, mira el resultado real (captura de pantalla o navegador si tu entorno lo permite: una imagen vale más que mil líneas de código) y corrige. Al final aplica el consejo de Chanel: antes de salir, mírate al espejo y quítate un accesorio.

---

## 3. Sistema de tokens

Nunca escribas valores "mágicos" sueltos (`margin: 13px`, `color: #3a7bd5` en veinte sitios). Define tokens una vez y úsalos en todas partes; así un cambio de marca o un modo oscuro es cambiar un archivo, no cazar valores por todo el proyecto. Punto de partida: `diseno/plantilla-tokens.css` (estructura, no estética: reemplaza los valores por los del plan).

- **Espaciado:** escala basada en 4 u 8 px (4, 8, 12, 16, 24, 32, 48, 64...). Más espacio entre grupos que dentro de un grupo: así se lee la jerarquía.
- **Tipografía:** escala con proporción constante (por ejemplo 1.2 o 1.25).
- **Radios:** pocos valores y con sentido jerárquico (un botón y un modal no tienen por qué tener el mismo radio).
- **Sombras/elevación:** 2 o 3 niveles como máximo, usados con significado (lo que flota sobre otra cosa).
- **Colores semánticos:** `--color-error`, `--color-exito`, etc., no `--rojo`.
- **Modo oscuro:** si se implementa, redefine los tokens en `@media (prefers-color-scheme: dark)` o con un atributo `data-theme`; no dupliques componentes.

---

## 4. Tipografía

La tipografía lleva la personalidad de la interfaz.

- Una o dos familias como máximo; si son dos, que sean claramente distintas (por ejemplo, una serif para títulos y una sans para texto).
- Elige las fuentes deliberadamente para el tema, no por costumbre. Carga solo los pesos que usas y con `font-display: swap`.
- Texto base de 16 px como mínimo en web; nunca menos de 14 px para texto legible.
- Longitud de línea de texto corrido por debajo de 80 caracteres (`max-width: 65ch` es un buen valor).
- Interlineado de 1.4 a 1.6 para texto, 1.1 a 1.25 para títulos. Las serif necesitan un poco más.
- Jerarquía con tamaño, peso y espacio, no con cinco colores distintos.
- Cifras tabulares (`font-variant-numeric: tabular-nums`) en tablas y montos para que las columnas se alineen.

---

## 5. Color

- **Contraste WCAG AA como mínimo:** 4.5:1 para texto normal, 3:1 para texto grande (24 px o 19 px en negrita) y para bordes de controles e iconos con significado. Compruébalo; no lo estimes a ojo.
- **Nunca transmitas información solo con color:** un error lleva un icono o texto además del rojo; un gráfico distingue series también por forma o etiqueta.
- Un acento principal usado con moderación para la acción más importante. Si todo está resaltado, nada lo está.
- Neutros con un ligero tinte de la paleta se ven más cohesivos que grises puros.
- Estados semánticos consistentes en toda la app: el mismo verde significa siempre éxito.

---

## 6. Layout y responsive

- **Mobile first:** diseña para 360 px de ancho y amplía. Ninguna pantalla puede tener scroll horizontal accidental.
- Usa Grid y Flexbox; evita posiciones absolutas para maquetar y anchos fijos en px para contenedores.
- Breakpoints según el contenido (donde el diseño se rompe), no según dispositivos concretos.
- Márgenes laterales de al menos 16 px en móvil.
- Áreas táctiles de 44×44 px como mínimo.
- El contenido cambia: prueba con textos el doble de largos (traducciones, nombres largos), listas de 0, 1 y 1000 elementos, e imágenes que no cargan. Usa `min-width: 0` en hijos flex y `overflow-wrap: anywhere` en textos que pueden ser URLs o palabras largas.
- Imágenes con `width`/`height` o `aspect-ratio` para que la página no salte al cargar.
- La estructura visual es información: bordes, numeraciones, separadores y etiquetas deben comunicar algo del contenido, no decorar. Numera (01, 02, 03) solo si el contenido es realmente una secuencia.
- Cuidado con la especificidad del CSS: es fácil crear clases que se anulan entre sí (por ejemplo, márgenes de `.section` contra `.cta`). Mantén los selectores planos y predecibles.

---

## 7. Componentes y estados de interacción

Cada elemento interactivo necesita todos sus estados, diseñados y probados:

| Estado | Requisito |
|---|---|
| Normal | Se reconoce que es interactivo (un botón parece botón, un enlace parece enlace). |
| Hover | Cambio visible pero sutil (solo en dispositivos con puntero). |
| Focus | **Indicador de foco visible** con `:focus-visible`, con buen contraste. Nunca `outline: none` sin reemplazo. |
| Active/pressed | Respuesta inmediata al clic o toque. |
| Disabled | Se ve deshabilitado y, si no es obvio, se explica por qué. |
| Loading | El botón muestra progreso y no admite doble envío. |

Y cada vista con datos tiene sus estados de datos: **cargando** (skeleton o indicador, sin saltos de layout), **vacío** (mensaje útil y acción para empezar), **error** (qué pasó y cómo reintentar) y **éxito** (confirmación visible). Ver `anti-estatico/GUIA.md`.

Formularios:

- Cada campo tiene `<label>` visible (el placeholder no es una etiqueta).
- Tipo de input correcto (`email`, `tel`, `number`, `date`) y `autocomplete` adecuado.
- Validación al salir del campo o al enviar, no en cada tecla; mensajes junto al campo que dicen cómo corregir.
- Al fallar el envío, se conserva lo que el usuario escribió y se lleva el foco al primer error.

Componentes complejos (modales, menús desplegables, pestañas, combobox): usa los de la librería del proyecto o elementos nativos (`<dialog>`, `<details>`, `<select>`) antes que construirlos desde cero; la accesibilidad de teclado de estos componentes es difícil de hacer bien.

---

## 8. Movimiento

- El movimiento que responde a una acción del usuario (abrir, expandir, confirmar) es bienvenido si muestra qué cambió.
- El movimiento automático se usa poco: un solo momento orquestado (por ejemplo, una entrada al cargar) funciona mejor que efectos repartidos por todas partes. Animar la entrada de cada sección y cada tarjeta es el patrón genérico.
- Duraciones de 150 a 250 ms para microinteracciones; anima `transform` y `opacity`, no `width`, `height` ni `top`.
- **Respeta `prefers-reduced-motion`:** reduce o elimina las animaciones no esenciales.

---

## 9. Accesibilidad

Es un piso de calidad, no un extra, y no hace falta anunciarlo:

- HTML semántico: `<button>` para acciones, `<a>` para navegación, `<nav>`, `<main>`, `<header>`, encabezados `h1`-`h6` en orden sin saltos.
- Todo se puede usar con teclado, en un orden de tabulación lógico. Los modales atrapan el foco y lo devuelven al cerrar; `Esc` cierra.
- `alt` descriptivo en imágenes con significado; `alt=""` en las decorativas.
- ARIA solo cuando no hay un elemento nativo que sirva. Un ARIA mal puesto es peor que ninguno.
- Anuncia los cambios dinámicos importantes (errores, resultados de búsqueda, toasts) con `aria-live`.
- La interfaz funciona con zoom al 200 % sin perder contenido.
- Idioma declarado (`<html lang="es">`).

Para una revisión más profunda, si están disponibles, usa las skills de accesibilidad del entorno.

---

## 10. Textos de la interfaz (microcopy)

Las palabras son contenido de diseño, no decoración.

- Escribe desde la perspectiva del usuario y con su vocabulario: "Notificaciones", no "Configuración de webhooks".
- Botones con verbo que dice exactamente qué pasa: "Guardar cambios", no "Enviar"; "Eliminar proyecto", no "OK".
- Una acción conserva su nombre en todo el flujo: el botón "Publicar" produce el aviso "Publicado".
- Los errores dicen qué pasó y cómo arreglarlo, sin culpar ni disculparse en exceso, y nunca son vagos ("Algo salió mal" no ayuda): "No pudimos guardar. Revisa tu conexión y vuelve a intentarlo".
- Un estado vacío es una invitación a actuar: "Todavía no tienes proyectos. Crea el primero".
- Frases cortas, mayúscula solo al inicio, sin relleno.

---

## 11. Señales de diseño genérico "hecho por IA"

Estos rasgos aparecen sin importar el tema y delatan una interfaz sin decisiones propias. Son válidos si el pedido los requiere, pero **no los uses por defecto**:

1. Fondo crema cálido (cerca de `#F4F1EA`) con serif de alto contraste y acento terracota (cerca de `#D97757`).
2. Fondo casi negro con un único acento verde ácido o bermellón.
3. Maquetación tipo periódico con líneas finas, cero radio y columnas densas.
4. El "kit de tarjetas SaaS": todo cortado en tarjetas redondeadas idénticas, el mismo radio en todo, la misma sombra gris suave y degradados como decoración.
5. Hero por defecto: número gigante con etiqueta pequeña, estadísticas y acento degradado.
6. Etiqueta en MAYÚSCULAS con mucho espaciado encima de cada título; resaltar una sola palabra del título en otro color o en cursiva; datos separados con puntos medios ("A · B · C"); una flecha "→" agregada a cada enlace o botón; fuente monoespaciada para etiquetas pequeñas.
7. Animación de entrada "fade + subir" en cada sección y transición en hover en cada tarjeta.
8. Emojis como iconos en una interfaz profesional.

Gasta la audacia en **un solo lugar**: que un elemento sea lo memorable y que todo lo demás sea tranquilo y disciplinado.

---

## 12. Rendimiento visual

- Imágenes en formatos modernos (WebP/AVIF), con el tamaño adecuado y `loading="lazy"` debajo del primer pantallazo.
- Evita saltos de layout (CLS): reserva espacio para imágenes, anuncios y contenido que carga tarde.
- No cargues una librería de iconos entera para usar tres; no cargues cinco pesos de una fuente para usar dos.
- Listas muy largas: paginación o virtualización.

---

## 13. GUI de escritorio (Tkinter, Qt, Electron, etc.)

Los mismos principios aplican, con algunos extras:

- Nunca bloquees el hilo de la interfaz con trabajo pesado o de red: usa hilos, workers o tareas asíncronas y actualiza la interfaz desde el hilo principal.
- Muestra progreso en operaciones largas y permite cancelarlas.
- Usa layouts que se adaptan al redimensionar (grid/box layouts), no coordenadas absolutas.
- Atajos de teclado estándar (Ctrl+S, Ctrl+Z, Esc para cerrar diálogos) y orden de tabulación lógico.
- Recuerda el tamaño y la posición de la ventana y las preferencias del usuario entre sesiones.
- Respeta la escala de pantalla (DPI alto) y, si la plataforma lo permite, el tema claro/oscuro del sistema.

---

## 14. Autocrítica y checklist final

Mira la interfaz real (capturas en móvil y escritorio si tu entorno lo permite) y comprueba:

- [ ] Si el proyecto tenía sistema de diseño, lo usé; la pantalla nueva se ve parte de la misma app.
- [ ] Hubo un plan de diseño (paleta, tipografía, layout, principios) revisado contra el pedido.
- [ ] Todos los valores salen de tokens; no hay colores ni medidas mágicas sueltas.
- [ ] Contraste AA comprobado; la información no depende solo del color.
- [ ] Funciona de 360 px a pantallas anchas sin scroll horizontal ni elementos cortados.
- [ ] Todos los controles tienen estados hover, focus visible, active, disabled y loading.
- [ ] Todas las vistas con datos tienen estados de carga, vacío, error y éxito.
- [ ] Se puede usar entera con teclado; los formularios tienen labels y errores claros.
- [ ] Respeta `prefers-reduced-motion`.
- [ ] Los textos son claros, específicos y consistentes; no hay "Lorem ipsum".
- [ ] No cae en las señales genéricas de la sección 11 (salvo que el pedido lo pida).
- [ ] Hay un elemento memorable y quité al menos un adorno innecesario.
- [ ] La consola del navegador no muestra errores ni advertencias nuevas.
