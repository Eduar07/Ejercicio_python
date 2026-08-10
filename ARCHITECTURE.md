# ARCHITECTURE.md — Arquitectura Hexagonal de Metricas

> **Estado:** ✅ Implementado. Ya no es una propuesta: los archivos viven físicamente en esta estructura.
> No se modificó ni una línea de lógica de negocio, ni un valor, ni un nombre de función. Los únicos
> cambios de código fueron las líneas de `import` (porque los archivos cambiaron de carpeta) y la
> separación de `config.py` en dos archivos (ver sección 3, era necesario para que el dominio no
> dependiera de infraestructura — antes era una violación real de la regla hexagonal).

---

## 1. Estructura de carpetas actual

```
Metricas/
├── main.py                     # Composition root / punto de entrada (vacío, pendiente)
├── __init__.py
│
├── domain/                     # El corazón del negocio. No importa nada de fuera del proyecto
│   ├── __init__.py             # salvo la librería estándar de Python.
│   ├── models.py                 → EmployeeMetric, WeekData, LogEntry, MasterEmployee
│   ├── constants.py              → GOALS, DEPARTMENT, HOURS_PER_DAY_THRESHOLD, PASSIVE_HOURS_THRESHOLD
│   ├── business_rules.py         → normalize_name, calculate_productive_color,
│   │                                calculate_passive_status, detect_cross_month,
│   │                                match_employess, apply_business_rules
│   └── errors.py                 → ATError, ERROR_MESSAGES
│
├── application/                 # Casos de uso / orquestación (aún vacía, ver sección 5)
│   └── __init__.py
│
├── adapters/                    # Implementaciones concretas que hablan con el mundo exterior
│   ├── __init__.py
│   ├── excel_reader.py           → lee .xlsx con openpyxl y arma EmployeeMetric
│   ├── excel_write.py            → (vacío) va a escribir el Excel de salida
│   ├── storage.py                → localiza/valida carpetas y archivos en disco
│   └── logger.py                 → (vacío) va a registrar el LogEntry en algún lado
│
├── infrastructure/               # Configuración técnica transversal
│   ├── __init__.py
│   └── config.py                  → PATHS, SHEET_NAME, DATE_FORMAT, WEEKLY_COLUMNS,
│                                     COLORS, STATUSES, HEADER_ROW, START_ROW
│
└── data/                         # Carpetas de datos reales (no es código)
    ├── Input/
    ├── Output/
    ├── Logs/
    └── Parametric_Files/
```

---

## 2. Qué se movió y a dónde (tabla de auditoría)

| Archivo original | Carpeta nueva | ¿Cambió algo dentro? |
|---|---|---|
| `models.py` | `domain/models.py` | No, idéntico byte a byte |
| `errors.py` | `domain/errors.py` | No, idéntico byte a byte |
| `business_rules.py` | `domain/business_rules.py` | Solo las 2 líneas de `import` |
| `config.py` (parte de negocio) | `domain/constants.py` **(archivo nuevo)** | Se extrajeron `GOALS`, `DEPARTMENT`, `HOURS_PER_DAY_THRESHOLD`, `PASSIVE_HOURS_THRESHOLD` con sus mismos valores |
| `config.py` (parte técnica) | `infrastructure/config.py` | Solo se quitaron las 4 constantes de negocio; `PATHS`, `SHEET_NAME`, `DATE_FORMAT`, `WEEKLY_COLUMNS`, `COLORS`, `STATUSES`, `HEADER_ROW`, `START_ROW` quedan tal cual |
| `excel_reader.py` | `adapters/excel_reader.py` | Solo las líneas de `import` |
| `excel_write.py` | `adapters/excel_write.py` | No, seguía vacío |
| `storage.py` | `adapters/storage.py` | Solo las 2 líneas de `import` |
| `logger.py` | `adapters/logger.py` | No, seguía vacío |
| `main.py` | se queda en la raíz | No, seguía vacío |

