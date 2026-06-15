# Changed from buster to slim (which uses the newer, active Debian bookworm)
FROM python:3.10-slim

WORKDIR /KuttuBot

# Update and install crucial system dependencies (git, mediainfo, ffmpeg)
RUN apt-get update && apt-get install -y \
    git \
    mediainfo \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them securely
COPY requirements.txt .
RUN pip3 install -U pip && pip3 install --no-cache-dir -U -r requirements.txt

# Copy ALL your bot files into the container
COPY . .

# Ensure start.sh has execution permissions
RUN chmod +x start.sh

# Start the bot
CMD ["python3", "bot.py"]
