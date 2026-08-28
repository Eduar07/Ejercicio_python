# Metricas — Automatización de reportes semanales de horas (AT)

> Documentación técnico-pedagógica. Objetivo: poder reconstruir este proyecto desde cero,
> entendiendo **por qué** existe cada pieza y en qué orden depende una de otra — no solo qué
> hace cada archivo. Está escrita para leerse empezando por `main.py` y siguiendo la ejecución
> real, paso a paso, tal como corre el programa.

## Qué hace el proyecto

Cada semana, ActivTrak exporta dos archivos `.xlsx` a una carpeta de SharePoint (`Input/`):

- **"Productivity by User \<fecha\>.xlsx"** — horas productivas activas/pasivas por empleado,
  en segundos.
- **"User_Details_\<fecha\>.xlsx"** — días activos por empleado.

El proyecto:

1. Se autentica contra Microsoft Graph (usando credenciales que viven en Azure Key Vault).
2. Busca en `Input/` esos dos archivos de la misma semana.
3. Los lee y los combina en una sola lista de métricas por empleado (horas activas, pasivas,
   totales, días activos).
4. Cruza esa lista contra el maestro de empleados (`AT_Employees.xlsx`) — solo procesa
   empleados que existen ahí.
5. Aplica reglas de negocio: ¿cumplió el umbral de horas productivas por día? ¿se pasó del
   umbral de horas pasivas? → calcula una meta (`GOAL`) y un color (verde/amarillo/rojo) por
   cada indicador.
6. Escribe (o acumula, semana tras semana) un Excel de salida consolidado por mes en
   `Output/{año}/{mes}/AT_Metrics_{año}-{mes}.xlsx`.
7. Archiva los dos crudos en `Input/Processed/{año}/{mes}/` y los borra de `Input/`.
8. Si algo falla, registra el resultado en un log mensual (`Parametric Files/AT_Process_Log_{año}.xlsx`).

**Todo el flujo vive en SharePoint vía Microsoft Graph.** No hay modo local — versiones
anteriores de este proyecto leían/escribían en `data/` del disco, pero ese modo ya no existe.

---

## Arquitectura: Hexagonal (Ports & Adapters)

El código está organizado en 4 capas, y la regla es que las dependencias solo apuntan **hacia
adentro**:

```
adapters/  ──implementa──>  application/ports/  <──depende de──  application/
    │                                                                  │
    │ (SharePoint, Excel, MSAL, Key Vault)                            │ (caso de uso)
    ▼                                                                  ▼
              ambos dependen de  ──>   domain/  (reglas de negocio puras)
```

- **`domain/`** — el núcleo. Entidades (`dataclasses`), reglas de negocio, errores. No importa
  nada de `adapters/`, `application/` ni `infrastructure/`. No sabe que existe SharePoint.
- **`application/`** — el caso de uso (`process_weekly_metrics.py`) y los **Ports**: interfaces
  (`ABC`) que describen *qué necesita* el caso de uso del mundo exterior, sin decir *cómo* se
  consigue. Depende solo de `domain/` y de sus propios ports — **nunca** de `adapters/`.
- **`adapters/`** — las implementaciones concretas de esos ports contra SharePoint/Graph, más
  los lectores/escritores de Excel de bajo nivel que usan por dentro.
- **`infrastructure/`** — constantes de configuración (nombres de hoja, filas, colores, URLs,
  nombres de carpeta). Sin lógica.
- **`main.py`** — el *composition root*: el único lugar que conoce tanto los ports como sus
  implementaciones concretas. Arma todo y lo conecta.

Por qué importa: si mañana algo tiene que leerse de otro lado (por ejemplo, un archivo local en
vez de SharePoint), alcanza con escribir un nuevo adapter que implemente el mismo Port — el caso
de uso (`process_weekly_metrics.py`) no se toca, porque nunca supo que SharePoint existía.

---

## Cómo se ejecuta

```
python main.py --file-name <nombre-disparador> --client-secret <secreto-de-key-vault>
```

- `--file-name` no se usa para decidir qué leer (el script vuelve a listar `Input/` por su
  cuenta) — se mantiene solo porque la herramienta que dispara el proceso (Power Automate
  Desktop) siempre manda un nombre de archivo.
- `--client-secret` es el secreto de la app registrada que da acceso a Azure Key Vault, de
  donde salen las credenciales reales de SharePoint.

