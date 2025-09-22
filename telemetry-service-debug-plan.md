# План дебага telemetry-service (худший сценарий)

## Проблема
```bash
curl -f http://localhost:8082/health
curl: (56) Recv failure: Connection reset by peer
```

Telemetry-service не работает в Docker. Ниже представлен пошаговый план дебага в худшем случае, когда каждая попытка не работает.

## 1. Проверка статуса контейнера и базовой связности

```bash
# Проверить статус всех контейнеров
cd apps && docker-compose ps

# Проверить логи telemetry-service
docker-compose logs telemetry-service --tail=100

# Проверить, запущен ли контейнер
docker ps -a | grep telemetry

# Попробовать подключиться к контейнеру
docker-compose exec telemetry-service /bin/bash

# Проверить процессы внутри контейнера
docker-compose exec telemetry-service ps aux
```

## 2. Проверка Docker build и целостности образа

```bash
# Пересобрать образ с нуля
docker-compose build --no-cache telemetry-service

# Проверить, что образ создался
docker images | grep telemetry

# Запустить контейнер отдельно для диагностики
docker run -it --rm -p 8082:8082 apps_telemetry-service

# Проверить Dockerfile на ошибки
docker build -t test-telemetry ./telemetry-service/
```

## 3. Тест минимального сервиса без зависимостей

```bash
# Dockerfile уже настроен на main_minimal.py
# Запустить только telemetry-service без зависимостей
docker-compose up telemetry-service --no-deps

# Проверить доступность
curl -f http://localhost:8082/health
curl -f http://localhost:8082/
curl -f http://localhost:8082/test

# Проверить логи в реальном времени
docker-compose logs -f telemetry-service
```

## 4. Проверка сетевой связности и привязки портов

```bash
# Проверить, что порт 8082 не занят на хосте
lsof -i :8082
netstat -tulpn | grep 8082

# Проверить Docker сеть
docker network ls
docker network inspect apps_smarthome-network

# Проверить привязку портов в контейнере
docker-compose exec telemetry-service netstat -tulpn

# Тест с другим портом (изменить docker-compose.yml)
# ports: "8083:8082"
```

## 5. Проверка зависимых сервисов (InfluxDB, Redis)

```bash
# Запустить только зависимости
docker-compose up influxdb redis -d

# Проверить их здоровье
docker-compose ps influxdb redis
curl -f http://localhost:8086/ping
redis-cli -h localhost -p 6379 ping

# Проверить логи зависимостей
docker-compose logs influxdb --tail=50
docker-compose logs redis --tail=50

# Проверить подключение из telemetry-service
docker-compose exec telemetry-service ping influxdb
docker-compose exec telemetry-service ping redis
```

## 6. Дебаг запуска приложения и инициализации

```bash
# Проверить импорты внутри контейнера
docker-compose exec telemetry-service python -c "import app.main_minimal; print('Import OK')"

# Запустить с подробным логированием
docker-compose exec telemetry-service python -m uvicorn app.main_minimal:app --host 0.0.0.0 --port 8082 --log-level debug

# Проверить Python и зависимости
docker-compose exec telemetry-service python --version
docker-compose exec telemetry-service pip list

# Проверить файловую систему
docker-compose exec telemetry-service ls -la /app/
docker-compose exec telemetry-service ls -la /app/app/
```

## 7. Проверка ресурсных ограничений и лимитов

```bash
# Проверить ресурсы Docker
docker system df
docker system prune -f

# Проверить память и CPU
docker stats
free -h
top

# Проверить логи системы
dmesg | tail -50

# Добавить ресурсные лимиты в docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 512M
#       cpus: '0.5'
```

## 8. Проверка конфигурации и переменных окружения

