ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    git \
    bash

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies using --break-system-packages for Alpine Python
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py .
COPY run.sh .

# Make run script executable
RUN chmod a+x run.sh

# Set up environment
ENV PYTHONUNBUFFERED=1
ENV HA_URL=http://supervisor/core/api
ENV HA_CONFIG_PATH=/config

# Expose port
EXPOSE 8001

# Run
CMD [ "/app/run.sh" ]
