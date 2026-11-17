#!/usr/bin/env python3
"""Detector de código estático, simulado o incompleto.

Busca en un proyecto los patrones típicos de algo que "parece" funcionar pero
no funciona: enlaces muertos, handlers vacíos, datos mock en código de
producción, TODOs, Lorem ipsum, URLs locales, posibles secretos, errores
silenciados, etc. Ver anti-estatico/GUIA.md.

Uso:
    python detectar_estatico.py [RUTAS...] [--json] [--todo] [--max N]

    RUTAS   Carpetas o archivos a revisar (por defecto, la carpeta actual).
    --json  Salida en JSON.
    --todo  Incluye también los hallazgos de severidad baja.
    --max   Máximo de hallazgos a mostrar por regla (por defecto 50).

Para ignorar una línea justificada, agrega en ella el comentario:
    anti-estatico: ignorar

Código de salida: 1 si hay hallazgos de severidad alta, 0 en otro caso,
2 si los argumentos son inválidos.

Solo usa la biblioteca estándar.
"""

from __future__ import annotations

import argparse
import bisect
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

DIRECTORIOS_EXCLUIDOS = {
    ".git", ".hg", ".svn", "node_modules", "bower_components", "dist", "build",
    "out", ".next", ".nuxt", ".svelte-kit", ".astro", ".turbo", ".cache",
    ".parcel-cache", "coverage", ".venv", "venv", "env", ".env", "__pycache__",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox", "site-packages",
    "vendor", "target", "bin", "obj", ".idea", ".vscode", ".gradle",
}

EXT_WEB = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".vue", ".svelte", ".astro"}
EXT_MARCADO = {".html", ".htm", ".php", ".erb", ".hbs", ".ejs", ".jinja", ".j2", ".twig"}
EXT_PY = {".py", ".pyw"}
EXT_OTROS = {".java", ".kt", ".cs", ".go", ".rb", ".rs", ".swift", ".dart", ".scala"}
EXT_ESTILO = {".css", ".scss", ".sass", ".less"}
EXT_CONFIG = {".yml", ".yaml", ".toml", ".ini", ".cfg"}
EXT_CODIGO = EXT_WEB | EXT_MARCADO | EXT_PY | EXT_OTROS
EXT_TODAS = EXT_CODIGO | EXT_ESTILO | EXT_CONFIG

ARCHIVOS_EXCLUIDOS = re.compile(
    r"(\.min\.(js|css)$|\.map$|package-lock\.json$|yarn\.lock$|pnpm-lock\.yaml$"
    r"|poetry\.lock$|uv\.lock$|\.d\.ts$)",
    re.IGNORECASE,
)

PATRON_TEST = re.compile(
    r"(^|[\\/])(tests?|__tests__|__mocks__|spec|specs|fixtures?|mocks?|seeds?|stories"
    r"|e2e|cypress|playwright)([\\/]|$)"
    r"|(^|[\\/])test_[^\\/]*\.py$|_test\.(py|go)$|\.(test|spec|stories|e2e)\.[a-z]+$"
    r"|conftest\.py$",
    re.IGNORECASE,
)

PATRON_CONFIG = re.compile(
    r"(config|compose|settings|\.env|setup|proxy|vite|webpack|next\.config|nuxt\.config"
    r"|playwright|jest|vitest|karma)[^\\/]*$",
    re.IGNORECASE,
)

MARCA_IGNORAR = "anti-estatico: ignorar"
TAMANO_MAXIMO = 1_500_000  # bytes

