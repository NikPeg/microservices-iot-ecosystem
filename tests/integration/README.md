# Integration Tests

Этот модуль содержит интеграционные тесты для микросервисной IoT экосистемы Smart Home.

## Структура тестов

- `conftest.py` - Конфигурация и фикстуры для тестов
- `test_health_checks.py` - Тесты проверки здоровья всех сервисов
- `test_device_service.py` - Тесты Device Service API
- `test_telemetry_service.py` - Тесты Telemetry Service API
- `test_smart_home_service.py` - Тесты Smart Home Service API
- `test_temperature_api.py` - Тесты Temperature API
- `test_integration_scenarios.py` - End-to-end интеграционные сценарии

## Установка зависимостей

```bash
cd tests/integration
pip install -r requirements.txt
```

## Запуск тестов

### Предварительные требования

1. Убедитесь, что все сервисы запущены:
```bash
cd apps
docker-compose up -d
```

2. Дождитесь готовности всех сервисов (обычно 1-2 минуты)

### Запуск всех тестов

```bash
cd tests/integration
pytest
```

### Запуск конкретных групп тестов

```bash
# Только health check тесты
pytest -m health

# Только тесты Device Service
pytest test_device_service.py

# Только интеграционные сценарии
pytest test_integration_scenarios.py

# Параллельный запуск тестов
pytest -n auto
```

### Генерация HTML отчета

```bash
pytest --html=reports/report.html --self-contained-html
```

## Переменные окружения

Можно переопределить URL сервисов через переменные окружения:

```bash
export DEVICE_SERVICE_URL="http://localhost:8081"
export TELEMETRY_SERVICE_URL="http://localhost:8082"
export TEMPERATURE_API_URL="http://localhost:8083"
export SMART_HOME_URL="http://localhost:8080"
```

## Особенности тестов

- Тесты автоматически ждут готовности всех сервисов перед выполнением
- Создаются и удаляются тестовые данные автоматически
- Поддерживается параллельное выполнение тестов
- Генерируются подробные HTML отчеты
- Тесты покрывают как отдельные сервисы, так и межсервисные взаимодействия

## Отладка

Для получения более подробной информации при отладке:

```bash
pytest -v -s --tb=long
```

Для запуска только неудачных тестов:

```bash
pytest --lf
