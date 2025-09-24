# Задание 4 - Итоговый отчет: Создание и документирование API

## Краткое резюме

Разработаны полные спецификации API для микросервисной экосистемы "Тёплый дом", включающие REST API для синхронного взаимодействия и AsyncAPI для событийно-ориентированной архитектуры. Созданы детальные контракты взаимодействия с примерами запросов и ответов.

## 1. Выбор типов API

### 1.1 REST API (Синхронное взаимодействие)

**Применение**:
- Операции CRUD с сущностями
- Запросы данных, требующие немедленного ответа
- Команды управления устройствами
- Аутентификация и авторизация

**Микросервисы с REST API**:
- **User Service** (порт 8083) - управление пользователями и аутентификация
- **Home Service** (порт 8084) - управление домами и комнатами
- **Device Service** (порт 8081) - управление устройствами и отправка команд
- **Automation Service** (порт 8085) - управление сценариями автоматизации
- **Notification Service** (порт 8086) - управление уведомлениями

### 1.2 AsyncAPI (Асинхронное взаимодействие)

**Применение**:
- Обработка событий между микросервисами
- Потоковая передача телеметрии
- Уведомления о изменениях состояния
- Выполнение сценариев автоматизации

**Основные каналы событий**:
- **device.events** - события устройств
- **telemetry.data** - потоковые данные телеметрии
- **automation.events** - события автоматизации
- **notification.events** - события уведомлений

## 2. Разработанные REST API спецификации

### 2.1 Device Service API

**Файл**: [`device-service-openapi.yaml`](./device-service-openapi.yaml)

#### Ключевые endpoints:

**Управление устройствами**:
- `GET /devices` - получение списка устройств с фильтрацией
- `GET /devices/{deviceId}` - получение детальной информации об устройстве
- `POST /devices` - регистрация нового устройства
- `PUT /devices/{deviceId}` - обновление информации об устройстве
- `DELETE /devices/{deviceId}` - удаление устройства

**Управление командами**:
- `POST /devices/{deviceId}/commands` - отправка команды устройству
- `GET /devices/{deviceId}/commands/{commandId}` - получение статуса команды

**Справочная информация**:
- `GET /device-types` - получение списка типов устройств

#### Особенности реализации:

**Аутентификация**: JWT Bearer токены
**Авторизация**: Scope-based доступ (devices:read, devices:write, devices:command)
**Валидация**: Строгая валидация входных данных с детальными сообщениями об ошибках
**Пагинация**: Поддержка limit/offset для списков
**Фильтрация**: Множественные параметры фильтрации (home_id, room_id, type, status)

#### Примеры использования:

