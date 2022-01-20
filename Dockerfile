FROM python:3.8

RUN apt-get update

# Create non-root user
RUN addgroup --system app && adduser --system --group app_user
USER app_user

WORKDIR /app

COPY ["requirements.txt", ".env", "./"]
RUN pip install -r requirements.txt

WORKDIR /app/src

ENTRYPOINT ["./entrypoint.sh"]
