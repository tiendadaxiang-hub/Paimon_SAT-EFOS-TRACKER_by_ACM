"""
config.py — Configuración central del tracker EFOS/EDOS SAT
"""

import os
from pathlib import Path

# ─── Rutas base ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
LOGS_DIR = BASE_DIR / "logs"

# ─── URLs oficiales SAT ───────────────────────────────────────────────────────
# Portal de Datos Abiertos del SAT (fuente canónica)
SAT_PORTAL_URL = (
    "https://www.sat.gob.mx/minisitio/DatosAbiertos/contribuyentes_publicados.html"
)

# Listado completo Art. 69-B (EFOS/EDOS) — URL primaria
SAT_CSV_URL = (
    "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/"
    "Datos_abiertos/Documents_AGAFF/Listado_completo_69-B.csv"
)

# URLs individuales por situación (Art. 69-B)
SAT_CSV_DEFINITIVOS   = (
    "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/"
    "Datos_abiertos/Documents_AGAFF/Definitivos.csv"
)
SAT_CSV_PRESUNTOS     = (
    "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/"
    "Datos_abiertos/Documents_AGAFF/Presuntos.csv"
)
SAT_CSV_DESVIRTUADOS  = (
    "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/"
    "Datos_abiertos/Documents_AGAFF/Desvirtuados.csv"
)
SAT_CSV_SENTENCIAS    = (
    "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/"
    "Datos_abiertos/Documents_AGAFF/SentenciasFavorables.csv"
)

# Art. 69-B Bis (transmisión indebida de pérdidas fiscales)
SAT_CSV_69B_BIS = (
    "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/"
    "Datos_abiertos/Documents_AGGC/Listado_69_B_Bis_Completo.csv"
)

# URL legacy (omawww) — se mantiene como fallback
SAT_CSV_URL_LEGACY = (
    "http://omawww.sat.gob.mx/cifras_sat/Documents/Listado_Completo_69-B.csv"
)

DOF_BASE_URL = "https://www.dof.gob.mx/nota_detalle.php"

# ─── Encoding del archivo SAT (no modificar) ──────────────────────────────────
SAT_CSV_ENCODING = "windows-1250"
SAT_CSV_HEADER_SKIP = 3       # Las primeras 3 filas son metadatos del SAT
SAT_CSV_DELIMITER = ","
SAT_CSV_QUOTECHAR = '"'

# ─── Columnas esperadas en el CSV del SAT ─────────────────────────────────────
# El SAT no garantiza nombres estables; se mapean por posición
COL_MAP = {
    0: "numero",          # Número secuencial
    1: "rfc",             # RFC del contribuyente
    2: "nombre",          # Nombre o razón social
    3: "situacion",       # Presunto / Definitivo / Desvirtuado / Sentencia
    4: "fecha_primera_publicacion",
    5: "numero_oficio",
}

# Valores posibles del campo situacion (normalizados a minúsculas)
SITUACION_PRESUNTO    = "presunto"
SITUACION_DEFINITIVO  = "definitivo"
SITUACION_DESVIRTUADO = "desvirtuado"
SITUACION_SENTENCIA   = "sentencia favorable"

# ─── Nombres de archivos ──────────────────────────────────────────────────────
RAW_CSV_NAME       = "listado_69b_raw_{fecha}.csv"
PROCESSED_CSV_NAME = "listado_69b_{fecha}.csv"
LAST_SNAPSHOT_NAME = "listado_69b_latest.csv"
DIFF_LOG_NAME      = "diff_{fecha}.json"

# ─── Scheduler ────────────────────────────────────────────────────────────────
# Hora de descarga diaria (formato 24h, hora Ciudad de México / CST UTC-6)
SCHEDULE_TIME = os.getenv("EFOS_SCHEDULE_TIME", "06:00")
# Descargar también al iniciar el script (aunque no sea la hora programada)
RUN_ON_START  = os.getenv("EFOS_RUN_ON_START", "true").lower() == "true"

# ─── Red y reintentos ─────────────────────────────────────────────────────────
REQUEST_TIMEOUT   = 60          # segundos
MAX_RETRIES       = 5
RETRY_BACKOFF     = 2.0         # segundos base para backoff exponencial
USER_AGENT        = (
    "sat-efos-tracker/1.0 (github.com/Ar0d3x/sat-efos-tracker; "
    "dr.nietodavid@protonmail.com)"
)

# ─── Notificaciones (opcional) ────────────────────────────────────────────────
# Configura vía variables de entorno para no exponer credenciales en el repo
SMTP_HOST     = os.getenv("EFOS_SMTP_HOST", "")
SMTP_PORT     = int(os.getenv("EFOS_SMTP_PORT", "587"))
SMTP_USER     = os.getenv("EFOS_SMTP_USER", "")
SMTP_PASSWORD = os.getenv("EFOS_SMTP_PASS", "")
NOTIFY_FROM   = os.getenv("EFOS_NOTIFY_FROM", "")
NOTIFY_TO     = os.getenv("EFOS_NOTIFY_TO", "")   # separados por coma
NOTIFY_ON_NEW = os.getenv("EFOS_NOTIFY_ON_NEW", "true").lower() == "true"
