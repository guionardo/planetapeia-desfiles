ARG PYTHON_VERSION=3.10-slim-bullseye

FROM python:${PYTHON_VERSION} as base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies.
RUN apt-get update && apt-get install -y \
    libpq-dev \
    libglib2.0-0 libsm6 libxrender1 libxext6 ffmpeg \
    # gcc \
    && apt-get autoremove \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

FROM base

RUN mkdir -p /code

WORKDIR /code

COPY pyproject.toml poetry.lock /code/
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction
COPY ./planetapeia_desfiles/ /code

ENV SECRET_KEY "9Mk8lOttfVCL1Q2UP1aw2rGxP7syAVz8uHRpMhvEP85pkFphoG"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "planetapeia_desfiles.wsgi"]
