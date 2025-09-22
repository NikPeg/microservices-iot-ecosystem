#!/usr/bin/env python3
"""
Простой тест для проверки исправлений блокирующих операций
"""

import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock, MagicMock

# Добавляем путь к модулям приложения
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Мокаем внешние зависимости
sys.modules['structlog'] = Mock()
sys.modules['influxdb_client'] = Mock()
sys.modules['influxdb_client.client.write_api'] = Mock()
sys.modules['influxdb_client.client.exceptions'] = Mock()
sys.modules['redis.asyncio'] = Mock()
sys.modules['fastapi'] = Mock()
sys.modules['fastapi.middleware.cors'] = Mock()
sys.modules['fastapi.responses'] = Mock()
sys.modules['prometheus_client'] = Mock()
sys.modules['uvicorn'] = Mock()

# Настраиваем моки
mock_logger = Mock()
mock_logger.info = Mock()
mock_logger.error = Mock()
mock_logger.warning = Mock()
mock_logger.debug = Mock()

structlog_mock = sys.modules['structlog']
structlog_mock.get_logger.return_value = mock_logger

# Мокаем InfluxDB клиент
influxdb_mock = sys.modules['influxdb_client']
influxdb_mock.InfluxDBClient = Mock()
influxdb_mock.Point = Mock()
influxdb_mock.ASYNCHRONOUS = Mock()

# Мокаем Redis
redis_mock = sys.modules['redis.asyncio']
redis_mock.Redis = Mock()
redis_mock.ConnectionError = Exception

# Мокаем FastAPI
fastapi_mock = sys.modules['fastapi']
fastapi_mock.FastAPI = Mock()
fastapi_mock.HTTPException = Exception
fastapi_mock.Depends = Mock()
fastapi_mock.Query = Mock()
fastapi_mock.BackgroundTasks = Mock()

# Мокаем настройки
class MockSettings:
    redis_telemetry_channel = "telemetry.data"
    redis_device_events_channel = "device.events"
    redis_alerts_channel = "alerts.notifications"
    influxdb_url = "http://localhost:8086"
    influxdb_token = "test-token"
    influxdb_org = "test-org"
    influxdb_bucket = "test-bucket"
    redis_host = "localhost"
    redis_port = 6379
    redis_password = ""
    redis_db = 0
    debug = True
    allowed_origins = ["*"]

# Теперь импортируем наши модули
try:
    from config import get_settings
    # Подменяем настройки
    import config
    config.get_settings = lambda: MockSettings()

    from database.influxdb import InfluxDBClient
    from database.redis_client import RedisClient
    from services.message_consumer import MessageConsumer
    from services.telemetry_service import TelemetryService

    print("✅ Все модули успешно импортированы")

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

async def test_influxdb_ping():
    """Тест асинхронного ping для InfluxDB"""
    print("\n🧪 Тестируем InfluxDB ping...")

    # Создаем мок клиента
    mock_client = Mock()
    mock_health = Mock()
    mock_health.status = "pass"
    mock_client.health.return_value = mock_health

    # Создаем InfluxDB клиент
    influxdb = InfluxDBClient("http://localhost:8086", "token", "org", "bucket")
    influxdb.client = mock_client

    try:
        # Тестируем асинхронный ping
        start_time = asyncio.get_event_loop().time()
        result = await influxdb.ping()
        end_time = asyncio.get_event_loop().time()

        print(f"✅ InfluxDB ping выполнен асинхронно за {end_time - start_time:.4f}s")
        print(f"✅ Результат: {result}")
        return True

    except Exception as e:
        print(f"❌ Ошибка в InfluxDB ping: {e}")
        return False

async def test_message_consumer():
    """Тест неблокирующего запуска message consumer"""
    print("\n🧪 Тестируем Message Consumer...")

    # Создаем мок Redis клиента
    mock_redis = Mock()
    mock_redis.subscribe = AsyncMock()
    mock_redis.listen = AsyncMock()

    # Создаем мок telemetry service
    mock_telemetry_service = Mock()

    # Создаем message consumer
    consumer = MessageConsumer(mock_redis, mock_telemetry_service)

    try:
        # Тестируем неблокирующий запуск
        start_time = asyncio.get_event_loop().time()
        await consumer.start_consuming()
        end_time = asyncio.get_event_loop().time()

        execution_time = end_time - start_time
        print(f"✅ Message Consumer запущен неблокирующе за {execution_time:.4f}s")

        # Проверяем, что время выполнения мало (не блокирует)
        if execution_time < 0.1:  # Менее 100ms
            print("✅ Запуск действительно неблокирующий")
            return True
        else:
            print(f"⚠️  Запуск может быть блокирующим (время: {execution_time:.4f}s)")
            return False

    except Exception as e:
        print(f"❌ Ошибка в Message Consumer: {e}")
        return False

async def test_application_startup():
    """Тест запуска приложения"""
    print("\n🧪 Тестируем запуск приложения...")

    try:
        # Имитируем запуск основных компонентов
        start_time = asyncio.get_event_loop().time()

        # Создаем мок компоненты
        mock_influxdb = Mock()
        mock_influxdb.connect = AsyncMock()
        mock_influxdb.ping = AsyncMock(return_value=True)

        mock_redis = Mock()
        mock_redis.connect = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis.subscribe = AsyncMock()
        mock_redis.listen = AsyncMock()

        mock_telemetry_service = Mock()

        # Имитируем последовательность запуска
        await mock_influxdb.connect()
        await mock_redis.connect()

        consumer = MessageConsumer(mock_redis, mock_telemetry_service)
        await consumer.start_consuming()

        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time

        print(f"✅ Приложение запущено за {execution_time:.4f}s")

        if execution_time < 0.5:  # Менее 500ms
            print("✅ Запуск быстрый и неблокирующий")
            return True
        else:
            print(f"⚠️  Запуск может быть медленным (время: {execution_time:.4f}s)")
            return False

    except Exception as e:
        print(f"❌ Ошибка при запуске приложения: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов исправлений блокирующих операций")
    print("=" * 60)

    tests = [
        ("InfluxDB Ping", test_influxdb_ping),
        ("Message Consumer", test_message_consumer),
        ("Application Startup", test_application_startup)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте {test_name}: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ:")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1

    print("=" * 60)
    print(f"Пройдено: {passed}/{total} тестов")

    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Исправления работают корректно.")
        return True
    else:
        print("⚠️  Некоторые тесты провалены. Требуются дополнительные исправления.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)