**Получение списка устройств**:
```http
GET /api/v1/devices?home_id=home-uuid&status=active&limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Отправка команды устройству**:
```http
POST /api/v1/devices/550e8400-e29b-41d4-a716-446655440000/commands
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "command": "set_temperature",
  "parameters": {
    "temperature": 24.0,
    "mode": "heat"
  },
  "timeout": 30
}
```

### 2.2 User Service API

#### Ключевые endpoints:

**Аутентификация**:
- `POST /auth/login` - аутентификация пользователя
- `POST /auth/refresh` - обновление токена
- `POST /auth/logout` - выход из системы

**Управление пользователями**:
- `GET /users/me` - получение информации о текущем пользователе
- `PUT /users/me` - обновление профиля пользователя
- `POST /users/register` - регистрация нового пользователя

### 2.3 Home Service API

#### Ключевые endpoints:

**Управление домами**:
- `GET /homes` - получение списка домов пользователя
- `POST /homes` - создание нового дома
- `GET /homes/{homeId}` - получение информации о доме
- `PUT /homes/{homeId}` - обновление информации о доме

**Управление комнатами**:
- `GET /homes/{homeId}/rooms` - получение списка комнат
- `POST /homes/{homeId}/rooms` - создание новой комнаты
- `PUT /homes/{homeId}/rooms/{roomId}` - обновление комнаты

### 2.4 Automation Service API

#### Ключевые endpoints:

**Управление сценариями**:
- `GET /scenarios` - получение списка сценариев
- `POST /scenarios` - создание нового сценария
- `GET /scenarios/{scenarioId}` - получение сценария
- `PUT /scenarios/{scenarioId}` - обновление сценария
- `DELETE /scenarios/{scenarioId}` - удаление сценария

**Выполнение сценариев**:
- `POST /scenarios/{scenarioId}/execute` - ручное выполнение сценария
- `GET /scenarios/{scenarioId}/executions` - история выполнения

## 3. AsyncAPI спецификация

**Файл**: [`smart-home-asyncapi.yaml`](./smart-home-asyncapi.yaml)

### 3.1 Каналы событий

#### device.events
**Назначение**: События, связанные с устройствами

**Типы событий**:
- `DeviceStatusChanged` - изменение статуса устройства
- `DeviceCommandExecuted` - выполнение команды устройства
- `DeviceRegistered` - регистрация нового устройства

**Пример события**:
```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440001",
  "eventType": "DeviceStatusChanged",
  "deviceId": "550e8400-e29b-41d4-a716-446655440000",
  "deviceName": "Living Room Thermostat",
  "oldStatus": "active",
  "newStatus": "offline",
  "timestamp": "2025-09-12T16:25:00Z",
  "metadata": {
    "reason": "network_timeout",
    "last_seen": "2025-09-12T16:20:00Z"
  }
}
```

#### telemetry.data
**Назначение**: Потоковые данные телеметрии

**Типы событий**:
- `MeasurementReceived` - получение новых измерений
- `AlertTriggered` - срабатывание предупреждения

**Пример события**:
```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440004",
  "eventType": "MeasurementReceived",
  "deviceId": "550e8400-e29b-41d4-a716-446655440000",
  "measurements": [
    {
      "type": "temperature",
      "value": 23.5,
      "unit": "°C",
      "quality": "good"
    },
    {
      "type": "humidity",
      "value": 45.2,
      "unit": "%",
      "quality": "good"
    }
  ],
  "timestamp": "2025-09-12T16:25:00Z"
}
```

#### automation.events
**Назначение**: События автоматизации и сценариев

**Типы событий**:
- `ScenarioTriggered` - запуск сценария
- `ScenarioExecuted` - завершение выполнения сценария
- `ExecuteDeviceCommand` - команда выполнения действия на устройстве

#### notification.events
**Назначение**: События системы уведомлений

**Типы событий**:
- `SendNotification` - запрос на отправку уведомления
- `NotificationDelivered` - подтверждение доставки уведомления

### 3.2 Операции (Operations)

**Публикация событий**:
- `publishDeviceStatusChanged` - публикация изменения статуса устройства
- `publishMeasurementData` - публикация данных телеметрии
- `publishScenarioEvent` - публикация событий сценариев
- `publishNotificationRequest` - публикация запроса уведомления

**Подписка на события**:
- `subscribeToDeviceEvents` - подписка на события устройств
- `subscribeToTelemetryData` - подписка на данные телеметрии
- `subscribeToAutomationEvents` - подписка на события автоматизации
- `subscribeToNotificationEvents` - подписка на события уведомлений

## 4. Стандартизация API

### 4.1 Коды ответов HTTP

#### Успешные ответы:
- **200 OK** - запрос выполнен успешно
- **201 Created** - ресурс создан успешно
- **202 Accepted** - запрос принят к обработке (асинхронные операции)
- **204 No Content** - запрос выполнен, содержимое отсутствует

#### Клиентские ошибки:
- **400 Bad Request** - некорректный запрос
- **401 Unauthorized** - требуется аутентификация
- **403 Forbidden** - доступ запрещен
- **404 Not Found** - ресурс не найден
- **409 Conflict** - конфликт данных
- **422 Unprocessable Entity** - ошибка валидации данных
- **429 Too Many Requests** - превышен лимит запросов

#### Серверные ошибки:
- **500 Internal Server Error** - внутренняя ошибка сервера
- **502 Bad Gateway** - ошибка шлюза
- **503 Service Unavailable** - сервис недоступен
- **504 Gateway Timeout** - таймаут шлюза

### 4.2 Стандартный формат ошибок

```json
{
  "error": {
    "code": "DEVICE_NOT_FOUND",
    "message": "Device with ID 550e8400-e29b-41d4-a716-446655440000 not found",
    "details": {
      "device_id": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": "2025-09-12T16:25:00Z",
      "trace_id": "trace-uuid"
    }
  }
}
```

### 4.3 Аутентификация и авторизация

#### JWT Bearer Token
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Области доступа (Scopes):
- `devices:read` - чтение информации об устройствах
- `devices:write` - управление устройствами
- `devices:command` - отправка команд устройствам
- `homes:read` - чтение информации о домах
- `homes:write` - управление домами
- `scenarios:read` - чтение сценариев
- `scenarios:write` - управление сценариями
- `scenarios:execute` - выполнение сценариев

### 4.4 Версионирование API

- **URL Versioning**: `/api/v1/`, `/api/v2/`
- **Обратная совместимость**: Минорные изменения обратно совместимы
- **Жизненный цикл**: Поддержка предыдущих версий в течение 12 месяцев

### 4.5 Rate Limiting

#### Лимиты по умолчанию:
- **Аутентифицированные пользователи**: 1000 запросов/час
- **Команды устройствам**: 100 команд/час на устройство
- **Создание сценариев**: 50 операций/час

#### Заголовки ответа:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1694520000
```