```bash
# Проверить переменные окружения в контейнере
docker-compose exec telemetry-service env | grep -E "(INFLUX|REDIS|LOG|PYTHON)"

# Проверить config.py на ошибки
docker-compose exec telemetry-service python -c "from app.config import get_settings; print(get_settings())"

# Создать .env файл с явными значениями
cat > apps/.env << EOF
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=telemetry-token
INFLUXDB_ORG=smart-home
INFLUXDB_BUCKET=telemetry
REDIS_HOST=redis
REDIS_PORT=6379
LOG_LEVEL=DEBUG
EOF
```

## 9. Тест с другими версиями Python/FastAPI

```bash
# Изменить Dockerfile:
# FROM python:3.10-slim AS base
# или
# FROM python:3.12-slim AS base

# Обновить requirements.txt до последних версий:
# fastapi==0.108.0
# uvicorn==0.25.0
# pydantic==2.6.0

# Пересобрать и протестировать
docker-compose build --no-cache telemetry-service
docker-compose up telemetry-service --no-deps
```

## 10. Полная пересборка с чистым окружением

```bash
# Остановить все контейнеры
docker-compose down -v

# Удалить все образы и данные
docker system prune -a -f
docker volume prune -f
docker network prune -f

# Очистить кэш Docker
docker builder prune -a -f

# Пересобрать все с нуля
docker-compose build --no-cache
docker-compose up -d

# Проверить пошагово
docker-compose up influxdb redis -d
sleep 30
docker-compose up telemetry-service --no-deps
```

## 11. ПОСЛЕДНИЙ ВАРИАНТ: Удаление telemetry-service из проекта

Если ничего не помогает, удалить telemetry-service полностью:

### Шаги удаления:

1. **Удалить из docker-compose.yml:**
   - Секцию `telemetry-service`
   - Зависимость `telemetry-service` в секции `app`
   - Зависимость `telemetry-service` в секции `device-service`

2. **Удалить переменные окружения:**
   - `TELEMETRY_SERVICE_URL` из всех сервисов

3. **Удалить файлы:**
   ```bash
   rm -rf apps/telemetry-service/
   ```

4. **Обновить код других сервисов:**
   - Убрать интеграцию с telemetry-service из device-service
   - Убрать TELEMETRY_SERVICE_URL из smart_home

5. **Обновить документацию:**
   - Удалить telemetry-service из архитектурных диаграмм
   - Обновить README.md
   - Обновить API документацию

6. **Опционально удалить InfluxDB:**
   ```bash
   # Если InfluxDB больше не нужен
   # Удалить секцию influxdb из docker-compose.yml
   # Удалить volume influxdb_data
   ```

### Файлы для изменения при удалении:

- `apps/docker-compose.yml` - удалить секцию telemetry-service и зависимости
- `apps/device-service/` - убрать интеграцию с telemetry-service
- `apps/smart_home/` - убрать TELEMETRY_SERVICE_URL
- `docs/` - обновить архитектурные диаграммы
- `README.md` - обновить описание сервисов

## Возможные причины проблем:

1. **Проблемы с зависимостями** - InfluxDB или Redis не запускаются или недоступны
2. **Сетевые проблемы** - неправильная конфигурация Docker сети
3. **Проблемы с портами** - конфликт портов или неправильная привязка
4. **Ошибки в коде** - проблемы с импортами, инициализацией или синтаксисом
5. **Ресурсные ограничения** - недостаток памяти, CPU или дискового пространства
6. **Проблемы с образом** - поврежденный Docker образ или проблемы при сборке
7. **Проблемы с правами доступа** - неправильные права на файлы или директории
8. **Проблемы с Python окружением** - несовместимые версии пакетов

## Диагностические команды для быстрой проверки:

```bash
# Быстрая диагностика
cd apps
docker-compose ps
docker-compose logs telemetry-service --tail=20
curl -f http://localhost:8082/health || echo "Service not responding"
docker-compose exec telemetry-service python -c "print('Python works')" || echo "Python not working"
```

Этот план покрывает все возможные сценарии от простых до критических, с финальным вариантом полного удаления сервиса из проекта.
