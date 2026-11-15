FROM python:3.11-slim

# Install cron and timezone data
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir requests

# Copy application files
COPY currency_exchange_rate.py /app/
COPY cronjob /etc/cron.d/currency-cron
COPY entrypoint.sh /app/entrypoint.sh

# Set permissions
RUN chmod 0644 /etc/cron.d/currency-cron && \
    chmod +x /app/entrypoint.sh && \
    mkdir -p /data

# Start the container
ENTRYPOINT ["/app/entrypoint.sh"]
