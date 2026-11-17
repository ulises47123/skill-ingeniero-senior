# Guía de buenas prácticas en Python

Lee esta guía siempre que la tarea sea en Python: scripts, APIs, CLIs, automatizaciones, análisis de datos o GUIs. Si el proyecto ya tiene sus propias convenciones (herramientas, estructura, estilo), **esas ganan**; esta guía es lo que aplicas cuando no las hay o para completarlas.

Contenido:

1. Versión y entorno
2. Estructura del proyecto
3. Herramientas de calidad
4. Estilo y legibilidad
5. Tipado
6. Modelado de datos
7. Errores y excepciones
8. Logging
9. Configuración y secretos
10. Archivos, rutas y codificación
11. Tests con pytest
12. Concurrencia y asincronía
13. Seguridad
14. Rendimiento
15. CLIs, APIs y GUIs
16. Trampas clásicas de Python
17. Checklist final

---

## 1. Versión y entorno

- Usa una versión de Python con soporte vigente (3.11 o superior en proyectos nuevos, salvo que el entorno imponga otra). Decláralo en `pyproject.toml` (`requires-python = ">=3.11"`).
- **Siempre en un entorno virtual**, nunca instalando paquetes en el Python del sistema. Prefiere `uv` si está disponible (rápido y con lockfile); si no, `python -m venv .venv` y `pip`.
- Dependencias declaradas en `pyproject.toml` y **versiones fijadas** en un lockfile (`uv.lock`, `poetry.lock` o un `requirements.txt` generado con `pip-compile`/`uv pip compile`). Un proyecto que funciona "en mi máquina" pero instala versiones distintas en otra es un proyecto roto.
- Separa dependencias de desarrollo (pytest, ruff, mypy) de las de ejecución.
- Antes de agregar una dependencia, comprueba que existe en PyPI con ese nombre exacto, que está mantenida y que la biblioteca estándar no lo resuelve ya.
- Antes de ejecutar nada, comprueba qué intérprete estás usando (`python --version`, `which python` / `where python`); muchos errores "misteriosos" son el intérprete o el entorno equivocado.

---

## 2. Estructura del proyecto

Para algo más que un script suelto, usa el layout `src/`:

```
mi-proyecto/
├── pyproject.toml
├── README.md
├── .env.example
├── .gitignore
├── src/
│   └── mi_paquete/
│       ├── __init__.py
│       ├── __main__.py      # permite `python -m mi_paquete`
│       ├── config.py        # carga de configuración
│       ├── modelos.py
│       ├── servicios/
│       └── cli.py
└── tests/
    ├── conftest.py
    └── test_servicios.py
```

- El layout `src/` obliga a instalar el paquete (`pip install -e .` o `uv sync`) para probarlo, lo que evita que los tests pasen por importar archivos sueltos que en producción no estarían.
- Separa la lógica pura (fácil de probar) de la entrada/salida (red, disco, base de datos, interfaz). La lógica no debería saber de dónde vienen los datos.
- Un script suelto también merece estructura mínima: funciones, un `main()` y el guard `if __name__ == "__main__": main()`. Nada de lógica suelta a nivel de módulo que se ejecuta al importar.

---

## 3. Herramientas de calidad

| Herramienta | Para qué | Comando típico |
|---|---|---|
| **ruff** | Linter y formateador (reemplaza flake8, isort, black) | `ruff check .` y `ruff format .` |
| **mypy** o **pyright** | Verificación de tipos | `mypy src` |
| **pytest** | Tests | `pytest -q` |
| **pytest-cov** | Cobertura | `pytest --cov=mi_paquete` |
| **pip-audit** | Vulnerabilidades en dependencias | `pip-audit` |

Configúralas en `pyproject.toml` para que todos usen las mismas reglas. Antes de dar algo por terminado, las cuatro primeras pasan sin errores nuevos.

Configuración razonable de partida:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "SIM", "RUF", "S", "PTH"]

