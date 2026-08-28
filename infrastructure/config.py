'''
Configuración: nombres de hojas, filas/columnas de lectura y escritura,
colores y nombres de carpetas. Agrupado por a qué parte del flujo
pertenece cada constante.
'''

# ============================================================
# Archivo maestro de empleados (AT_Employees.xlsx)
# Usado por adapters/excel_reader.py para leer y validar la hoja
# "Employees" (columnas EmployeeID / Name / Email / Status).
# ============================================================

SHEET_MASTER = "Employees"
HEADER_ROW_MASTER = 1
START_ROW_MASTER = 2

MASTER_COLUMNS = [
    "EmployeeID",
    "Name",
    "Email",
    "Status"
]


# ============================================================
# Archivos crudos de ActivTrak (Productivity by User + User_Details)
# Usado por adapters/excel_reader_raw.py para leer y validar ambos
# exports antes de combinarlos en EmployeeMetric.
# ============================================================

RAW_HEADER_ROW = 1
RAW_START_ROW = 2

PROD_BY_USER_COLUMNS_NEEDED = ["User", "ProdActive (secs)", "ProdPassive (secs)"]
USER_DETAILS_COLUMNS_NEEDED = ["User", "Active Days"]

# Carpetas (relativas a BASE_FOLDER, ver infrastructure/graph_config.py)
# donde SharePoint recibe los crudos y donde se archivan tras procesarlos.
RAW_INPUTS_FOLDER = "Input"
RAW_INPUTS_PROCESSED_FOLDER = "Input/Processed"


# ============================================================
# Workbook de salida (AT_Metrics_{año}-{mes}.xlsx)
# Usado por adapters/excel_write.py para armar cada bloque semanal.
# ============================================================

OUTPUT_SHEET_NAME = "Productive + Passive"

# Formato del texto "Week: {inicio} - {fin}" que encabeza cada bloque
# semanal (y que week_already_exists() usa para detectar duplicados).
DATE_FORMAT = "%m/%d/%Y"

# Fila donde arranca el primer bloque semanal y fila de cabecera de
# ese primer bloque (los bloques siguientes se calculan a partir de
# get_next_block_start_row(), no de estas constantes).
WEEK_ROW_OUTPUT = 5
HEADER_ROW_OUTPUT = 6
OUTPUT_START_ROW = 7

OUTPUT_COLUMNS = [
    "Name",
    "Department",
    "Productive Active Hrs",
    "Productive Passive Hrs",
    "Total Productive Hrs",
    "Active Days",
    "GOAL",
    "Productive Hrs/Day",
    "Comments"
]

# Posición (1-indexed) de cada columna dentro de OUTPUT_COLUMNS —
# usadas para aplicar formato numérico, colores y anchos por columna.
NAME_COLUMN = 1
DEPARTMENT_COLUMN = 2
PRODUCTIVE_ACTIVE_COLUMN = 3
PASSIVE_COLUMN = 4
TOTAL_PRODUCTIVE_COLUMN = 5
ACTIVE_DAYS_COLUMN = 6
GOAL_COLUMN = 7
HOURS_DAY_COLUMN = 8
COMMENTS_COLUMN = 9


# ============================================================
# Estilos del workbook de salida
# ============================================================

# Colores de semáforo por umbral (horas productivas, horas pasivas,
# horas totales) — aplicados por adapters/excel_write.apply_colors().
# Tonos pastel (los mismos que usa el "Light Fill" de formato
# condicional nativo de Excel) para que se note el semáforo sin que
# resalte demasiado sobre el resto de la tabla.
COLORS = {
    "green": "C6EFCE",
    "red": "FFC7CE",
    "yellow": "FFEB9C"
}

# Relleno de la fila de cabecera de cada bloque semanal: amarillo para
# las columnas GOAL/Comments, azul para el resto.
YELLOW_COLUMNS = {GOAL_COLUMN, COMMENTS_COLUMN}
BLUE_FILL_COLOR = "4472C4"
YELLOW_FILL_COLOR = "ffd555"

COLUMN_WIDTHS = {
    NAME_COLUMN: 27,
    DEPARTMENT_COLUMN: 32,
    PRODUCTIVE_ACTIVE_COLUMN: 20,
    PASSIVE_COLUMN: 20,
    TOTAL_PRODUCTIVE_COLUMN: 20,
    ACTIVE_DAYS_COLUMN: 11,
    GOAL_COLUMN: 8,
    HOURS_DAY_COLUMN: 20,
    COMMENTS_COLUMN: 42,
}


# ============================================================
# Log de ejecución (AT_Process_Log_{año}.xlsx)
# Usado por adapters/sharepoint_log_adapter.py.
# ============================================================

LOG_COLUMNS = [
    "Source File",
    "Execution Date",
    "Status",
    "Error Message",
    "Error Code",
]

# Valores posibles de la columna "Status" del log — main.py los usa al
# armar el LogEntry dentro del except ATError. "warning" queda
# definido para uso manual/futuro; hoy el flujo solo produce
# success/pending/error (ver domain/errors.py para el mapeo de
# códigos ATError a cada uno).
STATUSES = {
    "success": "SUCCESS",
    "error": "ERROR",
    "warning": "WARNING",
    "pending": "PENDING"
}
