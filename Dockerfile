FROM python:3.8

RUN apt-get clean \
    && apt-get -y update

RUN apt-get -y --no-install-recommends install python3-dev build-essential postgresql postgresql-contrib

# Create non-root user
RUN adduser --system --uid 1001  api 

USER api
# RUN chown -R api /app
WORKDIR /home/api

# make poetry binaries available to the docker container user
ENV PATH=$PATH:/home/api/.local/bin

COPY ["requirements.txt", ".env", "/home/api/"]
RUN pip install --no-cache-dir -r requirements.txt
RUN pip3 install uwsgi

COPY ./src /home/api/src

WORKDIR /home/api/src

ENTRYPOINT ["./entrypoint.sh"]
