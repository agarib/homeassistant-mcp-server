ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache python3 py3-pip bash

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

RUN printf '#!/bin/bash\nset -e\nexport PORT="${PORT:-8001}"\nexport LOG_LEVEL="${LOG_LEVEL:-info}"\nexport HA_URL="http://supervisor/core/api"\nexport HA_CONFIG_PATH="/config"\necho "Starting HA OpenAPI Server v4.0.22..."\nif [ -n "$SUPERVISOR_TOKEN" ]; then\n  echo "✓ Supervisor token is present"\nelse\n  echo "✗ Warning: SUPERVISOR_TOKEN not found"\nfi\nexec python3 -u /config/ha-openapi-server/server.py\n' > /app/run.sh && chmod +x /app/run.sh

ENV PYTHONUNBUFFERED=1
EXPOSE 8001
CMD ["/app/run.sh"]