[tool.mypy]
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"
```

---

## 4. Estilo y legibilidad

- Sigue PEP 8 (el formateador lo resuelve casi todo). `snake_case` para funciones y variables, `PascalCase` para clases, `MAYUSCULAS` para constantes.
- Nombres que dicen qué contienen: `pedidos_pendientes`, no `lista2`, `data` ni `tmp`.
- Funciones cortas con una responsabilidad. Si una función necesita comentarios de sección ("# paso 1", "# paso 2"), probablemente son varias funciones.
- Retornos tempranos en lugar de `if` anidados.
- Docstrings en funciones públicas: qué hace, qué recibe, qué devuelve y qué excepciones lanza (estilo Google o NumPy, el que use el proyecto).
- Comprensiones de listas para transformaciones simples; un bucle normal cuando la lógica tiene más de una condición.
- f-strings para formatear texto (excepto en logging, ver sección 8).
- `enumerate()` en lugar de `range(len(...))`; `zip(..., strict=True)` cuando las secuencias deben tener el mismo largo.

---

## 5. Tipado

- **Anota los tipos de todas las funciones públicas** (parámetros y retorno). Los tipos son documentación que se verifica sola y atrapan muchos bugs antes de ejecutar.
- Usa la sintaxis moderna: `list[str]`, `dict[str, int]`, `str | None` (no `List`, `Optional`).
- Evita `Any`; si de verdad no sabes el tipo, usa `object` y estrecha con `isinstance`.
- `Protocol` para interfaces por comportamiento, `TypedDict` para diccionarios con forma fija, `Literal` para valores permitidos, `Enum` para conjuntos cerrados.
- No silencies errores del verificador con `# type: ignore` sin un comentario que explique por qué es correcto.

---

## 6. Modelado de datos

- No pases diccionarios sueltos por todo el programa: define la forma de los datos.
- `@dataclass(frozen=True, slots=True)` para datos internos simples e inmutables.
- **Pydantic** (o similar) para datos que vienen de fuera (JSON de una API, formularios, archivos de configuración): valida y convierte en el borde del sistema y, a partir de ahí, trabaja con objetos tipados y confiables.
- `Enum` en lugar de strings mágicos (`Estado.PAGADO`, no `"pagado"` repetido en diez sitios).
- `Decimal` para dinero, nunca `float` (`0.1 + 0.2 != 0.3`).
- Fechas siempre con zona horaria (`datetime.now(tz=UTC)`); guarda en UTC y convierte solo para mostrar.

---

## 7. Errores y excepciones

- Captura **la excepción concreta** que esperas y sabes manejar: `except FileNotFoundError:`, nunca `except:` a secas ni `except Exception: pass`.
- Si capturas para agregar contexto, relanza encadenando: `raise ErrorConfig("falta DB_URL") from exc`.
- Crea una jerarquía de excepciones propia en proyectos medianos (`class ErrorApp(Exception)`, `class ErrorValidacion(ErrorApp)`).
- Falla pronto y con mensajes claros: valida las entradas al principio de la función.
- Usa `with` para todo recurso que deba cerrarse (archivos, conexiones, locks).
- En el punto de entrada (`main`, handler de la API), captura lo inesperado, regístralo con traza completa (`logger.exception`) y muestra al usuario un mensaje entendible; nunca una traza cruda.
- `assert` sirve para invariantes internas y tests, **no** para validar entradas: se desactiva con `python -O`.

---

## 8. Logging

- Usa `logging`, no `print`, en todo lo que no sea la salida intencional de un CLI. Un logger por módulo: `logger = logging.getLogger(__name__)`.
- Configura el logging una sola vez, en el punto de entrada, no en los módulos.
- Pasa los argumentos al logger en lugar de formatear: `logger.info("Procesados %d pedidos", total)`; así no se formatea si el nivel está desactivado.
- Niveles con sentido: `DEBUG` detalle para depurar, `INFO` hitos normales, `WARNING` algo raro pero recuperable, `ERROR` una operación falló, `CRITICAL` la aplicación no puede seguir.
- Nunca registres contraseñas, tokens ni datos personales completos.

---

## 9. Configuración y secretos

- Nada configurable escrito en el código: URLs, rutas, credenciales, puertos, límites y flags salen de variables de entorno o de un archivo de configuración.
- Centraliza la carga en un módulo (`config.py`), por ejemplo con `pydantic-settings`, que valida al arrancar y falla con un mensaje claro si falta algo. Es mejor que el programa no arranque a que falle a mitad de un proceso.
- `.env` para desarrollo local (en `.gitignore`) y `.env.example` con todas las claves y valores ficticios.
- Valores por defecto seguros: modo depuración apagado por defecto, no al revés.

