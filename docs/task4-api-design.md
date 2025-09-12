# Задание 4. Создание и документирование API

## 1. Выбор типов API

На основе архитектуры микросервисов, спроектированной в предыдущих заданиях, определены следующие типы API:

### 1.1 REST API (Синхронное взаимодействие)

**Используется для**:
- Операции CRUD с сущностями
- Запросы данных, требующие немедленного ответа
- Команды управления устройствами
- Аутентификация и авторизация

**Микросервисы с REST API**:
- **User Service** - управление пользователями и аутентификация
- **Home Service** - управление домами и комнатами
- **Device Service** - управление устройствами и отправка команд
- **Automation Service** - управление сценариями автоматизации
- **Notification Service** - управление уведомлениями

### 1.2 AsyncAPI (Асинхронное взаимодействие)

**Используется для**:
- Обработка событий между микросервисами
- Потоковая передача телеметрии
- Уведомления о изменениях состояния
- Выполнение сценариев автоматизации

**Основные события**:
- **Device Events** - события устройств (изменение состояния, данные)
- **Telemetry Events** - потоковые данные телеметрии
- **Automation Events** - события выполнения сценариев
- **Notification Events** - события отправки уведомлений

## 2. Проектирование REST API

### 2.1 Device Service API

#### Базовый URL: `http://device-service:8081/api/v1`

#### Endpoints:

##### GET /devices
**Описание**: Получение списка всех устройств пользователя

**Query Parameters**:
- `home_id` (UUID, optional) - фильтр по дому
- `room_id` (UUID, optional) - фильтр по комнате
- `type` (string, optional) - фильтр по типу устройства
- `status` (string, optional) - фильтр по статусу
- `limit` (integer, optional, default: 50) - количество записей
- `offset` (integer, optional, default: 0) - смещение

**Response**: 200 OK
```json
{
  "devices": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Living Room Thermostat",
      "serial_number": "THM-001-2024",
      "device_type": {
        "id": "device-type-uuid",
        "name": "Smart Thermostat",
        "category": "actuator"
      },
      "home_id": "home-uuid",
      "room_id": "room-uuid",
      "status": "active",
      "configuration": {
        "target_temperature": 22.0,
        "mode": "auto"
      },
      "capabilities": [
        {
          "type": "temperature_control",
          "parameters": {
            "min_temp": 10,
            "max_temp": 35
          }
        }
      ],
      "last_seen": "2025-09-12T16:00:00Z",
      "created_at": "2025-09-01T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

##### GET /devices/{deviceId}
**Описание**: Получение информации о конкретном устройстве

**Path Parameters**:
- `deviceId` (UUID, required) - идентификатор устройства

**Response**: 200 OK
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Living Room Thermostat",
  "serial_number": "THM-001-2024",
  "device_type": {
    "id": "device-type-uuid",
    "name": "Smart Thermostat",
    "category": "actuator"
  },
  "manufacturer": {
    "id": "manufacturer-uuid",
    "name": "SmartHome Inc.",
    "website": "https://smarthome.com"
  },
  "home_id": "home-uuid",
  "room_id": "room-uuid",
  "status": "active",
  "ip_address": "192.168.1.100",
  "protocol": "mqtt",
  "configuration": {
    "target_temperature": 22.0,
    "mode": "auto",
    "schedule_enabled": true
  },
  "capabilities": [
    {
      "type": "temperature_control",
      "name": "Temperature Control",
      "parameters": {
        "min_temp": 10,
        "max_temp": 35,
        "precision": 0.5
      },
      "supported_commands": ["set_temperature", "get_temperature"]
    }
  ],
  "last_seen": "2025-09-12T16:00:00Z",
  "installed_at": "2025-09-01T09:00:00Z",
  "created_at": "2025-09-01T10:00:00Z",
  "updated_at": "2025-09-12T15:30:00Z"
}
```

**Error Responses**:
- `404 Not Found` - устройство не найдено
- `403 Forbidden` - нет доступа к устройству

##### POST /devices
**Описание**: Регистрация нового устройства

**Request Body**:
```json
{
  "name": "Kitchen Smart Plug",
  "serial_number": "PLG-002-2024",
  "device_type_id": "device-type-uuid",
  "manufacturer_id": "manufacturer-uuid",
  "home_id": "home-uuid",
  "room_id": "room-uuid",
  "ip_address": "192.168.1.101",
  "protocol": "http",
  "configuration": {
    "power_limit": 2000,
    "auto_off_timeout": 3600
  }
}
```

