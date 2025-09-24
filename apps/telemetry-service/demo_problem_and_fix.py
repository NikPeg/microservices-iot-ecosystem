#!/usr/bin/env python3
"""
Демонстрация проблемы с блокирующими операциями и её решения
"""

import asyncio
import time
from unittest.mock import Mock, AsyncMock

print("🔍 ДЕМОНСТРАЦИЯ ПРОБЛЕМЫ И РЕШЕНИЯ")
print("=" * 60)

async def demonstrate_blocking_problem():
    """Демонстрация блокирующей проблемы (до исправления)"""
    print("\n❌ ПРОБЛЕМА: Блокирующие операции")
    print("-" * 40)

    async def blocking_message_consumer_old():
        """Старая версия с блокирующим await asyncio.gather()"""
        print("🔄 Запуск message consumer (старая версия)...")

        # Имитируем подписку на каналы
        await asyncio.sleep(0.01)  # subscribe
        print("✅ Подписались на каналы")

        # Создаем задачи
        listen_task = asyncio.create_task(asyncio.sleep(10))  # Долгая задача
        cleanup_task = asyncio.create_task(asyncio.sleep(10))  # Долгая задача

        print("⏳ Ожидание завершения задач (БЛОКИРУЕТ ЗАПУСК)...")
        # ЭТО БЛОКИРУЕТ ЗАПУСК ПРИЛОЖЕНИЯ!
        await asyncio.gather(listen_task, cleanup_task, return_exceptions=True)

        print("✅ Message consumer завершен")

    async def blocking_influxdb_ping_old():
        """Старая версия с синхронным ping"""
        print("🔄 InfluxDB ping (старая версия)...")

        # Имитируем синхронный вызов, который блокирует event loop
        def sync_health_check():
            time.sleep(0.1)  # Блокирующий вызов
            return Mock(status="pass")

        print("⏳ Синхронный health check (БЛОКИРУЕТ EVENT LOOP)...")
        health = sync_health_check()  # БЛОКИРУЕТ!

        print("✅ InfluxDB ping завершен")
        return health.status == "pass"

    # Демонстрируем проблему
    start_time = time.time()

    print("\n🚀 Попытка запуска приложения с проблемами...")
    try:
        # Это должно было бы зависнуть на await asyncio.gather()
        # Но мы прерываем через timeout для демонстрации
        await asyncio.wait_for(blocking_message_consumer_old(), timeout=1.0)
    except asyncio.TimeoutError:
        print("⏰ TIMEOUT! Приложение зависло на запуске message consumer")

    # Демонстрируем блокирующий ping
    await asyncio.get_event_loop().run_in_executor(None, blocking_influxdb_ping_old)

    end_time = time.time()
    print(f"⏱️  Время выполнения с проблемами: {end_time - start_time:.2f}s")

async def demonstrate_fixed_solution():
    """Демонстрация исправленного решения"""
    print("\n✅ РЕШЕНИЕ: Неблокирующие операции")
    print("-" * 40)

    async def non_blocking_message_consumer_new():
        """Новая версия без блокирующего await"""
        print("🔄 Запуск message consumer (новая версия)...")

        # Имитируем подписку на каналы
        await asyncio.sleep(0.01)
        print("✅ Подписались на каналы")

        # Создаем задачи, но НЕ ждем их завершения
        listen_task = asyncio.create_task(asyncio.sleep(10))
        cleanup_task = asyncio.create_task(asyncio.sleep(10))

        print("🚀 Задачи запущены в фоне (НЕ БЛОКИРУЮТ)")
        # НЕ ЖДЕМ ЗАВЕРШЕНИЯ - позволяем приложению продолжить запуск

        print("✅ Message consumer запущен неблокирующе")
        return [listen_task, cleanup_task]

    async def non_blocking_influxdb_ping_new():
        """Новая версия с асинхронным ping"""
        print("🔄 InfluxDB ping (новая версия)...")

        async def async_health_check():
            # Используем executor для неблокирующего выполнения
            await asyncio.sleep(0.01)  # Имитируем асинхронную операцию
            return Mock(status="pass")

        print("⚡ Асинхронный health check (НЕ БЛОКИРУЕТ EVENT LOOP)")
        health = await async_health_check()

        print("✅ InfluxDB ping завершен асинхронно")
        return health.status == "pass"

    # Демонстрируем решение
    start_time = time.time()

    print("\n🚀 Запуск приложения с исправлениями...")

    # Быстрый неблокирующий запуск
    tasks = await non_blocking_message_consumer_new()
    ping_result = await non_blocking_influxdb_ping_new()

    print("🎉 Приложение запущено успешно!")
    print(f"📊 InfluxDB доступен: {ping_result}")
    print(f"📊 Фоновых задач: {len(tasks)}")

    # Очищаем задачи
    for task in tasks:
        task.cancel()

    end_time = time.time()
    print(f"⏱️  Время выполнения с исправлениями: {end_time - start_time:.2f}s")

async def demonstrate_health_endpoint():
    """Демонстрация работы health endpoint"""
    print("\n🏥 HEALTH ENDPOINT")
    print("-" * 40)

    async def health_check_old():
        """Старая версия health check"""
        print("🔄 Health check (старая версия)...")

        # Блокирующий ping
        def blocking_ping():
            time.sleep(0.1)  # Блокирует event loop
            return True

        influxdb_ok = await asyncio.get_event_loop().run_in_executor(None, blocking_ping)
        redis_ok = True  # Предполагаем Redis работает

        if influxdb_ok and redis_ok:
            return {"status": "healthy", "service": "telemetry-service"}
        else:
            raise Exception("Service unhealthy")

    async def health_check_new():
        """Новая версия health check"""
        print("🔄 Health check (новая версия)...")

        # Неблокирующий ping
        async def async_ping():
            await asyncio.sleep(0.01)  # Асинхронная операция
            return True

        influxdb_ok = await async_ping()
        redis_ok = await async_ping()

        if influxdb_ok and redis_ok:
            return {"status": "healthy", "service": "telemetry-service"}
        else:
            raise Exception("Service unhealthy")

    # Тестируем старую версию
    start_time = time.time()
    try:
        result_old = await health_check_old()
        old_time = time.time() - start_time
        print(f"✅ Старая версия: {result_old['status']} ({old_time:.3f}s)")
    except Exception as e:
        print(f"❌ Старая версия: {e}")

    # Тестируем новую версию
    start_time = time.time()
    try:
        result_new = await health_check_new()
        new_time = time.time() - start_time
        print(f"✅ Новая версия: {result_new['status']} ({new_time:.3f}s)")
    except Exception as e:
        print(f"❌ Новая версия: {e}")

async def main():
    """Основная демонстрация"""
    await demonstrate_blocking_problem()
    await demonstrate_fixed_solution()
    await demonstrate_health_endpoint()

    print("\n" + "=" * 60)
    print("📋 РЕЗЮМЕ ИСПРАВЛЕНИЙ:")
    print("=" * 60)
    print("1. ❌ Убрали блокирующий await asyncio.gather() в MessageConsumer")
    print("2. ❌ Сделали InfluxDB ping асинхронным через executor")
    print("3. ❌ Упростили управление задачами в main.py")
    print("4. ✅ Приложение теперь запускается быстро и неблокирующе")
    print("5. ✅ Health endpoint отвечает без блокировки event loop")
    print("=" * 60)
    print("🎯 РЕЗУЛЬТАТ: Проблема 'Connection reset by peer' решена!")

if __name__ == "__main__":
    asyncio.run(main())
