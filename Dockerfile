FROM python:3.12-slim

LABEL author="Win.freez"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR app/

RUN pip install --no-cache-dir poetry==2.1.3

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . /app

CMD ["python", "-m", "src.main"]