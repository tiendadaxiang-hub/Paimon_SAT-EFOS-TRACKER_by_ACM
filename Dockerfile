# ── sat-efos-tracker — Dockerfile ────────────────────────────────────────────
# Imagen minimalista para correr en Proxmox/Docker (Raspberry Pi compatible)
# Build:  docker build -t sat-efos-tracker .
# Run:    docker run -d --name efos-tracker \
#           -e EFOS_SCHEDULE_TIME=06:00 \
#           -e EFOS_NOTIFY_TO=davo@example.com \
#           -v /ruta/local/data:/app/data \
#           -v /ruta/local/logs:/app/logs \
#           sat-efos-tracker

FROM python:3.12-slim

LABEL org.opencontainers.image.title="sat-efos-tracker"
LABEL org.opencontainers.image.description="Tracker automático del listado SAT Art. 69-B CFF (EFOS/EDOS)"
LABEL org.opencontainers.image.licenses="MIT"

# Variables de entorno configurables
ENV EFOS_SCHEDULE_TIME=06:00
ENV EFOS_RUN_ON_START=true
ENV EFOS_NOTIFY_ON_NEW=true
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema (mínimas)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código fuente
COPY config.py downloader.py parser.py differ.py notifier.py scheduler.py checker.py ./

# Crear directorios de datos (se sobreescriben con volúmenes externos)
RUN mkdir -p data/raw data/processed logs tests

# Puerto no necesario (no es API), pero se documenta por si se agrega FastAPI después
# EXPOSE 8000

HEALTHCHECK --interval=60m --timeout=30s --start-period=60s --retries=3 \
    CMD python scheduler.py --status || exit 1

CMD ["python", "scheduler.py"]
