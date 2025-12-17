FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app

EXPOSE 8000

# Run prestart script (e.g., checks DB connection, runs migrations)
COPY scripts/prestart.sh /usr/local/bin/prestart.sh
RUN chmod +x /usr/local/bin/prestart.sh
ENTRYPOINT ["/usr/local/bin/prestart.sh"]

# Command to run the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
