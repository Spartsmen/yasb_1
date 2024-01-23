FROM python:3.10
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y libpq-dev
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install
COPY . /app/
WORKDIR /app/Telegram_bot
CMD ["poetry", "run", "python", "py_telegram_bot.py"]