Requiere `msal`, `azure-identity`, `azure-keyvault-secrets`, `openpyxl`, `requests` instalados
(no hay `requirements.txt` en el repo todavía).

---

## Convención de nombres de los archivos de entrada

Los dos crudos se suben manualmente a `Input/` en SharePoint. El script **deduce el rango de la
semana leyendo el nombre del archivo** — no hay ninguna fecha adentro del Excel que use para
esto — así que el nombre tiene que respetar exactamente estos formatos
([`domain/raw_input_rules.py`](domain/raw_input_rules.py)):

| Archivo | Formato de fecha | Ejemplo |
|---|---|---|
| Productivity by User | `AÑO_MES_DIA` (guiones bajos) | `Productivity by User 2026_08_03.xlsx` |
| User_Details | `AÑO-MES-DIA` (guiones normales) | `User_Details_2026-08-03.xlsx` |

**Semana normal**: una sola fecha en cada archivo. El script asume **semana laboral de 5 días**
y calcula el fin como `inicio + 4 días` (`2026_08_03` → 03/08 al 07/08).

**User_Details siempre lleva una sola fecha**, incluso en rangos parciales: el día de inicio, o
sea el mismo que el primer número del par en "Productivity by User". El script usa esa fecha
para confirmar que ambos archivos son de la misma semana — si no coinciden, no los empareja y no
procesa nada.

En `Input/` debe haber **exactamente un** par a la vez (un "Productivity by User" y un
"User_Details"). Si hay dos de alguno, `find_matching_pair()` devuelve `None` y el script
termina sin procesar.

### Semanas que cruzan dos meses

Cuando una semana cae entre dos meses, el proceso son **dos pasadas**:

**Pasada 1 — se sube la semana completa** con el formato normal de una sola fecha. El script
detecta el cruce, crea **dos bloques de plantilla vacíos** (solo nombres de empleados, sin
horas) — uno en el Output de cada mes — archiva el par, y termina con `ERR013`. Esto es
esperado: el crudo trae totales semanales sin desglose por día, así que el script no puede saber
cuántas horas van a cada mes.

**Pasada 2 — se suben los dos parciales, uno por vez**, cada uno con el **rango explícito** en el
nombre de "Productivity by User" (dos fechas separadas por guion). Cada par se procesa como
semana normal y **rellena la plantilla ya creada** con las horas reales.

Ejemplo real — semana Lun 29/06/2026 a Vie 03/07/2026:

```
Pasada 1 (semana completa):
  Productivity by User 2026_06_29.xlsx     →  crea template junio: Week: 06/29/2026 - 06/30/2026
  User_Details_2026-06-29.xlsx                 crea template julio: Week: 07/01/2026 - 07/03/2026

Pasada 2a (parte que cierra junio):
  Productivity by User 2026_06_29-2026_06_30.xlsx   →  llena el template de junio
  User_Details_2026-06-29.xlsx

Pasada 2b (parte que abre julio):
  Productivity by User 2026_07_01-2026_07_03.xlsx   →  llena el template de julio
  User_Details_2026-07-01.xlsx
```

> **⚠️ Regla crítica**: los rangos de los parciales tienen que calzar **exactamente** con los
> rangos de las plantillas que se crearon en la pasada 1. Si no calzan, el script no reconoce la
> plantilla y crea un bloque nuevo aparte, dejando la plantilla vacía huérfana.
>
> - La parte que **cierra** el mes calza sola (siempre termina el último día del mes).
> - La parte que **abre** el mes nuevo debe terminar **el mismo día en que termina la semana
>   completa** (`inicio + 4 días`), no extenderse más allá. Acá es donde más fácil se rompe: si
>   la semana completa fue `2026_06_29` (termina el 03/07), el parcial de julio va `01` al `03`
>   — nunca hasta el 04 o el 05.

---

## Recorrido paso a paso, desde `main.py`

Esta es la secuencia **real y completa**, en el orden exacto en que corre el código.