---

## 3. El único ajuste "de fondo": separar `config.py`

El documento anterior (la propuesta) ya había detectado este problema y no se atrevía a tocarlo sin permiso. Ahora sí se resolvió, porque es indispensable para que la arquitectura hexagonal sea real y no solo de nombre:

`business_rules.py` (que es **dominio**, el círculo más interno) necesitaba `HOURS_PER_DAY_THRESHOLD` y `PASSIVE_HOURS_THRESHOLD`, que vivían en `config.py`. Si `config.py` se movía completo a `infrastructure/` (el círculo más externo), el dominio hubiera terminado dependiendo de infraestructura — literalmente lo contrario de lo que dice la arquitectura hexagonal (las flechas de dependencia solo pueden apuntar hacia adentro).

**Solución aplicada:** se partió `config.py` en dos, sin tocar ni un valor:
- Lo que es **regla de negocio** (`GOALS`, `DEPARTMENT`, `HOURS_PER_DAY_THRESHOLD`, `PASSIVE_HOURS_THRESHOLD`) → `domain/constants.py`.
- Lo que es **detalle técnico** (rutas de carpetas, nombre de la hoja de Excel, formato de fecha, columnas esperadas, colores hex, códigos de estado, filas de encabezado) → `infrastructure/config.py`.

Resultado: `domain/business_rules.py` ahora importa de `domain/constants.py` (dominio importando de dominio, válido) en vez de importar de infraestructura. La regla hexagonal ya se cumple sin excepciones.

### Bono: el cálculo de `PROJECT_ROOT` quedó bien solo
```python
PROJECT_ROOT = Path(__file__).parent.parent
```
Esta línea sube dos niveles desde donde vive el archivo. Antes, con `config.py` en la raíz, subía a un nivel *por encima* de `Metricas/` (mal). Ahora que `config.py` vive en `infrastructure/config.py` (un nivel de profundidad respecto a la raíz), subir dos niveles aterriza exactamente en `Metricas/` — que es donde vive `data/`. Se verificó en caliente:

```
PROJECT_ROOT: /home/eduar/Metricas
input path  : /home/eduar/Metricas/data/Input
```

No se tocó esa línea de código; el movimiento de carpeta fue lo que la corrigió.

---

## 4. Reglas de dependencia (verificadas, no solo declaradas)

```
main.py (composition root)
   │
   ├──> adapters/ ──────┐
   ├──> infrastructure/ ┤
   └──> application/ ───┼──> domain/
                         │
adapters/ ───────────────┼──> domain/  +  infrastructure/
infrastructure/ ─────────┘   (config.py no depende de nada del proyecto)
domain/ ──────────────────────> (nada del proyecto; solo librería estándar)
```

| Archivo | Importa de | ¿Cumple la regla hexagonal? |
|---|---|---|
| `domain/business_rules.py` | `domain.models`, `domain.constants` | ✅ Sí |
| `domain/models.py`, `domain/errors.py` | nada del proyecto | ✅ Sí |
| `adapters/excel_reader.py` | `domain.models`, `domain.errors`, `infrastructure.config` | ✅ Sí |
| `adapters/storage.py` | `domain.errors`, `infrastructure.config` | ✅ Sí |
| `infrastructure/config.py` | nada del proyecto | ✅ Sí |

Cero violaciones.

---

## 5. Lo que queda pendiente (a propósito, no se inventó nada)

- **`application/`** está vacía. No había ninguna orquestación de casos de uso en el código original
  (`main.py` estaba vacío), así que no se inventó lógica que no existía. Cuando definas el flujo real
  (ej. "leer Excel → matchear con maestro de empleados → aplicar reglas → escribir salida → loguear"),
  ese código va aquí, y `main.py` se limita a ensamblar los adaptadores concretos e invocarlo.
