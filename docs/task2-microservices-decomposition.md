# Задание 2. Проектирование микросервисной архитектуры

## 1. Декомпозиция приложения на микросервисы

### 1.1 Принципы декомпозиции

При разбиении монолитного приложения на микросервисы использовались следующие принципы:

- **Domain-Driven Design (DDD)**: Каждый микросервис соответствует отдельному Bounded Context
- **Single Responsibility Principle**: Каждый сервис отвечает за одну бизнес-функцию
- **Database per Service**: Каждый микросервис имеет собственную базу данных
- **Loose Coupling**: Минимальные зависимости между сервисами
- **High Cohesion**: Связанная функциональность группируется в одном сервисе

### 1.2 Выделенные микросервисы

#### 1.2.1 Device Service (Сервис управления устройствами)
**Домен**: Device Management
**Ответственность**: 
- Регистрация и управление IoT устройствами (датчики, реле, выключатели)
- Отправка команд устройствам
- Мониторинг состояния устройств
- Управление типами и возможностями устройств

**Ключевые сущности**:
- Device (устройство)
- DeviceType (тип устройства)
- DeviceCapability (возможности устройства)
- DeviceCommand (команда устройству)

**База данных**: PostgreSQL (device_db)
**Порт**: 8081

#### 1.2.2 Telemetry Service (Сервис телеметрии)
**Домен**: Telemetry & Monitoring
**Ответственность**:
- Сбор данных с датчиков
- Хранение временных рядов
- Агрегация и анализ данных
- Генерация предупреждений на основе пороговых значений

**Ключевые сущности**:
- Measurement (измерение)
- MetricType (тип метрики)
- TimeSeriesData (временные ряды)
- Alert (предупреждение)

**База данных**: InfluxDB (telemetry_db) + Redis (кэш)
**Порт**: 8082

#### 1.2.3 User Service (Сервис управления пользователями)
**Домен**: User Management
**Ответственность**:
- Регистрация и аутентификация пользователей
- Управление профилями и настройками
- Авторизация и контроль доступа
- Управление подписками и тарифными планами

**Ключевые сущности**:
- User (пользователь)
- Profile (профиль)
- Role (роль)
- Subscription (подписка)

**База данных**: PostgreSQL (user_db)
**Порт**: 8083

#### 1.2.4 Home Service (Сервис управления домами)
**Домен**: Home Management
**Ответственность**:
- Управление структурой домов (комнаты, этажи)
- Привязка устройств к местоположениям
- Управление конфигурацией домов
- Группировка устройств по зонам

**Ключевые сущности**:
- Home (дом)
- Room (комната)
- Floor (этаж)
- Location (местоположение)

**База данных**: PostgreSQL (home_db)
**Порт**: 8084

#### 1.2.5 Automation Service (Сервис автоматизации)
**Домен**: Automation & Scenarios
**Ответственность**:
- Создание и управление сценариями автоматизации
- Обработка триггеров и условий
- Выполнение автоматических действий
- Планирование задач по расписанию

**Ключевые сущности**:
- Scenario (сценарий)
- Trigger (триггер)
- Condition (условие)
- Action (действие)

**База данных**: PostgreSQL (automation_db) + Redis (кэш состояний)
**Порт**: 8085

#### 1.2.6 Notification Service (Сервис уведомлений)
**Домен**: Notifications
**Ответственность**:
- Отправка уведомлений пользователям
- Управление каналами доставки (email, SMS, push)
- Шаблонизация сообщений
- Отслеживание статуса доставки

**Ключевые сущности**:
- Notification (уведомление)
- NotificationTemplate (шаблон)
- DeliveryChannel (канал доставки)
- DeliveryAttempt (попытка доставки)

**База данных**: PostgreSQL (notification_db) + Redis (очередь)
**Порт**: 8086

#### 1.2.7 API Gateway (Шлюз API)
**Ответственность**:
- Единая точка входа для клиентских приложений
- Маршрутизация запросов к микросервисам
- Аутентификация и авторизация
- Rate limiting и мониторинг
- Агрегация ответов от нескольких сервисов

**Технология**: Kong или Nginx + Lua
**Порт**: 8080

### 1.3 Инфраструктурные компоненты

#### 1.3.1 Message Broker
**Технология**: Apache Kafka
**Ответственность**:
- Асинхронная коммуникация между сервисами
- Event streaming для телеметрии
- Гарантированная доставка сообщений

**Основные топики**:
- `device.events` - события устройств
- `telemetry.data` - данные телеметрии
- `automation.triggers` - триггеры автоматизации
- `notifications.queue` - очередь уведомлений