PALABRAS_PLACEHOLDER_SECRETO = re.compile(
    r"(your|tu_|xxx|changeme|cambiar|example|ejemplo|placeholder|dummy|<|\$\{|\{\{|process\.env"
    r"|os\.environ|import\.meta|getenv|\*\*\*)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Regla:
    id: str
    severidad: str  # "alta" | "media" | "baja"
    patron: re.Pattern[str]
    descripcion: str
    sugerencia: str
    extensiones: frozenset[str]
    omitir_en_tests: bool = False
    severidad_en_config: str | None = None


def _r(patron: str, flags: int = 0) -> re.Pattern[str]:
    return re.compile(patron, flags)


REGLAS: list[Regla] = [
    Regla(
        "enlace-muerto", "alta",
        _r(r"""href\s*=\s*\{?\s*["'](#|javascript:\s*void\(0\);?)["']"""),
        "Enlace que no lleva a ningún lado.",
        "Enlazar a una ruta real o usar <button> con una acción real.",
        frozenset(EXT_WEB | EXT_MARCADO),
    ),
    Regla(
        "handler-vacio", "alta",
        _r(r"""on[A-Z]\w*\s*=\s*\{\s*\(\s*[\w,\s]*\)\s*=>\s*(\{\s*\}|null|undefined|void\s*0)\s*\}"""
           r"""|\bon[a-z]+\s*=\s*["']\s*["']|[@:]\s*(click|submit|change|input)\s*=\s*["']\s*["']"""),
        "Evento conectado a una función vacía: el elemento no hace nada.",
        "Implementar la acción real o quitar el elemento.",
        frozenset(EXT_WEB | EXT_MARCADO),
    ),
    Regla(
        "submit-falso", "alta",
        _r(r"""onSubmit\s*=\s*\{\s*\(?\s*(\w+)\s*\)?\s*=>\s*\{?\s*\1\.preventDefault\(\)\s*;?\s*\}?\s*\}"""),
        "Formulario que solo cancela el envío y no hace nada más.",
        "Validar, enviar los datos y mostrar el resultado real.",
        frozenset(EXT_WEB),
    ),
    Regla(
        "handler-solo-log", "media",
        _r(r"""on[A-Z]\w*\s*=\s*\{\s*\(\s*[\w,\s]*\)\s*=>\s*\{?\s*console\.log\("""),
        "Evento que solo escribe en consola.",
        "Implementar la acción real.",
        frozenset(EXT_WEB),
    ),
    Regla(
        "exito-simulado", "media",
        _r(r"""alert\(\s*["'`][^"'`]*(guardad|enviad|éxito|exito|success|saved|sent|creado|created)""",
           re.IGNORECASE),
        "Mensaje de éxito que podría mostrarse sin que la operación ocurra.",
        "Mostrar la confirmación solo tras la respuesta exitosa, y el error si falla.",
        frozenset(EXT_WEB | EXT_MARCADO),
    ),
    Regla(
        "no-implementado", "alta",
        _r(r"""raise\s+NotImplementedError|throw\s+new\s+Error\(\s*["'`][^"'`]*(not\s+implemented|no\s+implementad)"""
           r"""|todo!\(\)|unimplemented!\(\)""",
           re.IGNORECASE),
        "Funcionalidad sin implementar.",
        "Implementarla, o declararla como pendiente en el reporte si está fuera del alcance.",
        frozenset(EXT_CODIGO),
        omitir_en_tests=True,
    ),
    Regla(
        "retorno-fijo", "alta",
        _r(r"""return\s+(true|false|True|False|None|null|\[\]|\{\}|0|["'][^"']*["'])\s*;?\s*(//|#)[^\n]*"""
           r"""(mock|fake|falso|temp|todo|stub|placeholder|hardcod|por ahora|for now)""",
           re.IGNORECASE),
        "Valor de retorno fijo marcado como provisional.",
        "Implementar la lógica real o fallar de forma explícita.",
        frozenset(EXT_CODIGO),
        omitir_en_tests=True,
    ),
    Regla(
        "mock-en-produccion", "alta",
        _r(r"""\b(const|let|var)\s+(mock|fake|dummy|fakeData|sample|hardcoded)\w*\s*(:\s*[^=]+)?=\s*[\[{]"""
           r"""|^\s*(MOCK|FAKE|DUMMY|SAMPLE|mock|fake|dummy|sample)_?\w*\s*(:\s*[^=]+)?=\s*[\[{]""",
           re.IGNORECASE | re.MULTILINE),
        "Datos de ejemplo definidos dentro del código de producción.",
        "Leer los datos de la fuente real (API, base de datos, estado). Si es una maqueta pedida, moverlos a mocks/ o seed/.",
        frozenset(EXT_CODIGO),
        omitir_en_tests=True,
    ),
    Regla(
        "lorem-ipsum", "alta",
        _r(r"lorem\s+ipsum|dolor\s+sit\s+amet", re.IGNORECASE),
        "Texto de relleno.",
        "Usar contenido real o realista del tema.",
        frozenset(EXT_TODAS),
        omitir_en_tests=True,
    ),
    Regla(
        "imagen-relleno", "media",
        _r(r"(via\.placeholder\.com|placehold\.(co|it)|picsum\.photos|dummyimage\.com|placekitten\.com"
           r"|loremflickr\.com|fakeimg\.pl|source\.unsplash\.com/random)", re.IGNORECASE),
        "Imagen de relleno de un servicio externo.",
        "Usar imágenes reales del proyecto o declarar cuáles debe reemplazar el usuario.",
        frozenset(EXT_TODAS),
        omitir_en_tests=True,
    ),
    Regla(
        "texto-relleno", "baja",
        _r(r"\b(usuario\s+ejemplo|john\s+doe|jane\s+doe|producto\s+\d+|item\s+\d+|test\s+user"
           r"|foo\s*bar|asdf+)\b", re.IGNORECASE),
        "Texto que parece de relleno.",
        "Comprobar que no sea contenido fijo que debería venir de datos.",
        frozenset(EXT_WEB | EXT_MARCADO),
        omitir_en_tests=True,
    ),
    Regla(
        "url-local", "media",
        _r(r"https?://(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d+)?", re.IGNORECASE),
        "URL local escrita en el código.",
        "Leerla de una variable de entorno o configuración.",
        frozenset(EXT_TODAS),
        omitir_en_tests=True,
        severidad_en_config="baja",
    ),
    Regla(
        "posible-secreto", "alta",
        _r(r"""\b\w*(api[_-]?key|secret|password|passwd|contrase(ñ|n)a|token|access[_-]?key|private[_-]?key|client[_-]?secret)\w*"""
           r"""["']?\s*[:=]\s*["'][^"'\s]{8,}["']"""
           r"""|\bsk-[A-Za-z0-9_-]{20,}|\bAKIA[0-9A-Z]{16}\b|\bgh[pousr]_[A-Za-z0-9]{30,}"""
           r"""|\bxox[abprs]-[A-Za-z0-9-]{10,}|-----BEGIN\s+(RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE\s+KEY-----""",
           re.IGNORECASE),
        "Posible secreto escrito en el código.",
        "Moverlo a una variable de entorno, quitarlo del historial y rotarlo si ya se publicó.",
        frozenset(EXT_TODAS),
    ),
    Regla(
        "catch-vacio", "alta",
        _r(r"""catch\s*(\([^)]*\))?\s*\{\s*\}|\.catch\(\s*\(?\s*\w*\s*\)?\s*=>\s*(\{\s*\}|null|undefined)\s*\)"""),
        "Error capturado y descartado en silencio.",
        "Manejar el error (mensaje, reintento, valor por defecto) o propagarlo.",
        frozenset(EXT_WEB | EXT_OTROS | {".php"}),
    ),
    Regla(
        "except-vacio", "alta",
        _r(r"""^[ \t]*except[^:\n]*:[ \t]*(#[^\n]*)?\n[ \t]*(pass|\.\.\.)[ \t]*(#[^\n]*)?$""", re.MULTILINE),
        "Excepción capturada y descartada en silencio.",
        "Capturar la excepción concreta y manejarla, o dejar que se propague.",
        frozenset(EXT_PY),
    ),
    Regla(
        "except-generico", "media",
        _r(r"""^[ \t]*except[ \t]*:""", re.MULTILINE),
        "`except:` sin tipo captura todo, incluso Ctrl+C.",
        "Capturar la excepción concreta.",
        frozenset(EXT_PY),
    ),
    Regla(
        "funcion-vacia", "media",
        _r(r"""^[ \t]*def\s+\w+\([^)]*\)[^:\n]*:[ \t]*\n(?:[ \t]*(?:\"\"\"[^\n]*\"\"\"|#[^\n]*)\n)*[ \t]*pass[ \t]*$""",
           re.MULTILINE),
        "Función con cuerpo vacío (`pass`).",
        "Implementarla o, si es abstracta, usar `abc.abstractmethod` o `Protocol`.",
        frozenset(EXT_PY),
        omitir_en_tests=True,
    ),
    Regla(
        "todo-pendiente", "media",
        _r(r"""\b(TODO|FIXME|XXX|HACK)\b"""),
        "Trabajo pendiente marcado en el código.",
        "Implementarlo si está en un flujo real, o declararlo en el reporte.",
        frozenset(EXT_TODAS),
    ),
    Regla(
        "depuracion-olvidada", "alta",
        _r(r"""^\s*debugger\s*;?\s*$|\bbreakpoint\(\)|pdb\.set_trace\(\)|ipdb\.set_trace\(\)""", re.MULTILINE),
        "Punto de depuración olvidado.",
        "Quitarlo.",
        frozenset(EXT_CODIGO),
    ),
    Regla(
        "silenciador", "media",
        _r(r"""@ts-ignore|@ts-nocheck|eslint-disable|#\s*type:\s*ignore|#\s*noqa|#\s*pragma:\s*no\s*cover"""
           r"""|@SuppressWarnings|#pragma\s+warning\s+disable"""),
        "Error o advertencia silenciada.",
        "Entender y corregir la causa; si es correcto, explicar por qué en el mismo comentario.",
        frozenset(EXT_CODIGO),
    ),
    Regla(
        "tipo-any", "baja",
        _r(r""":\s*any\b|\bas\s+any\b|<any>"""),
        "Tipo `any` que desactiva la verificación de tipos.",
        "Usar el tipo real o `unknown` y estrecharlo.",
        frozenset({".ts", ".tsx", ".vue", ".svelte", ".astro"}),
    ),
    Regla(
        "console-log", "baja",
        _r(r"""\bconsole\.(log|debug)\("""),
        "Log de depuración en código de producción.",
        "Quitarlo o usar el sistema de logging del proyecto.",
        frozenset(EXT_WEB),
        omitir_en_tests=True,
    ),
    Regla(
        "espera-arbitraria", "baja",
        _r(r"""waitForTimeout\(\s*\d+|cy\.wait\(\s*\d+|time\.sleep\(\s*\d"""),
        "Espera fija: frágil en tests y lenta en producción.",
        "Esperar la condición real (elemento visible, respuesta recibida).",
        frozenset(EXT_CODIGO),
    ),
]

ORDEN_SEVERIDAD = {"alta": 0, "media": 1, "baja": 2}


@dataclass
class Hallazgo:
    regla: str
    severidad: str
    archivo: str
    linea: int
    fragmento: str
    descripcion: str
    sugerencia: str


def es_archivo_de_test(ruta: Path) -> bool:
    return bool(PATRON_TEST.search(ruta.as_posix()))


def es_archivo_de_config(ruta: Path) -> bool:
    return bool(PATRON_CONFIG.search(ruta.name)) or ruta.suffix.lower() in EXT_CONFIG


def recorrer(rutas: list[Path], propio: Path) -> list[Path]:
    archivos: list[Path] = []
    for ruta in rutas:
        if ruta.is_file():
            archivos.append(ruta)
            continue
        for candidato in ruta.rglob("*"):
            if any(parte in DIRECTORIOS_EXCLUIDOS for parte in candidato.relative_to(ruta).parts[:-1]):
                continue
            if not candidato.is_file():
                continue
            if candidato.suffix.lower() not in EXT_TODAS:
                continue
            if ARCHIVOS_EXCLUIDOS.search(candidato.name):
                continue
            archivos.append(candidato)
    unicos = {a.resolve(): a for a in archivos if a.resolve() != propio}
    return sorted(unicos.values())


def leer(ruta: Path) -> str | None:
    try:
        if ruta.stat().st_size > TAMANO_MAXIMO:
            return None
        datos = ruta.read_bytes()
    except OSError:
        return None
    if b"\x00" in datos[:4096]:
        return None
    return datos.decode("utf-8", errors="replace")


def secreto_es_placeholder(texto: str) -> bool:
    return bool(PALABRAS_PLACEHOLDER_SECRETO.search(texto))


def analizar_archivo(ruta: Path, base: Path, max_fragmento: int = 140) -> list[Hallazgo]:
    contenido = leer(ruta)
    if contenido is None:
        return []
    ext = ruta.suffix.lower()
    en_test = es_archivo_de_test(ruta)
    en_config = es_archivo_de_config(ruta)
    lineas = contenido.splitlines()
    inicios = [0]
    inicios.extend(i + 1 for i, c in enumerate(contenido) if c == "\n")

    try:
        nombre = ruta.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        nombre = ruta.as_posix()

    hallazgos: list[Hallazgo] = []
    vistos: set[tuple[str, int]] = set()
    for regla in REGLAS:
        if ext not in regla.extensiones:
            continue
        if regla.omitir_en_tests and en_test:
            continue
        for coincidencia in regla.patron.finditer(contenido):
            texto = coincidencia.group(0)
            # Si el patrón empieza con un salto de línea consumido, apuntar a la primera línea con texto.
            desplazamiento = len(texto) - len(texto.lstrip("\n"))
            numero = bisect.bisect_right(inicios, coincidencia.start() + desplazamiento)
            if (regla.id, numero) in vistos:
                continue
            linea = lineas[numero - 1] if 0 < numero <= len(lineas) else ""
            if MARCA_IGNORAR in linea:
                continue
            if regla.id == "posible-secreto" and secreto_es_placeholder(texto):
                continue
            severidad = regla.severidad
            if en_config and regla.severidad_en_config:
                severidad = regla.severidad_en_config
            fragmento = linea.strip()
            if len(fragmento) > max_fragmento:
                fragmento = fragmento[: max_fragmento - 1] + "…"
            if regla.id == "posible-secreto":
                fragmento = re.sub(r"""(["'])[^"']{4}([^"']*)\1""", r"\1****\1", fragmento)
            vistos.add((regla.id, numero))
            hallazgos.append(
                Hallazgo(regla.id, severidad, nombre, numero, fragmento, regla.descripcion, regla.sugerencia)
            )
    return hallazgos


def imprimir_texto(hallazgos: list[Hallazgo], revisados: int, max_por_regla: int) -> None:
    if not hallazgos:
        print(f"Sin hallazgos en {revisados} archivos revisados.")
        print("Recuerda: el detector no reemplaza la prueba de uso real (anti-estatico/GUIA.md, sección 9).")
        return

    por_regla: dict[tuple[str, str], list[Hallazgo]] = {}
    for h in hallazgos:
        por_regla.setdefault((h.severidad, h.regla), []).append(h)

    reglas_ordenadas = sorted(
        por_regla.items(), key=lambda kv: (ORDEN_SEVERIDAD[kv[0][0]], kv[0][1])
    )
    for (_, regla_id), lista in reglas_ordenadas:
        primero = lista[0]
        print(f"\n[{primero.severidad.upper()}] {regla_id} ({len(lista)}): {primero.descripcion}")
        print(f"  Qué hacer: {primero.sugerencia}")
        for h in lista[:max_por_regla]:
            print(f"  - {h.archivo}:{h.linea}  {h.fragmento}")
        if len(lista) > max_por_regla:
            print(f"  ... y {len(lista) - max_por_regla} más")

    conteo = {s: sum(1 for h in hallazgos if h.severidad == s) for s in ORDEN_SEVERIDAD}
    print(
        f"\nResumen: {len(hallazgos)} hallazgos en {revisados} archivos "
        f"(alta: {conteo['alta']}, media: {conteo['media']}, baja: {conteo['baja']})."
    )
    print("Cada hallazgo se resuelve o se justifica en el reporte. "
          f"Para ignorar una línea justificada, agrega '{MARCA_IGNORAR}'.")


def main(argv: list[str] | None = None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]  # Windows usa cp1252 por defecto
        except (AttributeError, ValueError):
            pass

    parser = argparse.ArgumentParser(
        description="Detecta código estático, simulado o incompleto (ver anti-estatico/GUIA.md)."
    )
    parser.add_argument("rutas", nargs="*", default=["."], help="Carpetas o archivos a revisar.")
    parser.add_argument("--json", action="store_true", help="Salida en JSON.")
    parser.add_argument("--todo", action="store_true", help="Incluir hallazgos de severidad baja.")
    parser.add_argument("--max", type=int, default=50, help="Máximo de hallazgos por regla a mostrar.")
    args = parser.parse_args(argv)

    rutas = [Path(r) for r in args.rutas]
    inexistentes = [str(r) for r in rutas if not r.exists()]
    if inexistentes:
        print(f"No existe: {', '.join(inexistentes)}", file=sys.stderr)
        return 2

    base = rutas[0] if len(rutas) == 1 and rutas[0].is_dir() else Path.cwd()
    archivos = recorrer(rutas, Path(__file__).resolve())

    hallazgos: list[Hallazgo] = []
    for archivo in archivos:
        hallazgos.extend(analizar_archivo(archivo, base))
    if not args.todo:
        hallazgos = [h for h in hallazgos if h.severidad != "baja"]
    hallazgos.sort(key=lambda h: (ORDEN_SEVERIDAD[h.severidad], h.archivo, h.linea))

    if args.json:
        print(json.dumps(
            {"archivos_revisados": len(archivos), "hallazgos": [asdict(h) for h in hallazgos]},
            ensure_ascii=False, indent=2,
        ))
    else:
        imprimir_texto(hallazgos, len(archivos), args.max)

    return 1 if any(h.severidad == "alta" for h in hallazgos) else 0


if __name__ == "__main__":
    sys.exit(main())
