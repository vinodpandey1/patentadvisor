# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    gcc \
    make \
    sqlite3 \
    libsqlite3-dev \
    libssl-dev \
    zlib1g-dev && \
    wget https://www.sqlite.org/2023/sqlite-autoconf-3410200.tar.gz && \
    tar -xvzf sqlite-autoconf-3410200.tar.gz && \
    cd sqlite-autoconf-3410200 && \
    ./configure && make && make install && \
    cd .. && rm -rf sqlite-autoconf-3410200* && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY . .


EXPOSE 8000

CMD ["uvicorn", "src.controller.app:app", "--host", "0.0.0.0", "--port", "8000"]