**Response**: 201 Created
```json
{
  "id": "new-device-uuid",
  "name": "Kitchen Smart Plug",
  "serial_number": "PLG-002-2024",
  "status": "inactive",
  "created_at": "2025-09-12T16:25:00Z"
}
```

##### POST /devices/{deviceId}/commands
**Описание**: Отправка команды устройству

**Path Parameters**:
- `deviceId` (UUID, required) - идентификатор устройства

**Request Body**:
```json
{
  "command": "set_temperature",
  "parameters": {
    "temperature": 24.0,
    "mode": "heat"
  },
  "timeout": 30
}
```

**Response**: 202 Accepted
```json
{
  "command_id": "command-uuid",
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "command": "set_temperature",
  "status": "pending",
  "issued_at": "2025-09-12T16:25:00Z",
  "expires_at": "2025-09-12T16:25:30Z"
}
```

##### GET /devices/{deviceId}/commands/{commandId}
**Описание**: Получение статуса выполнения команды

**Response**: 200 OK
```json
{
  "id": "command-uuid",
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "command": "set_temperature",
  "parameters": {
    "temperature": 24.0,
    "mode": "heat"
  },
  "status": "completed",
  "result": {
    "success": true,
    "message": "Temperature set successfully",
    "current_temperature": 24.0,
    "execution_time": "1.2s"
  },
  "issued_at": "2025-09-12T16:25:00Z",
  "executed_at": "2025-09-12T16:25:01Z"
}
```

### 2.2 User Service API

#### Базовый URL: `http://user-service:8083/api/v1`

##### POST /auth/login
**Описание**: Аутентификация пользователя

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response**: 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "refresh_token_here",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "status": "active"
  }
}
```

##### GET /users/me
**Описание**: Получение информации о текущем пользователе

**Headers**:
- `Authorization: Bearer {access_token}`

**Response**: 200 OK
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "status": "active",
  "email_verified": true,
  "profile": {
    "timezone": "Europe/Moscow",
    "language": "ru",
    "preferences": {
      "notifications_enabled": true,
      "theme": "dark"
    }
  },
  "subscription": {
    "plan": "premium",
    "status": "active",
    "expires_at": "2025-12-31T23:59:59Z"
  },
  "created_at": "2025-01-01T00:00:00Z"
}
```

### 2.3 Home Service API

#### Базовый URL: `http://home-service:8084/api/v1`

##### GET /homes
**Описание**: Получение списка домов пользователя

**Response**: 200 OK
```json
{
  "homes": [
    {
      "id": "home-uuid",
      "name": "My Smart Home",
      "address": "123 Smart Street, Tech City",
      "timezone": "Europe/Moscow",
      "rooms_count": 5,
      "devices_count": 12,
      "created_at": "2025-09-01T10:00:00Z"
    }
  ]
}
```

##### GET /homes/{homeId}/rooms
**Описание**: Получение списка комнат в доме

**Response**: 200 OK
```json
{
  "rooms": [
    {
      "id": "room-uuid",
      "name": "Living Room",
      "type": "living_room",
      "floor": 1,
      "area_sqm": 25.5,
      "devices_count": 3
    }
  ]
}
```

### 2.4 Automation Service API

#### Базовый URL: `http://automation-service:8085/api/v1`

##### GET /scenarios
**Описание**: Получение списка сценариев пользователя

**Response**: 200 OK
```json
{
  "scenarios": [
    {
      "id": "scenario-uuid",
      "name": "Evening Comfort",
      "description": "Automatically adjust temperature and lighting in the evening",
      "enabled": true,
      "home_id": "home-uuid",
      "triggers": [
        {
          "type": "time_based",
          "configuration": {
            "time": "19:00",
            "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
          }
        }
      ],
      "actions": [
        {
          "type": "device_command",
          "configuration": {
            "device_id": "thermostat-uuid",
            "command": "set_temperature",
            "parameters": {
              "temperature": 22.0
            }
          }
        }
      ],
      "last_executed": "2025-09-11T19:00:00Z",
      "execution_count": 45
    }
  ]
}
```

