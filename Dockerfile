FROM python:3.10-slim as base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1

ARG PIPENV_FLAGS

WORKDIR /app

COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv
RUN pipenv install --system ${PIPENV_FLAGS}
COPY . /app/

CMD ["uvicorn", "main:app",  "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]