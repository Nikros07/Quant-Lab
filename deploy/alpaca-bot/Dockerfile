FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY trendbot ./trendbot
ENV PYTHONUNBUFFERED=1
# Läuft einmal und beendet sich -> per Cron/Scheduler starten (siehe README)
ENTRYPOINT ["python", "-m", "trendbot"]
CMD ["run"]