##### POST /scenarios/{scenarioId}/execute
**Описание**: Ручное выполнение сценария

**Response**: 202 Accepted
```json
{
  "execution_id": "execution-uuid",
  "scenario_id": "scenario-uuid",
  "status": "running",
  "started_at": "2025-09-12T16:25:00Z"
}
```

## 3. Проектирование AsyncAPI

### 3.1 Device Events Channel

**Channel**: `device.events`

#### Device Status Changed Event
```yaml
deviceStatusChanged:
  summary: Device status has changed
  payload:
    type: object
    properties:
      eventId:
        type: string
        format: uuid
      eventType:
        type: string
        enum: [DeviceStatusChanged]
      deviceId:
        type: string
        format: uuid
      oldStatus:
        type: string
        enum: [active, inactive, error, maintenance, offline]
      newStatus:
        type: string
        enum: [active, inactive, error, maintenance, offline]
      timestamp:
        type: string
        format: date-time
      metadata:
        type: object
    example:
      eventId: "event-uuid"
      eventType: "DeviceStatusChanged"
      deviceId: "550e8400-e29b-41d4-a716-446655440000"
      oldStatus: "active"
      newStatus: "offline"
      timestamp: "2025-09-12T16:25:00Z"
      metadata:
        reason: "network_timeout"
        last_seen: "2025-09-12T16:20:00Z"
```

#### Device Command Executed Event
```yaml
deviceCommandExecuted:
  summary: Device command has been executed
  payload:
    type: object
    properties:
      eventId:
        type: string
        format: uuid
      eventType:
        type: string
        enum: [DeviceCommandExecuted]
      commandId:
        type: string
        format: uuid
      deviceId:
        type: string
        format: uuid
      command:
        type: string
      parameters:
        type: object
      result:
        type: object
        properties:
          success:
            type: boolean
          message:
            type: string
          executionTime:
            type: string
      timestamp:
        type: string
        format: date-time
    example:
      eventId: "event-uuid"
      eventType: "DeviceCommandExecuted"
      commandId: "command-uuid"
      deviceId: "550e8400-e29b-41d4-a716-446655440000"
      command: "set_temperature"
      parameters:
        temperature: 24.0
      result:
        success: true
        message: "Temperature set successfully"
        executionTime: "1.2s"
      timestamp: "2025-09-12T16:25:01Z"
```

### 3.2 Telemetry Events Channel

**Channel**: `telemetry.data`

#### Measurement Received Event
```yaml
measurementReceived:
  summary: New measurement data received from device
  payload:
    type: object
    properties:
      eventId:
        type: string
        format: uuid
      eventType:
        type: string
        enum: [MeasurementReceived]
      deviceId:
        type: string
        format: uuid
      measurements:
        type: array
        items:
          type: object
          properties:
            type:
              type: string
            value:
              type: number
            unit:
              type: string
            quality:
              type: string
              enum: [good, bad, uncertain]
      timestamp:
        type: string
        format: date-time
    example:
      eventId: "event-uuid"
      eventType: "MeasurementReceived"
      deviceId: "550e8400-e29b-41d4-a716-446655440000"
      measurements:
        - type: "temperature"
          value: 23.5
          unit: "°C"
          quality: "good"
        - type: "humidity"
          value: 45.2
          unit: "%"
          quality: "good"
      timestamp: "2025-09-12T16:25:00Z"
```

### 3.3 Automation Events Channel

**Channel**: `automation.triggers`

#### Scenario Triggered Event
```yaml
scenarioTriggered:
  summary: Automation scenario has been triggered
  payload:
    type: object
    properties:
      eventId:
        type: string
        format: uuid
      eventType:
        type: string
        enum: [ScenarioTriggered]
      scenarioId:
        type: string
        format: uuid
      executionId:
        type: string
        format: uuid
      triggeredBy:
        type: string
      triggerData:
        type: object
      timestamp:
        type: string
        format: date-time
    example:
      eventId: "event-uuid"
      eventType: "ScenarioTriggered"
      scenarioId: "scenario-uuid"
      executionId: "execution-uuid"
      triggeredBy: "time_trigger"
      triggerData:
        scheduled_time: "19:00"
        actual_time: "19:00:02"
      timestamp: "2025-09-12T19:00:02Z"
```

