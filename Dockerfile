FROM python:3.10-slim-buster
RUN apt-get update && apt-get install -y curl build-essential && rm -Rf /var/cache/apt/*
RUN curl -sSL https://install.python-poetry.org | python -
WORKDIR /app
COPY . .
RUN /root/.local/bin/poetry install

ENTRYPOINT ["/root/.local/bin/poetry", "run", "python", "/app/mqtt2aprs/mqtt2aprs.py"]