#### 1.3.2 Service Discovery
**Технология**: Consul
**Ответственность**:
- Регистрация и обнаружение сервисов
- Health checking
- Configuration management
- Service mesh coordination

#### 1.3.3 Monitoring & Observability
**Компоненты**:
- **Prometheus** - сбор метрик
- **Grafana** - визуализация метрик
- **Jaeger** - distributed tracing
- **ELK Stack** - централизованное логирование

## 2. Взаимодействие между микросервисами

### 2.1 Синхронное взаимодействие (REST API)

#### User Service ↔ Home Service
- `GET /api/v1/users/{userId}/homes` - получение домов пользователя
- `POST /api/v1/users/{userId}/homes` - создание нового дома

#### Home Service ↔ Device Service
- `GET /api/v1/homes/{homeId}/devices` - получение устройств дома
- `POST /api/v1/homes/{homeId}/rooms/{roomId}/devices` - привязка устройства к комнате

#### Device Service ↔ Telemetry Service
- `GET /api/v1/devices/{deviceId}/latest-data` - получение последних данных устройства
- `POST /api/v1/devices/{deviceId}/measurements` - отправка измерений

### 2.2 Асинхронное взаимодействие (Events)

#### Device Service → Telemetry Service
```json
{
  "eventType": "DeviceDataReceived",
  "deviceId": "device-123",
  "timestamp": "2025-09-12T15:00:00Z",
  "data": {
    "temperature": 22.5,
    "humidity": 45.2,
    "status": "active"
  }
}
```

#### Telemetry Service → Automation Service
```json
{
  "eventType": "ThresholdExceeded",
  "deviceId": "device-123",
  "metricType": "temperature",
  "value": 30.0,
  "threshold": 25.0,
  "timestamp": "2025-09-12T15:00:00Z"
}
```

#### Automation Service → Device Service
```json
{
  "eventType": "ExecuteDeviceCommand",
  "deviceId": "heater-456",
  "command": "turn_on",
  "parameters": {
    "temperature": 22.0
  },
  "scenarioId": "scenario-789"
}
```

#### Automation Service → Notification Service
```json
{
  "eventType": "SendNotification",
  "userId": "user-123",
  "type": "alert",
  "message": "Температура в гостиной превысила 25°C",
  "channels": ["email", "push"],
  "priority": "high"
}
```

### 2.3 Паттерны взаимодействия

#### 2.3.1 Request-Response Pattern
Используется для синхронных операций, требующих немедленного ответа:
- Получение данных пользователя
- Выполнение команд устройств
- Валидация данных

#### 2.3.2 Publish-Subscribe Pattern
Используется для асинхронных событий:
- Обработка телеметрии
- Выполнение сценариев автоматизации
- Отправка уведомлений

#### 2.3.3 Saga Pattern
Используется для распределенных транзакций:
- Регистрация нового пользователя с созданием дома
- Удаление устройства со всеми связанными данными

## 3. Архитектура баз данных

### 3.1 Database per Service Pattern

Каждый микросервис имеет собственную базу данных для обеспечения независимости и масштабируемости:

