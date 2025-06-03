FROM python:3.12-slim

LABEL author="Win.freez"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR app/

RUN pip install --no-cache-dir poetry==2.1.3

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY . /app

CMD ["python", "-m", "src.main"]