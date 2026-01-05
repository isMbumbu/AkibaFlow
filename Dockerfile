FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ADD THIS
RUN apt-get update \
    && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app

EXPOSE 8000

COPY scripts/prestart.sh /usr/local/bin/prestart.sh
RUN chmod +x /usr/local/bin/prestart.sh

ENTRYPOINT ["/usr/local/bin/prestart.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