#### Device Service Database (PostgreSQL)
```sql
-- Устройства
CREATE TABLE devices (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    model VARCHAR(100),
    manufacturer VARCHAR(100),
    home_id UUID NOT NULL,
    room_id UUID,
    status VARCHAR(20) DEFAULT 'inactive',
    capabilities JSONB,
    configuration JSONB,
    last_seen TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Команды устройств
CREATE TABLE device_commands (
    id UUID PRIMARY KEY,
    device_id UUID REFERENCES devices(id),
    command VARCHAR(50) NOT NULL,
    parameters JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    executed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### User Service Database (PostgreSQL)
```sql
-- Пользователи
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Подписки
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    plan VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);
```

#### Home Service Database (PostgreSQL)
```sql
-- Дома
CREATE TABLE homes (
    id UUID PRIMARY KEY,
    owner_id UUID NOT NULL, -- ссылка на User Service
    name VARCHAR(100) NOT NULL,
    address TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    configuration JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Комнаты
CREATE TABLE rooms (
    id UUID PRIMARY KEY,
    home_id UUID REFERENCES homes(id),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50), -- living_room, bedroom, kitchen, etc.
    floor INTEGER DEFAULT 1,
    area DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Telemetry Service Database (InfluxDB)
```sql
-- Измерения (временные ряды)
measurement_data,device_id=device-123,metric_type=temperature value=22.5,quality=good 1694520000000000000
measurement_data,device_id=device-123,metric_type=humidity value=45.2,quality=good 1694520000000000000

-- Агрегированные данные
measurement_hourly,device_id=device-123,metric_type=temperature min=20.1,max=25.3,avg=22.7,count=60 1694520000000000000
```

#### Automation Service Database (PostgreSQL)
```sql
-- Сценарии
CREATE TABLE scenarios (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    home_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT true,
    triggers JSONB NOT NULL,
    conditions JSONB,
    actions JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- История выполнения
CREATE TABLE scenario_executions (
    id UUID PRIMARY KEY,
    scenario_id UUID REFERENCES scenarios(id),
    triggered_by VARCHAR(100),
    status VARCHAR(20), -- success, failed, partial
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);
```

#### Notification Service Database (PostgreSQL)
```sql
-- Уведомления
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    message TEXT NOT NULL,
    channels VARCHAR(100)[], -- email, sms, push
    priority VARCHAR(20) DEFAULT 'normal',
    status VARCHAR(20) DEFAULT 'pending',
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3.2 Стратегии обеспечения консистентности данных

#### 3.2.1 Eventual Consistency
Большинство операций используют модель eventual consistency через события:
- Изменения в Device Service → события → обновления в Telemetry Service
- Создание пользователя → события → создание дома по умолчанию

#### 3.2.2 Saga Pattern для критических операций
Для операций, требующих строгой консистентности:
- Удаление пользователя (удаление во всех связанных сервисах)
- Перенос устройства между домами

#### 3.2.3 Компенсирующие транзакции
При сбоях в распределенных операциях:
- Откат изменений в случае ошибки
- Повторная обработка неуспешных операций

## 4. Технические решения и паттерны

### 4.1 Архитектурные паттерны

#### 4.1.1 Hexagonal Architecture (Ports & Adapters)
Каждый микросервис использует гексагональную архитектуру:
- **Domain Layer** - бизнес-логика и доменные сущности
- **Application Layer** - use cases и application services
- **Infrastructure Layer** - адаптеры для внешних систем

#### 4.1.2 CQRS (Command Query Responsibility Segregation)
Для сервисов с высокой нагрузкой на чтение (Telemetry Service):
- Отдельные модели для команд и запросов
- Оптимизированные read-модели
- Event sourcing для критических данных

#### 4.1.3 Circuit Breaker Pattern
Для повышения отказоустойчивости:
- Защита от каскадных сбоев
- Graceful degradation при недоступности сервисов
- Автоматическое восстановление

### 4.2 Обеспечение безопасности

#### 4.2.1 OAuth 2.0 + JWT
- Централизованная аутентификация через User Service
- JWT токены для авторизации между сервисами
- Refresh tokens для длительных сессий

#### 4.2.2 Service-to-Service Authentication
- mTLS для межсервисного взаимодействия
- API keys для внешних интеграций
- Service mesh для управления безопасностью

### 4.3 Мониторинг и наблюдаемость

#### 4.3.1 Distributed Tracing
- Уникальные trace ID для отслеживания запросов
- Span-ы для каждого сервиса
- Корреляция логов и метрик

#### 4.3.2 Health Checks
- Liveness probes для Kubernetes
- Readiness probes для балансировки нагрузки
- Dependency health checks

## 5. Преимущества новой архитектуры

### 5.1 Масштабируемость
- Независимое масштабирование каждого сервиса
- Горизонтальное масштабирование по требованию
- Оптимизация ресурсов под конкретные нагрузки

### 5.2 Отказоустойчивость
- Изоляция сбоев в рамках одного сервиса
- Graceful degradation при недоступности компонентов
- Автоматическое восстановление

### 5.3 Гибкость разработки
- Независимые команды разработки
- Различные технологические стеки для разных задач
- Быстрое внедрение новых функций

### 5.4 Производительность
- Специализированные базы данных для разных типов данных
- Кэширование на уровне сервисов
- Асинхронная обработка тяжелых операций

## 6. Вызовы и риски

### 6.1 Сложность
- Распределенная система сложнее в отладке
- Необходимость мониторинга множества компонентов
- Сложность тестирования интеграций

### 6.2 Консистентность данных
- Eventual consistency может быть неприемлема для некоторых операций
- Необходимость компенсирующих транзакций
- Сложность обеспечения ACID свойств

### 6.3 Производительность сети
- Увеличение латентности из-за сетевых вызовов
- Необходимость оптимизации межсервисного взаимодействия
- Управление нагрузкой на message broker

## Заключение

Предложенная микросервисная архитектура обеспечивает:
- Четкое разделение ответственности между сервисами
- Масштабируемость и отказоустойчивость
- Гибкость в выборе технологий
- Возможность независимой разработки и развертывания

Архитектура готова к реализации MVP с последующим расширением функциональности.