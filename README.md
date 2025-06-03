# Линтеры и форматтеры

### В проекте используются следующие инструменты для поддержания качества кода:

* ruff — линтер и автоформаттер (замена flake8 + isort + часть pylint)
* mypy — проверка типов
* pre-commit — автоматический запуск проверок перед коммитами

## Установка

#### Все инструменты добавлены в зависимости через Poetry. Для установки необходимо:

#### Клонировать репозиторий:

* `git clone https://github.com/KateNailBotTeam/KateNailBot`
* `cd KateNailBot`

#### Установить зависимости и активировать окружение:

* `poetry install`
* `poetry shell`

#### Установить pre-commit хуки:

* `poetry run pre-commit install`


## Конфигурация

#### Все настройки находятся в pyproject.toml:
* ruff: секции [tool.ruff], [tool.ruff.lint], [tool.ruff.format]
* mypy: секция [tool.mypy]


## Для запуска проверок вручную:

#### Линтинг с авто-исправлениями
* `poetry run ruff check --fix .`

#### Форматирование кода
* `poetry run ruff format .`

#### Проверка типов
* `poetry run mypy .`

## Автоматические проверки при коммитах

#### При каждом git commit автоматически выполняются:

* ruff (с авто-исправлением)
* ruff format
* mypy

#### Для запуска всех проверок вручную на всех файлах:
* `poetry run pre-commit run --all-files`


# Тестирование проекта и обеспечение качества кода

### В проекте используется pytest с поддержкой асинхронных тестов (pytest-asyncio) и измерением покрытия кода (pytest-cov).

#### Все тесты находятся в директории tests, и разделены на
* **Unit-тесты**: покрывают бизнес-логику, хендлеры и вспомогательные функции.
* **Моки Telegram API**: реальные запросы в Telegram не выполняются — все методы заменены на AsyncMock.
* В дальнейшем планируется добавить **интеграционные тесты**, которые будут взаимодействовать с внешними сервисами и БД.

### Фикстуры
* Используются фикстуры pytest для моков сообщений, обновлений, методов бота и диспетчера. Это позволяет писать простые и изолированные тесты хендлеров без зависимости от Telegram API или реального состояния.

## Ручной запуск проверок pytest

#### Убедитесь что установлены зависимости и активировано окружение:
* `poetry install`
* `poetry shell`

#### Убедитесь что установлены pre-commit хуки:
* `poetry run pre-commit install`

### Ручной запуск тестов производится командой
* `poetry run pytest`

#### По умолчанию используется следующие настройки:
* Путь к исходному коду: src
* Каталог с тестами: tests
* Режим asyncio: auto
* Отчёт о покрытии: --cov=src --cov-report=term-missing
* Scope событийного цикла: module (один loop на файл)

#### Фильтрация по маркерам
* Запустить только unit-тесты:
`    poetry run pytest -m "unit"`
* Исключить медленные тесты:
`poetry run pytest -m "not slow"`
* Только интеграционные тесты:
`poetry run pytest -m "integration"`

#### Для отображения покрытия кода
* `poetry run pytest --cov=src --cov-report=term-missing`


# Docker Compose для KateNailBot

#### Команды для работы
Сборка и запуск:
* `docker compose up -d`

Собрать и запустить только бота:
* `docker compose up -d bot`

Остановить все сервисы: 
* `docker compose down`

Остановить с удалением volumes:
* `docker compose down -v`

Просмотр логов бота:
* `docker compose logs -f bot`

Просмотр логов тестов
* `docker compose logs -f tests`

Запустить тесты (сервис tests автоматически останавливается после выполнения)
* `docker compose run --rm tests`

### Настройка окружения
* Скопируйте .env.example в .env

* Заполните необходимые переменные:
TELEGRAM_BOT_TOKEN - токен Telegram бота

### Рекомендации по разработке
* Для разработки использовать:
`docker compose up -d bot`

* Перед коммитом запускать тесты:
`docker compose run --rm tests`

### Если возникают проблемы с зависимостями, необходимо:

* Удалить контейнеры и volumes:
`docker compose down -v`

* Пересобрать образы:
`docker compose build --no-cache`

* Запустить заново:
`docker compose up -d`
