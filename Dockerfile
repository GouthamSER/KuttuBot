FROM python:3.10-slim-buster

# Set the working directory first so all following commands happen inside it
WORKDIR /KuttuBot

# Update and install crucial system dependencies (git, mediainfo, ffmpeg)
# Cleaning up apt lists afterwards saves RAM and storage space on your VPS
RUN apt-get update && apt-get install -y \
    git \
    mediainfo \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them securely
COPY requirements.txt .
RUN pip3 install -U pip && pip3 install --no-cache-dir -U -r requirements.txt

# CRITICAL FIX: Copy ALL your bot files (bot.py, plugins, helper, etc.) into the container
COPY . .

# Ensure start.sh has execution permissions, just in case you need it
RUN chmod +x start.sh

# Start the bot
CMD ["python3", "bot.py"]