---

## 10. Archivos, rutas y codificación

- `pathlib.Path` en lugar de concatenar strings con `/` o `\\`; funciona igual en Windows, macOS y Linux.
- Rutas relativas al proyecto calculadas desde el archivo (`Path(__file__).resolve().parent`), no desde el directorio actual, que cambia según desde dónde se ejecute.
- **Especifica siempre la codificación:** `open(ruta, encoding="utf-8")`. En Windows la codificación por defecto no es UTF-8 y es una fuente clásica de errores.
- Archivos grandes: procesa por líneas o por bloques, no con `.read()` completo.
- Escritura segura: escribe en un archivo temporal y renómbralo al final (`Path.replace`) para no dejar archivos a medio escribir si el proceso se interrumpe.
- CSV con el módulo `csv` (o pandas), nunca con `split(",")`; JSON con `json`, nunca armando strings a mano.

---

## 11. Tests con pytest

- Tests en `tests/`, archivos `test_*.py`, nombres que describen el comportamiento: `test_rechaza_pedido_sin_productos`.
- Estructura Preparar / Actuar / Verificar, un comportamiento por test.
- Fixtures en `conftest.py` para preparar datos y recursos; `tmp_path` para archivos temporales; `monkeypatch` para variables de entorno.
- `@pytest.mark.parametrize` para probar muchos casos (incluidos los límites: vacío, `None`, negativo, muy grande, Unicode) sin duplicar código.
- Prueba que se lanzan los errores esperados: `with pytest.raises(ErrorValidacion, match="cantidad")`.
- **Mockea solo los bordes** (red, reloj, servicios externos), no tu propia lógica: un test que solo verifica que se llamó un mock no prueba nada real.
- Tests deterministas: nada de depender del orden, de la hora actual sin fijarla, de la red real ni de `time.sleep` arbitrarios (espera la condición, ver `depuracion/GUIA.md`).
- Para un bug: primero el test que lo reproduce y falla, después el arreglo.

---

## 12. Concurrencia y asincronía

- Elige según el tipo de trabajo:
  - **I/O (red, disco, muchas peticiones):** `asyncio` o `concurrent.futures.ThreadPoolExecutor`.
  - **CPU (cálculo pesado):** `ProcessPoolExecutor` / `multiprocessing` (los hilos no aceleran CPU por el GIL en la mayoría de las versiones).
- En código `async`, nunca llames funciones bloqueantes (`requests`, `time.sleep`, lectura de archivos grandes) directamente: usa librerías async (`httpx`, `aiofiles`) o `asyncio.to_thread`.
- Toda llamada de red lleva **timeout** explícito. Sin timeout, un servidor colgado cuelga tu programa para siempre.
- Reintentos solo para errores transitorios, con espera exponencial y un máximo (por ejemplo con `tenacity`).
- Protege el estado compartido entre hilos con locks o, mejor, evita compartirlo (colas).

---

## 13. Seguridad

- **Nunca** `eval()`/`exec()` con datos externos.
- `subprocess.run([...], check=True)` con lista de argumentos; nunca `shell=True` con strings que incluyen entrada del usuario.
- SQL siempre parametrizado (`cursor.execute("... WHERE id = ?", (id_,))`) o con un ORM; nunca f-strings en consultas.
- No uses `pickle` ni `yaml.load` (usa `yaml.safe_load`) con datos no confiables: pueden ejecutar código.
- Valida rutas que vienen del usuario para evitar salir del directorio permitido (`../../etc/passwd`).
- Usa `secrets` (no `random`) para tokens y contraseñas; `hashlib`/`bcrypt`/`argon2` según corresponda para contraseñas, nunca guardarlas en texto plano.
- Peticiones HTTP con verificación TLS activada (no `verify=False`).
- Ejecuta `pip-audit` (o equivalente) en proyectos con dependencias.

---

## 14. Rendimiento

