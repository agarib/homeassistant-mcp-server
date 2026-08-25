ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache python3 py3-pip bash

WORKDIR /app
COPY requirements.txt .
RUN python3 -m pip install --break-system-packages --no-cache-dir -r requirements.txt

COPY server.py .
COPY app/ ./app/

RUN printf '#!/bin/bash\nset -e\nexport PORT="${PORT:-8001}"\nexport LOG_LEVEL="${LOG_LEVEL:-info}"\nexport HA_URL="http://supervisor/core/api"\nexport HA_CONFIG_PATH="/config"\necho "Starting HA OpenAPI Server v4.1.4..."\necho "DEBUG: Checking s6-overlay environment store..."\nif [ -d "/var/run/s6/container_environment" ]; then\n  echo "  Found s6 environment directory"\n  ls -la /var/run/s6/container_environment/ 2>/dev/null | head -20 || echo "  Cannot list directory"\nelse\n  echo "  No s6 environment directory found"\nfi\necho ""\necho "DEBUG: Environment variables containing TOKEN:"\nenv | grep -i token || echo "  No TOKEN variables in env"\necho ""\necho "DEBUG: Attempting to source s6 environment..."\nfor file in /var/run/s6/container_environment/*; do\n  if [ -f "$file" ]; then\n    echo "  Sourcing $file"\n    . "$file" 2>/dev/null || true\n  fi\ndone\necho ""\necho "DEBUG: HA_URL=$HA_URL"\necho "DEBUG: HA_CONFIG_PATH=$HA_CONFIG_PATH"\nif [ -z "$SUPERVISOR_TOKEN" ]; then\n  echo "ERROR: SUPERVISOR_TOKEN is not set!"\nfi\nexec python3 /app/server.py' > /app/run.sh && chmod +x /app/run.sh

ENV PYTHONUNBUFFERED=1
EXPOSE 8001
CMD ["/app/run.sh"]