ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache python3 py3-pip bash

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

RUN printf '#!/bin/bash\nset -e\nexport PORT="${PORT:-8001}"\nexport LOG_LEVEL="${LOG_LEVEL:-info}"\nexport HA_URL="http://supervisor/core/api"\nexport HA_CONFIG_PATH="/config"\necho "Starting HA OpenAPI Server v4.0.24..."\necho "Environment check:"\necho "  SUPERVISOR_TOKEN: ${SUPERVISOR_TOKEN:+[PRESENT]}${SUPERVISOR_TOKEN:-[MISSING]}"\necho "  HASSIO_TOKEN: ${HASSIO_TOKEN:+[PRESENT]}${HASSIO_TOKEN:-[MISSING]}"\nif [ -n "$SUPERVISOR_TOKEN" ]; then\n  export HA_TOKEN="$SUPERVISOR_TOKEN"\nelif [ -n "$HASSIO_TOKEN" ]; then\n  export HA_TOKEN="$HASSIO_TOKEN"\n  export SUPERVISOR_TOKEN="$HASSIO_TOKEN"\nfi\nexec python3 -u /config/ha-openapi-server/server.py\n' > /app/run.sh && chmod +x /app/run.sh

ENV PYTHONUNBUFFERED=1
EXPOSE 8001
CMD ["/app/run.sh"]