### 3.4 Notification Events Channel

**Channel**: `notifications.queue`

#### Send Notification Event
```yaml
sendNotification:
  summary: Request to send notification to user
  payload:
    type: object
    properties:
      eventId:
        type: string
        format: uuid
      eventType:
        type: string
        enum: [SendNotification]
      userId:
        type: string
        format: uuid
      notificationType:
        type: string
        enum: [info, warning, error, alert]
      title:
        type: string
      message:
        type: string
      channels:
        type: array
        items:
          type: string
          enum: [email, sms, push, in_app]
      priority:
        type: string
        enum: [low, normal, high, urgent]
      templateData:
        type: object
      timestamp:
        type: string
        format: date-time
    example:
      eventId: "event-uuid"
      eventType: "SendNotification"
      userId: "user-uuid"
      notificationType: "alert"
      title: "Temperature Alert"
      message: "Temperature in Living Room has exceeded 30°C"
      channels: ["push", "email"]
      priority: "high"
      templateData:
        device_name: "Living Room Thermostat"
        current_temperature: 31.5
        threshold: 30.0
      timestamp: "2025-09-12T16:25:00Z"
```

## 4. Коды ответов HTTP

### 4.1 Успешные ответы
- **200 OK** - Запрос выполнен успешно
- **201 Created** - Ресурс создан успешно
- **202 Accepted** - Запрос принят к обработке (асинхронные операции)
- **204 No Content** - Запрос выполнен, содержимое отсутствует

### 4.2 Клиентские ошибки
- **400 Bad Request** - Некорректный запрос
- **401 Unauthorized** - Требуется аутентификация
- **403 Forbidden** - Доступ запрещен
- **404 Not Found** - Ресурс не найден
- **409 Conflict** - Конфликт данных
- **422 Unprocessable Entity** - Ошибка валидации данных
- **429 Too Many Requests** - Превышен лимит запросов

### 4.3 Серверные ошибки
- **500 Internal Server Error** - Внутренняя ошибка сервера
- **502 Bad Gateway** - Ошибка шлюза
- **503 Service Unavailable** - Сервис недоступен
- **504 Gateway Timeout** - Таймаут шлюза

## 5. Стандартные форматы ошибок

### 5.1 Формат ошибки
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

### 5.2 Формат ошибки валидации
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "fields": [
        {
          "field": "temperature",
          "message": "Temperature must be between 10 and 35 degrees",
          "value": 50
        }
      ],
      "timestamp": "2025-09-12T16:25:00Z",
      "trace_id": "trace-uuid"
    }
  }
}
```

## 6. Аутентификация и авторизация

### 6.1 JWT Bearer Token
Все API требуют аутентификации через JWT токен в заголовке:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 6.2 Области доступа (Scopes)
- `devices:read` - чтение информации об устройствах
- `devices:write` - управление устройствами
- `devices:command` - отправка команд устройствам
- `homes:read` - чтение информации о домах
- `homes:write` - управление домами
- `scenarios:read` - чтение сценариев
- `scenarios:write` - управление сценариями
- `scenarios:execute` - выполнение сценариев

## 7. Версионирование API

### 7.1 URL Versioning
Версия API указывается в URL: `/api/v1/`, `/api/v2/`

### 7.2 Обратная совместимость
- Минорные изменения (добавление полей) - обратно совместимы
- Мажорные изменения (удаление/изменение полей) - новая версия API
- Поддержка предыдущих версий в течение 12 месяцев

## 8. Rate Limiting

### 8.1 Лимиты по умолчанию
- **Аутентифицированные пользователи**: 1000 запросов/час
- **Команды устройствам**: 100 команд/час на устройство
- **Создание сценариев**: 50 операций/час

### 8.2 Заголовки ответа
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1694520000
```

## Заключение

Разработанные API обеспечивают:
- **Четкие контракты** взаимодействия между микросервисами
- **Синхронное взаимодействие** через REST API для операций CRUD
- **Асинхронное взаимодействие** через события для реактивной обработки
- **Стандартизированные форматы** запросов и ответов
- **Безопасность** через JWT аутентификацию и авторизацию
- **Масштабируемость** через rate limiting и версионирование

API готовы для реализации и интеграции микросервисов в экосистеме "Тёплый дом".