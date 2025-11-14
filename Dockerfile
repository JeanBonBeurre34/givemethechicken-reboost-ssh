FROM python:3.9-slim

WORKDIR /app

# Copy honeypot script
COPY givemethechicken.py /app/

# Install Paramiko only (no compiler needed)
RUN pip install --no-cache-dir paramiko

# Expose SSH port
EXPOSE 22

# Run server
CMD ["python", "givemethechicken.py"]