## 5. Примеры интеграции

### 5.1 Сценарий: Автоматическое управление температурой

**1. Получение данных телеметрии (AsyncAPI)**:
```json
{
  "eventType": "MeasurementReceived",
  "deviceId": "thermostat-001",
  "measurements": [
    {"type": "temperature", "value": 18.0, "unit": "°C"}
  ]
}
```

**2. Срабатывание сценария (AsyncAPI)**:
```json
{
  "eventType": "ScenarioTriggered",
  "scenarioId": "heating-scenario",
  "triggeredBy": "temperature_threshold"
}
```

**3. Выполнение команды устройству (REST API)**:
```http
POST /api/v1/devices/thermostat-001/commands
{
  "command": "set_temperature",
  "parameters": {"temperature": 22.0}
}
```

### 5.2 Сценарий: Уведомление о проблеме с устройством

**1. Изменение статуса устройства (AsyncAPI)**:
```json
{
  "eventType": "DeviceStatusChanged",
  "deviceId": "sensor-001",
  "newStatus": "error"
}
```

**2. Отправка уведомления (AsyncAPI)**:
```json
{
  "eventType": "SendNotification",
  "userId": "user-001",
  "title": "Device Error",
  "message": "Sensor in kitchen has encountered an error"
}
```

## 6. Инструменты разработки и тестирования

### 6.1 Swagger UI
- Интерактивная документация REST API
- Возможность тестирования endpoints
- Автогенерация клиентских SDK

### 6.2 AsyncAPI Studio
- Визуализация событийной архитектуры
- Валидация AsyncAPI спецификаций
- Генерация документации

### 6.3 Postman Collections
- Готовые коллекции для тестирования API
- Автоматизированные тесты
- Мониторинг API

### 6.4 Mock Servers
- Заглушки для разработки
- Тестирование интеграций
- Параллельная разработка команд

## 7. Мониторинг и наблюдаемость API

### 7.1 Метрики производительности
- Время ответа API (latency)
- Пропускная способность (throughput)
- Частота ошибок (error rate)
- Доступность сервисов (availability)

### 7.2 Трассировка запросов
- Distributed tracing с Jaeger
- Корреляция запросов между сервисами
- Анализ узких мест производительности

### 7.3 Логирование
- Структурированные логи в JSON формате
- Централизованное логирование через ELK Stack
- Корреляция логов с trace ID

## 8. Безопасность API

### 8.1 Защита от атак
- **Rate Limiting** - защита от DDoS
- **Input Validation** - защита от injection атак
- **CORS** - контроль доступа из браузеров
- **HTTPS Only** - шифрование трафика

### 8.2 Аудит и мониторинг
- Логирование всех API вызовов
- Мониторинг подозрительной активности
- Алерты на аномальное поведение

## Заключение

Разработанные API спецификации обеспечивают:

✅ **Четкие контракты** взаимодействия между микросервисами
✅ **Синхронное взаимодействие** через REST API для операций CRUD
✅ **Асинхронное взаимодействие** через события для реактивной обработки
✅ **Стандартизированные форматы** запросов и ответов
✅ **Безопасность** через JWT аутентификацию и авторизацию
✅ **Масштабируемость** через rate limiting и версионирование
✅ **Наблюдаемость** через трассировку и мониторинг
✅ **Готовность к реализации** с детальными примерами

API готовы для реализации и интеграции микросервисов в экосистеме "Тёплый дом", обеспечивая надежное и эффективное взаимодействие между всеми компонентами системы.

---

**Созданные файлы API спецификаций**:
- [`task4-api-design.md`](./task4-api-design.md) - детальное описание API дизайна
- [`device-service-openapi.yaml`](./device-service-openapi.yaml) - OpenAPI спецификация Device Service
- [`smart-home-asyncapi.yaml`](./smart-home-asyncapi.yaml) - AsyncAPI спецификация для событий