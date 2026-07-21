# sat-efos-tracker

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![SAT](https://img.shields.io/badge/fuente-SAT%20México-red)
![Art. 69-B](https://img.shields.io/badge/Art.-69--B%20CFF-orange)

Tracker automático del **Listado Art. 69-B CFF** publicado por el SAT (EFOS/EDOS).

Descarga el CSV oficial directamente del portal del SAT, detecta cambios respecto al snapshot anterior y registra un log estructurado (JSON) con nuevos RFC, cambios de situación y bajas. Notificación opcional por correo.

> **Principio de fuente única:** el script descarga siempre el archivo original desde
> `omawww.sat.gob.mx` — nunca de intermediarios ni software contable. El CSV procesado
> local es solo una copia normalizada para consulta; la fuente de verdad es siempre el SAT y el DOF.

---

## ¿Por qué existe este proyecto?

El SAT publica el listado del Art. 69-B como un CSV de más de 14,000 filas en un portal poco accesible. Los contribuyentes que operaron con un EFOS tienen **30 días hábiles** desde la publicación para desvirtuar la presunción — un plazo que puede perderse si no hay monitoreo activo.

Este repositorio automatiza esa vigilancia: descarga, normaliza y compara el listado para que contadores, abogados fiscalistas y contribuyentes detecten cambios el mismo día en que el SAT los publica, sin depender de software privativo.

---

## Estructura del proyecto

```
sat-efos-tracker/
├── config.py          # URLs, rutas, parámetros globales
├── downloader.py      # Descarga HTTP con reintentos y detección de cambios por SHA-256
├── parser.py          # Limpieza y normalización del CSV (encoding windows-1250)
├── differ.py          # Comparación entre snapshots: nuevos / cambios / bajas
├── checker.py         # Consulta de RFC(s) contra el listado local (CLI o módulo)
├── notifier.py        # Notificaciones por SMTP cuando hay novedades
├── scheduler.py       # Orquestador principal + daemon diario
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── data/
│   ├── raw/           # CSVs originales del SAT (encoding windows-1250)
│   └── processed/     # CSVs normalizados (UTF-8, columnas mapeadas)
├── logs/
│   ├── tracker.log    # Log de operación del daemon
│   └── diff_*.json    # Diffs estructurados por fecha
└── tests/
    └── test_core.py   # Pruebas unitarias (22 tests)
```

---

## Instalación rápida

### Opción A — Python directo

```bash
git clone https://github.com/tiendadaxiang-hub/Paimon_SAT-EFOS-TRACKER_by_ACM.git
cd Paimon_SAT-EFOS-TRACKER_by_ACM
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Ejecutar una vez inmediatamente
python scheduler.py --now

# Ver resumen del último diff
python scheduler.py --status

# Consultar un RFC
python checker.py ABC010101ABC

# Consultar lote desde CSV (columna "rfc")
python checker.py --csv mis_proveedores.csv --col rfc
```

### Opción B — Docker (recomendado para Proxmox/homelab)

```bash
cp .env.example .env
# Editar .env con tu configuración

docker compose up -d
docker compose logs -f
```

---

## Flujo de ejecución

```
SAT (omawww.sat.gob.mx)
        │
        ▼  HTTP GET con reintentos (backoff exponencial)
   downloader.py
        │  Verifica SHA-256 vs snapshot anterior
        │  Si idéntico → sin acción
        ▼
   parser.py
        │  Decode windows-1250 → UTF-8
        │  Skip 3 filas de metadatos SAT
        │  Normaliza RFC, nombre, situación, fecha
        ▼
   differ.py
        │  Compara índice anterior vs nuevo
        │  Clasifica: NUEVO / CAMBIO / BAJA
        │  Guarda diff_YYYYMMDD_HHMM.json
        ▼
   notifier.py  (opcional, si SMTP configurado)
        │  Envía resumen por correo si hay cambios
        ▼
   data/processed/listado_69b_latest.csv   ← índice local consultable
```

---

## Campos del listado procesado

| Campo                        | Descripción                                                        |
|------------------------------|--------------------------------------------------------------------|
| `numero`                     | Secuencial del SAT                                                 |
| `rfc`                        | RFC del contribuyente (12-13 caracteres)                           |
| `nombre`                     | Nombre o razón social (normalizado a mayúsculas)                   |
| `situacion`                  | `presunto` / `definitivo` / `desvirtuado` / `sentencia favorable`  |
| `fecha_primera_publicacion`  | Fecha ISO 8601 de primera aparición en lista                       |
| `numero_oficio`              | Número de oficio SAT de referencia                                 |

---

## Consulta de RFC

```bash
# Individual
python checker.py RFC123456789

# Múltiple
python checker.py RFC1 RFC2 RFC3

# Lote desde CSV
python checker.py --csv proveedores.csv --col rfc
```

Ejemplo de salida:
```
──────────────────────────────────────────────────
  RFC       : ABC010101ABC
  Estado    : ⚠️  EN LISTA
  Situación : DEFINITIVO
  Nombre    : EMPRESA FANTASMA SA DE CV
  Publicado : 2023-01-15
  Oficio    : 500-05-2023-00001
──────────────────────────────────────────────────
Fuente: listado local (Art. 69-B CFF) — sat.gob.mx
```

---

## Variables de entorno

| Variable              | Default   | Descripción                                 |
|-----------------------|-----------|---------------------------------------------|
| `EFOS_SCHEDULE_TIME`  | `06:00`   | Hora de descarga diaria (HH:MM)             |
| `EFOS_RUN_ON_START`   | `true`    | Ejecutar ciclo al iniciar                   |
| `EFOS_NOTIFY_ON_NEW`  | `true`    | Enviar correo si hay cambios                |
| `EFOS_SMTP_HOST`      | —         | Servidor SMTP (p.ej. `smtp.gmail.com`)      |
| `EFOS_SMTP_PORT`      | `587`     | Puerto SMTP (STARTTLS)                      |
| `EFOS_SMTP_USER`      | —         | Usuario SMTP                                |
| `EFOS_SMTP_PASS`      | —         | Contraseña SMTP / App Password              |
| `EFOS_NOTIFY_FROM`    | —         | Dirección remitente                         |
| `EFOS_NOTIFY_TO`      | —         | Destinatarios (separados por coma)          |

---

## Tests

```bash
# Con pytest
python -m pytest tests/ -v

# Sin pytest (built-in)
python tests/test_core.py
```

22 pruebas unitarias cubriendo parser, differ y checker.

---

## Fuentes oficiales

- **Listado CSV SAT:** `http://omawww.sat.gob.mx/cifras_sat/Documents/Listado_Completo_69-B.csv`
- **Portal SAT:** `http://omawww.sat.gob.mx/cifras_sat/Paginas/datos/vinculo.html?page=ListCompleta69B.html`
- **DOF:** `https://www.dof.gob.mx` (publicación de oficios individuales)
- **Fundamento legal:** Art. 69-B CFF; Art. 113 Bis CFF

---

## Aviso legal

Este repositorio descarga y procesa datos públicos del SAT para facilitar la consulta operativa. **No sustituye la consulta directa al portal oficial del SAT.** Ante cualquier discrepancia, prevalece siempre la información publicada por el SAT en su portal y en el DOF. El uso de esta herramienta no exime al contribuyente de sus obligaciones fiscales ni constituye asesoría legal o fiscal.

---

Paimon...(luego volver)

## Licencia

MIT — libre para usar, modificar y distribuir citando al autor.
