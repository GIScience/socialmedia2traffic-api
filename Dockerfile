FROM python:3.8

RUN apt-get update

# Create non-root user
RUN addgroup --system app && adduser --system --group app
USER app

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app/src

ENTRYPOINT ["./entrypoint.sh"]
