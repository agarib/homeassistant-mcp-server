ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache python3 py3-pip bash

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

RUN printf '#!/bin/bash\nset -e\nexport PORT="${PORT:-8001}"\nexport LOG_LEVEL="${LOG_LEVEL:-info}"\nexport HA_URL="http://supervisor/core/api"\nexport HA_CONFIG_PATH="/config"\necho "Starting HA OpenAPI Server v4.0.27..."\necho "DEBUG: Checking s6-overlay environment store..."\nif [ -d "/var/run/s6/container_environment" ]; then\n  echo "  Found s6 environment directory"\n  ls -la /var/run/s6/container_environment/ 2>/dev/null | head -20 || echo "  Cannot list directory"\nelse\n  echo "  No s6 environment directory found"\nfi\necho ""\necho "DEBUG: Environment variables containing TOKEN:"\nenv | grep -i token || echo "  No TOKEN variables in env"\necho ""\necho "DEBUG: Attempting to source s6 environment..."\nfor file in /var/run/s6/container_environment/*; do\n  if [ -f "$file" ]; then\n    varname=$(basename "$file")\n    varvalue=$(cat "$file")\n    export "$varname"="$varvalue"\n    if echo "$varname" | grep -qi token; then\n      echo "  Loaded $varname from s6 (length: ${#varvalue})"\n    fi\n  fi\ndone\necho ""\necho "DEBUG: Final token check:"\necho "  SUPERVISOR_TOKEN: ${SUPERVISOR_TOKEN:+PRESENT (length: ${#SUPERVISOR_TOKEN})}${SUPERVISOR_TOKEN:-MISSING}"\necho "  HASSIO_TOKEN: ${HASSIO_TOKEN:+PRESENT (length: ${#HASSIO_TOKEN})}${HASSIO_TOKEN:-MISSING}"\nif [ -n "$SUPERVISOR_TOKEN" ]; then\n  echo "✓ Using SUPERVISOR_TOKEN"\n  export HA_TOKEN="$SUPERVISOR_TOKEN"\nelif [ -n "$HASSIO_TOKEN" ]; then\n  echo "✓ Using HASSIO_TOKEN as SUPERVISOR_TOKEN"\n  export HA_TOKEN="$HASSIO_TOKEN"\n  export SUPERVISOR_TOKEN="$HASSIO_TOKEN"\nelse\n  echo "✗ No token found - API calls will fail"\nfi\necho ""\nexec python3 -u /config/ha-openapi-server/server.py\n' > /app/run.sh && chmod +x /app/run.sh

ENV PYTHONUNBUFFERED=1
EXPOSE 8001
CMD ["/app/run.sh"]