- **`adapters/excel_write.py`** y **`adapters/logger.py`** siguen vacíos, tal como estaban.
- **No se crearon "puertos"** (interfaces/`Protocol`) todavía. Es el siguiente paso natural cuando
  `application/` empiece a tener casos de uso reales: en vez de que la aplicación importe directamente
  `adapters.excel_reader`, dependería de una interfaz abstracta que `excel_reader` implementa — así el
  día de mañana puedes cambiar de Excel a una base de datos sin tocar la capa de aplicación. No se hizo
  ahora porque hubiera sido agregar una abstracción sin código real detrás; se deja documentado para
  cuando haga falta.

---

## 6. Explicación coloquial de todo el proyecto, paso a paso

Piensa en este proyecto como una fábrica que procesa reportes semanales de horas de empleados en Excel.
Así se organiza todo, en el orden en que ocurriría si ya estuviera terminado:

### Paso 1 — Alguien deja un Excel en la carpeta de entrada
Los archivos `.xlsx` con las horas de la semana se depositan en `data/Input/`. Esto es solo una carpeta
en disco, no código.

### Paso 2 — `adapters/storage.py` se fija qué hay para procesar
`list_input_files()` mira `data/Input/`, y si la carpeta no existe o está vacía, no se queda callado:
lanza un error claro (`ATError` con código `ERR001` o `ERR002`). También sabe dónde vive el Excel maestro
de empleados (`get_employees_path()`) y dónde debería escribirse el log de cada corrida
(`get_log_path(year)`). Es el "encargado de bodega": sabe dónde está todo, pero no sabe leer el
contenido de los Excel.

### Paso 3 — `adapters/excel_reader.py` abre el Excel y lo traduce a objetos Python
`read_excel(file_path)` abre el archivo con la librería `openpyxl`, busca la hoja llamada
`"Prod + Pass Hours All Dept"` (ese nombre vive en `infrastructure/config.py`, por si cambia algún día),
valida que las columnas sean exactamente las esperadas (`WEEKLY_COLUMNS`) y, si coinciden, arma una lista
de `EmployeeMetric` — un objeto por cada fila/empleado, con sus horas productivas, pasivas, meta, etc.
Si algo no cuadra (no abre el archivo, no existe la hoja, las columnas no coinciden), lanza un `ATError`
con el código correspondiente en vez de reventar con un error críptico de Python.

### Paso 4 — `domain/models.py` define la "forma" de los datos
Aquí no hay comportamiento, solo estructura: qué campos tiene un empleado (`EmployeeMetric`), qué es una
semana de datos (`WeekData`), qué es una entrada de log (`LogEntry`) y qué es un empleado del maestro
(`MasterEmployee`). Son los moldes que usa todo lo demás.

### Paso 5 — `domain/business_rules.py` aplica las reglas del negocio
Con los `EmployeeMetric` ya en mano, esta capa hace el trabajo pesado de negocio:
- `normalize_name` limpia nombres (mayúsculas, sin tildes) para poder comparar "José Pérez" con
  "JOSE PEREZ" sin que la tilde arruine la comparación.
- `match_employess` cruza la lista semanal contra el maestro de empleados por nombre normalizado, y se
  queda solo con los que sí están en el maestro.
- `calculate_productive_color` decide si un empleado se pinta verde o rojo según si sus horas
  productivas por día superan el umbral (`HOURS_PER_DAY_THRESHOLD`, 6.75 horas).
- `calculate_passive_status` decide lo mismo pero para horas pasivas (`PASSIVE_HOURS_THRESHOLD`, 1.25
  horas) — aquí la lógica es al revés: pasarse del umbral es rojo, no verde.
- `detect_cross_month` avisa si una semana cruza de un mes a otro (por ejemplo, empieza el 29 de enero y
  termina el 2 de febrero), algo importante para no mezclar reportes de meses distintos.
- `apply_business_rules` es el que junta las dos funciones de color y se las aplica a toda la lista de
  empleados de una sola pasada.

