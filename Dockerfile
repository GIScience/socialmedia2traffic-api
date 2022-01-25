FROM python:3.8

RUN apt-get clean \
    && apt-get -y update

RUN apt-get -y --no-install-recommends install python3-dev build-essential

RUN pip3 install uwsgi

WORKDIR /app

COPY ["requirements.txt", ".env", "./"]
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN addgroup --system app && adduser --system --group  api
USER api

COPY ./src /app/src

WORKDIR /app/src

ENTRYPOINT ["./entrypoint.sh"]