**0. Arranque** — [`main.py:103-104`](main.py#L103-L104) → `if __name__ == "__main__": main()`

**1. Leer argumentos** — [`main.py:53`](main.py#L53) `parse_arguments()` (definida en
[`main.py:21-25`](main.py#L21-L25)) → recibe `--file-name` y `--client-secret` por consola.

**2. Autenticarse antes que nada** — [`main.py:58`](main.py#L58)
`authenticate_graph(args.client_secret)` (definida en [`main.py:28-38`](main.py#L28-L38)). Sin
esto no se puede hacer nada más, por eso es el primer paso real del `try`:
- [`adapters/key_vault_auth.py:13`](adapters/key_vault_auth.py#L13) `get_key_vault_session()` —
  abre sesión contra Azure Key Vault usando `ClientSecretCredential` (tenant/client/URL del
  vault están en [`infrastructure/graph_config.py`](infrastructure/graph_config.py), sección
  "Azure Key Vault").
- [`adapters/key_vault_auth.py:22`](adapters/key_vault_auth.py#L22)
  `get_sharepoint_credentials()` — con esa sesión, saca del vault el tenant_id/client_id/
  client_secret **de SharePoint** (los nombres de esos 3 secretos están en
  `SHAREP_SECRET_NAMES`, en el mismo archivo de config).
- [`adapters/graph_auth.py:5`](adapters/graph_auth.py#L5) `get_access_token()` — con esas
  credenciales de SharePoint, MSAL (`ConfidentialClientApplication.acquire_token_for_client()`)
  pide el token de acceso a Microsoft Graph.

**3. Construir el contexto de Graph** — [`main.py:59`](main.py#L59) `build_context(access_token)`
(definida en [`main.py:41-49`](main.py#L41-L49)):
- [`adapters/sharepoint_client.py:103`](adapters/sharepoint_client.py#L103) `get_site_id()`
- [`adapters/sharepoint_client.py:118`](adapters/sharepoint_client.py#L118) `get_drive_id()`
- arma un `GraphContext` ([`adapters/sharepoint_client.py:9-13`](adapters/sharepoint_client.py#L9-L13)):
  `access_token` + `site_id` + `drive_id`. **Este objeto se pasa a todos los adapters** — es el
  "cómo hablarle a esta biblioteca de SharePoint" de acá en adelante.

**4. Instanciar los adapters (composition root)** — [`main.py:61-63`](main.py#L61-L63): se crean
`SharePointRawInputAdapter(context)`, `SharePointMasterEmployeeAdapter(context)` y
`SharePointMetricsOutputAdapter(context)`. Cada uno implementa un Port distinto (ver tabla más
abajo) — de acá en adelante, el resto del código habla con estos objetos a través de sus
interfaces, no con SharePoint directamente.

**5. Buscar el par de archivos crudos** — [`main.py:65`](main.py#L65) `raw_input.find_next_pair()`
→ [`adapters/sharepoint_raw_input_adapter.py:33-37`](adapters/sharepoint_raw_input_adapter.py#L33-L37):
- [`adapters/sharepoint_client.py:16`](adapters/sharepoint_client.py#L16)
  `list_input_files_graph()` lista todo lo que hay en `Input/`.
- [`domain/raw_input_rules.py:43`](domain/raw_input_rules.py#L43) `find_matching_pair()` — regla
  **pura** (sin I/O): busca exactamente un archivo que empiece con "Productivity by User" y uno
  que empiece con "User_Details", parsea la fecha de cada nombre
  ([`parse_prod_by_user_filename`](domain/raw_input_rules.py#L12),
  [`parse_user_details_filename`](domain/raw_input_rules.py#L34)) y verifica que coincidan.
  Devuelve un `RawInputPair` ([`domain/model.py:48-53`](domain/model.py#L48-L53)) o `None`.
- Si es `None` — [`main.py:67-69`](main.py#L67-L69): imprime "Raw pair not ready yet..." y
  **termina sin error**. No es una falla, es un estado normal: todavía no llegó el segundo
  archivo de la semana.

**6. Ejecutar el caso de uso** — [`main.py:71`](main.py#L71)
`process_weekly_metrics(pair, raw_input, master_employees_reader, metrics_output)` →
[`application/process_weekly_metrics.py:21-90`](application/process_weekly_metrics.py#L21-L90).
Esta función **no sabe que existe SharePoint** — solo conoce los 3 Ports que recibe como
parámetro. Adentro:

  a. `raw_input.read_employee_metrics(pair)` ([línea 36](application/process_weekly_metrics.py#L36))
     → [`sharepoint_raw_input_adapter.py:39-50`](adapters/sharepoint_raw_input_adapter.py#L39-L50):
     descarga los bytes de los dos archivos (`download_file_graph`, guardados en una caché
     interna del adapter para reusarlos más tarde al archivar sin volver a descargarlos) y llama
     a [`adapters/excel_reader_raw.py:113`](adapters/excel_reader_raw.py#L113)
     `build_employee_metrics_from_raw()`, que combina ambos archivos por nombre de empleado:
     `read_prod_by_user_hours()` convierte segundos a horas decimales, `read_user_details_active_days()`
     saca los días activos, y arma cada `EmployeeMetric` ya con
     `department=DEPARTMENT` ([`domain/constants.py:12`](domain/constants.py#L12), fijo:
     `"7000 - INFORMATION TECHNOLOGY"`).

  b. Arma un `WeekData` ([líneas 38-43](application/process_weekly_metrics.py#L38-L43)).

  c. `master_employees_reader.get_master_employees()` ([línea 45](application/process_weekly_metrics.py#L45))
     → [`sharepoint_master_employee_adapter.py:22-28`](adapters/sharepoint_master_employee_adapter.py#L22-L28):
     descarga `Parametric Files/AT_Employees.xlsx`; si no existe, `ATError ERR025` (salta directo
     al paso 7). Si existe, [`adapters/excel_reader.py:63`](adapters/excel_reader.py#L63)
     `read_excel()` lo parsea a `list[MasterEmployee]`.

  d. [`domain/business_rules.py:35`](domain/business_rules.py#L35) `detect_cross_month()` —
     ¿el mes de `week_start` es distinto al de `week_end`?
     - **Si cruza de mes**: [`build_placeholder_employees()`](domain/business_rules.py#L89)
       arma una fila vacía por cada empleado del maestro (también con `department=DEPARTMENT`),
       [`split_cross_month_range()`](domain/business_rules.py#L111) parte el rango en un bloque
       de cierre (mes actual) y uno de apertura (mes siguiente), y se llama
       `metrics_output.write_week(...)` dos veces — una por cada mes — con esos placeholders
       ([líneas 56-61](application/process_weekly_metrics.py#L56-L61)). Termina lanzando
       `ATError ERR013` (se crearon plantillas nuevas) o `ERR015` (ya existían, no se cambió
       nada) — **no llega a escribir datos reales ni a archivar los crudos**.
     - **Si no cruza**: [`match_employees()`](domain/business_rules.py#L40) cruza por nombre
       normalizado (`normalize_name` quita tildes/mayúsculas) contra el maestro —
       [`apply_business_rules()`](domain/business_rules.py#L60) calcula `goal`
       (`calculate_goal`) y los 4 colores por umbral (`calculate_productive_color`,
       `calculate_passive_status`, `calculate_active_hours_color`, `calculate_total_hours_color`
       — umbrales en [`domain/constants.py`](domain/constants.py)).

  e. `metrics_output.write_week(...)` ([líneas 77-83](application/process_weekly_metrics.py#L77-L83))
     → [`sharepoint_metrics_output_adapter.py:36-75`](adapters/sharepoint_metrics_output_adapter.py#L36-L75):
     arma la ruta `Output/{año}/{mes}/AT_Metrics_{año}-{mes}.xlsx`
     ([`build_output_path`](adapters/sharepoint_client.py#L93)), descarga ese workbook si ya
     existe o crea uno nuevo, chequea `week_already_exists()` — si la semana ya está, devuelve
     `False` sin tocar nada; si no, escribe el bloque completo (`write_week_range`,
     `write_headers`, `apply_column_colors`, `apply_header_font`, `set_column_width`,
     `write_employees`, `apply_colors`, `apply_table_borders` — todo en
     [`adapters/excel_write.py`](adapters/excel_write.py)) y sube el resultado
     (`upload_file_graph`).

  f. Si la semana ya existía (`written = False`) — [líneas 85-86](application/process_weekly_metrics.py#L85-L86):
     devuelve el mensaje `"Week already exists. Nothing to process."`; `main.py` lo imprime
     ([línea 74](main.py#L74)) y termina normal, **sin archivar** (no tiene sentido archivar un
     par que no aportó nada nuevo).

  g. Si se escribió — [línea 88](application/process_weekly_metrics.py#L88):
     `raw_input.archive_pair(pair)` →
     [`sharepoint_raw_input_adapter.py:52-61`](adapters/sharepoint_raw_input_adapter.py#L52-L61):
     sube copias de los dos crudos a `Input/Processed/{año}/{mes}/`
     ([`build_processed_path`](adapters/sharepoint_client.py#L99-L100), usando los bytes que ya
     había descargado en el paso (a), sin re-descargar) y borra los originales de `Input/`
     (`delete_file_graph`).

**7. Manejo de errores** (`except ATError`) — [`main.py:76-100`](main.py#L76-L100): mapea el
código del error a un status (`ERR015` → `STATUSES["success"]`, `ERR013` →
`STATUSES["pending"]`, cualquier otro → `STATUSES["error"]` — ver
[`infrastructure/config.py`](infrastructure/config.py)), arma un `LogEntry` con el nombre del
archivo que se estaba procesando (o un texto genérico si ni siquiera se llegó a encontrar el
par), y si ya había contexto de Graph autenticado, sube el log vía
[`adapters/sharepoint_log_adapter.py:23-57`](adapters/sharepoint_log_adapter.py#L23-L57)
`SharePointExecutionLogAdapter.write()` a `Parametric Files/AT_Process_Log_{año}.xlsx`. Si la
autenticación misma falló (no hay `context`), solo imprime por consola — no hay forma de subir
un log sin haberse autenticado. Siempre vuelve a lanzar la excepción al final (`raise`), para
que quien dispare el script (PAD) vea que falló.

---

## Los 4 Ports y quién implementa cada uno

Cada Port es una interfaz (`ABC` + `@abstractmethod`) en `application/ports/`. El caso de uso
(`process_weekly_metrics.py`) solo conoce estas 4 interfaces — nunca las clases concretas de la
columna derecha, esas las conecta `main.py`.

| Port | Qué expone | Implementación concreta |
|---|---|---|
| [`RawInputPort`](application/ports/raw_input_port.py) | `find_next_pair()`, `read_employee_metrics(pair)`, `archive_pair(pair)` | [`SharePointRawInputAdapter`](adapters/sharepoint_raw_input_adapter.py) |
| [`MasterEmployeePort`](application/ports/master_employee_port.py) | `get_master_employees()` | [`SharePointMasterEmployeeAdapter`](adapters/sharepoint_master_employee_adapter.py) |
| [`MetricsOutputPort`](application/ports/metrics_output_port.py) | `write_week(year, month, week_start, week_end, employees)` | [`SharePointMetricsOutputAdapter`](adapters/sharepoint_metrics_output_adapter.py) |
| [`ExecutionLogPort`](application/ports/execution_log_port.py) | `write(log_entry)` | [`SharePointExecutionLogAdapter`](adapters/sharepoint_log_adapter.py) |

Cada adapter de la columna derecha es "delgado": arma rutas y llama a las funciones de más bajo
nivel de `adapters/sharepoint_client.py` (HTTP contra Graph) y de `adapters/excel_reader.py` /
`adapters/excel_reader_raw.py` / `adapters/excel_write.py` (parseo/escritura de `.xlsx` con
`openpyxl`). Esos módulos de bajo nivel no implementan ningún Port directamente — son las
herramientas que usan los adapters por dentro.

---

## Domain — reglas de negocio puras

Nada en `domain/` importa `openpyxl`, `requests` ni nada de `adapters/`/`infrastructure/`
(excepto `domain/business_rules.py` y `domain/raw_input_rules.py`, que sí dependen de
`domain/constants.py` y `domain/model.py` — eso sigue siendo domain, no infraestructura).

| Archivo | Contiene |
|---|---|
| [`domain/model.py`](domain/model.py) | Los 5 `dataclass`: `EmployeeMetric`, `WeekData`, `LogEntry`, `MasterEmployee`, `RawInputPair`. |
| [`domain/business_rules.py`](domain/business_rules.py) | `normalize_name`, matching, cálculo de `goal` y de los 4 colores, detección/partición de cruce de mes. |
| [`domain/raw_input_rules.py`](domain/raw_input_rules.py) | Parseo de nombres de archivo crudo y `find_matching_pair()` — reglas de "qué archivos son", separadas de "qué dicen las métricas". |
| [`domain/constants.py`](domain/constants.py) | `GOALS`, `DEPARTMENT`, umbrales de horas. |
| [`domain/errors.py`](domain/errors.py) | `ATError` + el diccionario `ERROR_MESSAGES` (todos los códigos `ERRxxx`). |

---

## Infrastructure — configuración

| Archivo | Contiene |
|---|---|
| [`infrastructure/config.py`](infrastructure/config.py) | Nombres de hoja, filas/columnas de lectura y escritura, colores, anchos de columna, nombres de carpeta — agrupado por a qué parte del flujo pertenece cada bloque (ver comentarios en el archivo). |
| [`infrastructure/graph_config.py`](infrastructure/graph_config.py) | `GraphCredentials`, `BASE_FOLDER` (la carpeta raíz en SharePoint), constantes de Key Vault. |

---

## Códigos de error (`ATError`)

Definidos en [`domain/errors.py`](domain/errors.py). Los que terminan el proceso con un status
distinto de `ERROR` están marcados:

| Código | Significado | Status en el log |
|---|---|---|
| ERR001 | La carpeta no existe | ERROR |
| ERR002 | No hay archivos Excel para procesar | ERROR |
| ERR004 | No se pudo abrir el archivo Excel | ERROR |
| ERR005 | No existe la hoja esperada | ERROR |
| ERR006 | Las columnas del Excel no coinciden con lo esperado | ERROR |
| ERR013 | El archivo cruza dos meses — se crearon plantillas para completar a mano | **PENDING** |
| ERR014 | No se pudo guardar el Excel | ERROR |
| ERR015 | Cruce de mes — las plantillas ya existían, no se cambió nada | **SUCCESS** |
| ERR020 | No se pudo autenticar contra Graph | ERROR |
| ERR021 | No se pudo listar archivos de SharePoint | ERROR |
| ERR022 | No se pudo descargar un archivo de SharePoint | ERROR |
| ERR023 | No se pudo subir un archivo a SharePoint | ERROR |
| ERR024 | No se pudo resolver el sitio o el drive de SharePoint | ERROR |
| ERR025 | No se encontró el maestro de empleados en SharePoint | ERROR |
| ERR026 | Archivo bloqueado (probablemente abierto en el navegador) | ERROR |
| ERR027 | No se pudo borrar un archivo de SharePoint | ERROR |

---

## Estructura de carpetas del repo

```
main.py                          composition root: auth, wiring de adapters, log de errores

domain/
  model.py                       dataclasses (EmployeeMetric, WeekData, LogEntry,
                                  MasterEmployee, RawInputPair)
  business_rules.py               matching, goal, colores, cruce de mes
  raw_input_rules.py               parseo de nombres de archivo + emparejamiento
  constants.py                     GOALS, DEPARTMENT, umbrales
  errors.py                        ATError + ERROR_MESSAGES

application/
  process_weekly_metrics.py       el caso de uso completo
  ports/
    raw_input_port.py
    master_employee_port.py
    metrics_output_port.py
    execution_log_port.py

adapters/
  sharepoint_raw_input_adapter.py       implementa RawInputPort
  sharepoint_master_employee_adapter.py implementa MasterEmployeePort
  sharepoint_metrics_output_adapter.py  implementa MetricsOutputPort
  sharepoint_log_adapter.py             implementa ExecutionLogPort
  sharepoint_client.py             llamadas HTTP crudas a Microsoft Graph + GraphContext
  excel_reader.py                  lee el maestro de empleados (.xlsx)
  excel_reader_raw.py               lee los dos crudos de ActivTrak (.xlsx)
  excel_write.py                    escribe el workbook de salida (.xlsx)
  graph_auth.py                     MSAL — pide el token de Graph
  key_vault_auth.py                 Azure Key Vault — trae las credenciales de SharePoint

infrastructure/
  config.py                        constantes de Excel (hojas, filas, columnas, colores)
  graph_config.py                   constantes de SharePoint/Graph/Key Vault
```

---

## Gaps conocidos / recomendaciones

- **No hay tests.** El caso de uso (`process_weekly_metrics`) es fácil de testear ahora que solo
  depende de 3 Ports (se pueden mockear con clases simples que implementen la interfaz) — es la
  pieza con más valor para cubrir primero si se agregan tests.
- No hay `requirements.txt` en el repo — las dependencias (`msal`, `azure-identity`,
  `azure-keyvault-secrets`, `openpyxl`, `requests`) están instaladas en el entorno donde corre
  hoy, pero no versionadas.