- Mide antes de optimizar: `cProfile`, `timeit` o `py-spy`. La intuición sobre dónde está la lentitud suele fallar.
- Estructuras adecuadas: `set`/`dict` para búsquedas (O(1)) en vez de buscar en listas; `collections.deque` para colas; `Counter`, `defaultdict`.
- Generadores para procesar flujos grandes sin cargarlos en memoria.
- Evita consultas a base de datos o peticiones HTTP dentro de bucles; agrúpalas.
- En datos tabulares grandes usa operaciones vectorizadas (pandas/polars/numpy), no bucles fila a fila.
- `functools.cache`/`lru_cache` para resultados puros que se repiten.

---

## 15. CLIs, APIs y GUIs

**CLI:** `argparse` (estándar) o `typer`/`click`. Con `--help` útil, códigos de salida correctos (0 éxito, distinto de 0 error), errores a `stderr`, salida de datos a `stdout`, y opción `--verbose`. Si una operación es destructiva, pide confirmación o ofrece `--dry-run`.

**API (FastAPI, Flask, Django):** valida la entrada con modelos (Pydantic/serializers), devuelve códigos HTTP correctos y errores con estructura consistente, separa rutas de lógica de negocio, maneja migraciones de base de datos con la herramienta del framework (Alembic, migraciones de Django) y documenta los endpoints (FastAPI lo hace solo con OpenAPI).

**GUI (Tkinter, PySide/PyQt):** nunca bloquees el hilo de la interfaz (usa hilos o `QThread` y actualiza la interfaz solo desde el hilo principal: `after()` en Tkinter, señales en Qt); layouts que se adaptan (`grid`/`pack` con pesos, `QLayout`), nunca `place` con coordenadas fijas para toda la ventana. Aplica `diseno/GUIA.md`.

**Análisis de datos y notebooks:** la lógica reutilizable va en módulos `.py`, no solo en el notebook; fija semillas aleatorias; nunca modifiques los datos originales, escribe resultados en otro archivo.

---

## 16. Trampas clásicas de Python

| Trampa | Problema | Correcto |
|---|---|---|
| `def f(x, lista=[])` | La lista por defecto se comparte entre llamadas | `def f(x, lista=None)` y crear la lista dentro si es `None` |
| `except:` / `except Exception: pass` | Oculta errores reales, incluso `KeyboardInterrupt` con el primero | Capturar la excepción concreta |
| `if x == None` | Puede fallar con objetos que redefinen `==` | `if x is None` |
| `x is 5`, `s is "hola"` | `is` compara identidad, no valor | `==` |
| Lambdas en bucle `[lambda: i for i in range(3)]` | Todas capturan el último `i` | `lambda i=i: i` |
| Modificar una lista mientras se itera | Se saltan elementos | Iterar sobre una copia o construir una nueva |
| `open()` sin `encoding` | Rompe con acentos en Windows | `encoding="utf-8"` |
| `float` para dinero | Errores de redondeo | `Decimal` |
| `datetime.now()` sin zona | Errores con horarios y servidores en otra zona | `datetime.now(tz=UTC)` |
| `from modulo import *` | Contamina el espacio de nombres y oculta orígenes | Importar lo que se usa |
| Nombrar un archivo `random.py`, `json.py`, `email.py` | Tapa el módulo estándar | Nombres propios del proyecto |
| Imports circulares | Errores al importar | Reorganizar dependencias o mover el import |
| `requests.get(url)` sin timeout | Cuelgue indefinido | `timeout=10` |

---

## 17. Checklist final de Python

- [ ] Entorno virtual, dependencias declaradas y versiones fijadas.
- [ ] `ruff check` y `ruff format --check` sin errores nuevos.
- [ ] `mypy`/`pyright` sin errores nuevos; funciones públicas tipadas.
- [ ] `pytest` pasa completo; hay tests para la lógica nueva y para los casos límite.
- [ ] Nada configurable ni secreto en el código; `.env.example` actualizado.
- [ ] Sin `except` vacíos, sin `print` de depuración, sin `eval`/`shell=True` con datos externos.
- [ ] Archivos abiertos con `encoding` y `with`; rutas con `pathlib`.
- [ ] Timeouts en toda llamada de red.
- [ ] Ejecuté el programa de verdad (no solo los tests) con un caso normal y uno de error.
- [ ] README con cómo instalar, configurar y ejecutar.
