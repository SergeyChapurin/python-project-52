# Устанавливаем базовый образ
FROM python:3.10-slim

# Устанавливаем системные зависимости для сборки
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        libpq-dev \
        build-essential \
        gunicorn \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл pyproject.toml и poetry.lock
COPY pyproject.toml poetry.lock* /app/

# указываем, что Poetry будет использовать системное окружение вместо создания виртуального
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости проекта через Poetry
RUN poetry install

# Копируем остальной код
COPY . .

# Открываем порт 8000 для доступа к приложению
EXPOSE 8000

# Команда для запуска приложения
CMD ["gunicorn", "-w", "5", "-b", "0.0.0.0:8000", "task_manager.wsgi:application"]
