# Линтеры и форматтеры

### В проекте используются следующие инструменты для поддержания качества кода:

* ruff — линтер и автоформаттер (замена flake8 + isort + часть pylint)
* mypy — проверка типов
* pre-commit — автоматический запуск проверок перед коммитами

## Установка

#### Все инструменты добавлены в зависимости через Poetry. Для установки необходимо:

#### Клонировать репозиторий:

* git clone https://github.com/KateNailBotTeam/KateNailBot
* cd KateNailBot

#### Установить зависимости и активировать окружение:

* poetry install
* poetry shell

#### Установить pre-commit хуки:

* poetry run pre-commit install


## Конфигурация

#### Все настройки находятся в pyproject.toml:
* ruff: секции [tool.ruff], [tool.ruff.lint], [tool.ruff.format]
* mypy: секция [tool.mypy]


## Для запуска проверок вручную:

#### Линтинг с авто-исправлениями
* poetry run ruff check --fix .

#### Форматирование кода
* poetry run ruff format .

#### Проверка типов
* poetry run mypy .

## Автоматические проверки при коммитах

#### При каждом git commit автоматически выполняются:

* ruff (с авто-исправлением)
* ruff format
* mypy

#### Для запуска всех проверок вручную на всех файлах:
* poetry run pre-commit run --all-files
