FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code and environment file
COPY discord_bot.py .
COPY .env .

# Create logs directory
RUN mkdir -p /app/logs

# Run the bot
CMD ["python", "discord_bot.py"]