Estas son las reglas que le dan valor real al proyecto — por eso viven en el centro (`domain/`) y no
dependen de Excel, ni de rutas de carpetas, ni de nada externo. Si mañana el reporte viniera de un CSV en
vez de un Excel, estas reglas no cambiarían ni una línea.

### Paso 6 — `domain/constants.py` e `infrastructure/config.py` alimentan los umbrales y las rutas
`domain/constants.py` tiene los números que son decisiones de negocio (¿cuántas horas son "suficientes"?
¿cuál es la meta semanal?). `infrastructure/config.py` tiene los detalles técnicos que dependen de cómo
está armado el Excel hoy (nombre de la hoja, en qué fila empiezan los datos, qué columnas se esperan,
qué colores hex pintar). Si mañana cambian el nombre de la hoja de Excel, tocas un solo archivo técnico
y las reglas de negocio ni se enteran.

### Paso 7 (pendiente) — `domain/errors.py` estandariza cualquier error que ocurra
Cualquier cosa que salga mal en cualquier paso anterior —carpeta que no existe, Excel corrupto, columnas
que no coinciden— se reporta con el mismo formato: un código (`ERR001`, `ERR004`, etc.), un mensaje fijo
tomado de `ERROR_MESSAGES`, y un detalle específico de qué pasó. Así, sin importar en qué parte del
proceso reviente algo, el error que le llega a quien esté mirando el log tiene siempre la misma forma.

### Paso 8 (pendiente) — `adapters/excel_write.py` escribiría el resultado
Hoy está vacío, pero por su nombre y su lugar en la arquitectura, sería el encargado de tomar la lista
de `EmployeeMetric` ya con sus colores calculados y escribirla a un Excel de salida en `data/Output/`,
probablemente pintando cada celda según `COLORS["green"]` / `COLORS["red"]`.

### Paso 9 (pendiente) — `adapters/logger.py` dejaría constancia de la corrida
También vacío por ahora. Su trabajo sería tomar un `LogEntry` (cuántos registros se procesaron, si hubo
error, cuánto tardó) y guardarlo en `data/Logs/<año>/AT_Process_Log.xlsx`, la ruta que ya calcula
`storage.get_log_path(year)`.

### Paso 10 (pendiente) — `application/` y `main.py` amarran todo
Hoy `main.py` está vacío. El día que se escriba, la idea es que **no contenga lógica de negocio ni
detalles técnicos**, solo la orquestación: "llama a `storage` para saber qué archivos hay → llama a
`excel_reader` para leerlos → llama a `business_rules` para aplicar las reglas → llama a `excel_write`
para guardar el resultado → llama a `logger` para dejar constancia". Ese "llamar en orden" es
exactamente lo que en arquitectura hexagonal se llama un **caso de uso**, y por eso su lugar natural es
`application/`, no la raíz del proyecto ni el propio `main.py`.

---

## 7. Por qué esto ya es "hexagonal" de verdad y no solo carpetas con nombres bonitos

La prueba de fuego de la arquitectura hexagonal no es cómo se llaman las carpetas, es que **las flechas
de dependencia solo apunten hacia adentro**. Hoy, en este proyecto:

- `domain/` no le importa si los datos vienen de un Excel, de una API o de una base de datos — no
  importa nada de `adapters/` ni de `infrastructure/`.
- `adapters/` sí puede importar de `domain/` (necesita sus modelos y sus errores) y de
  `infrastructure/` (necesita las rutas y el nombre de la hoja) — eso es válido, va hacia adentro.
- El día de mañana que quieras cambiar de Excel a, por ejemplo, leer de una API REST, solo tocas
  `adapters/` (agregas un `api_reader.py` nuevo con la misma forma que `excel_reader.py`) y nada de
  `domain/` se entera ni se rompe. Esa es la garantía real de "escalable sin limitantes" que pediste.
