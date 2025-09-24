# Задание 3 - Итоговый отчет: Разработка ER-диаграммы

## Краткое резюме

Разработана полная модель данных для микросервисной экосистемы "Тёплый дом" с детальными ER-диаграммами для каждого микросервиса. Определены ключевые сущности, их атрибуты и взаимосвязи в соответствии с принципами Database per Service.

## 1. Результаты идентификации сущностей

### 1.1 Распределение сущностей по микросервисам

| Микросервис | Количество сущностей | Основные сущности |
|-------------|---------------------|-------------------|
| **User Service** | 6 | User, Profile, Subscription, Role, UserRole, Session |
| **Home Service** | 5 | Home, Room, Floor, Location, HomeConfiguration |
| **Device Service** | 5 | Device, DeviceType, DeviceCommand, DeviceCapability, Manufacturer |
| **Automation Service** | 6 | Scenario, ScenarioExecution, Trigger, Condition, Action, ActionExecution |
| **Notification Service** | 6 | Notification, NotificationTemplate, DeliveryAttempt, DeliveryChannel, NotificationPreference, NotificationQueue |
| **Telemetry Service** | 4 | Measurement, MetricType, Alert, AlertRule |

**Общее количество сущностей**: 32

### 1.2 Ключевые характеристики модели данных

#### Идентификаторы
- **UUID** для всех первичных ключей
- **Глобальная уникальность** идентификаторов
- **Совместимость** с распределенными системами

#### Временные метки
- **created_at** - обязательное поле для всех сущностей
- **updated_at** - для изменяемых сущностей
- **TIMESTAMP WITH TIME ZONE** для корректной работы в разных часовых поясах

#### Гибкие данные
- **JSONB** для конфигураций, настроек и метаданных
- **ENUM** для ограниченных наборов значений
- **Массивы** для множественных значений

## 2. Созданные ER-диаграммы

### 2.1 User Service ER Diagram
**Файл**: [`er-user-service.puml`](./er-user-service.puml)

**Ключевые сущности**:
- **User** - основная сущность пользователя с аутентификационными данными
- **Profile** - расширенная информация о пользователе
- **Subscription** - управление подписками и тарифными планами
- **Role/UserRole** - система ролей и разрешений
- **Session** - управление пользовательскими сессиями

**Особенности**:
- Один-к-одному связь User-Profile
- Поддержка множественных подписок
- Гибкая система ролей
- Отслеживание сессий и безопасность

### 2.2 Home Service ER Diagram
**Файл**: [`er-home-service.puml`](./er-home-service.puml)

**Ключевые сущности**:
- **Home** - дом пользователя с адресной информацией
- **Room** - комнаты с типизацией и характеристиками
- **Floor** - этажи дома
- **Location** - точные местоположения внутри дома
- **HomeConfiguration** - гибкие настройки дома

**Особенности**:
- Иерархическая структура: Home → Floor → Room → Location
- Поддержка координат для точного позиционирования
- Гибкая конфигурация через JSONB

### 2.3 Device Service ER Diagram
**Файл**: [`er-device-service.puml`](./er-device-service.puml)

**Ключевые сущности**:
- **Device** - центральная сущность IoT устройства
- **DeviceType** - типизация устройств по категориям
- **DeviceCommand** - команды для управления устройствами
- **DeviceCapability** - возможности и функции устройств
- **Manufacturer** - информация о производителях

**Особенности**:
- Поддержка различных IoT протоколов
- Отслеживание состояния и активности устройств
- Гибкая система возможностей через JSONB
- История команд с результатами выполнения

### 2.4 Automation Service ER Diagram
**Файл**: [`er-automation-service.puml`](./er-automation-service.puml)

**Ключевые сущности**:
- **Scenario** - сценарии автоматизации
- **ScenarioExecution** - история выполнения сценариев
- **Trigger** - триггеры для запуска сценариев
- **Condition** - условия выполнения
- **Action** - действия сценариев
- **ActionExecution** - детальная история выполнения действий

**Особенности**:
- Сложная логика триггеров и условий
- Детальное логирование выполнения
- Поддержка retry механизмов
- Приоритизация и тайм-ауты

### 2.5 Notification Service ER Diagram
**Файл**: [`er-notification-service.puml`](./er-notification-service.puml)

**Ключевые сущности**:
- **Notification** - уведомления пользователям
- **NotificationTemplate** - шаблоны сообщений
- **DeliveryAttempt** - попытки доставки
- **DeliveryChannel** - каналы доставки пользователей
- **NotificationPreference** - настройки уведомлений
- **NotificationQueue** - очередь доставки

**Особенности**:
- Множественные каналы доставки
- Система приоритетов и повторных попыток
- Шаблонизация сообщений
- Персональные настройки пользователей

### 2.6 Microservices Overview ER Diagram
**Файл**: [`er-microservices-overview.puml`](./er-microservices-overview.puml)

**Описание**: Высокоуровневая диаграмма, показывающая основные сущности всех микросервисов и их взаимосвязи.

**Межсервисные связи**:
- User → Home (владение)
- User → Device Command (управление)
- User → Scenario (создание)
- User → Notification (получение)
- Home → Device (размещение)
- Device → Measurement (генерация данных)

## 3. Описание связей между сущностями

### 3.1 Внутрисервисные связи

#### User Service
- **User ↔ Profile**: Один-к-одному (1:1)
- **User ↔ Subscription**: Один-ко-многим (1:N)
- **User ↔ UserRole**: Один-ко-многим (1:N)
- **Role ↔ UserRole**: Один-ко-многим (1:N)
- **User ↔ Session**: Один-ко-многим (1:N)

#### Home Service
- **Home ↔ Room**: Один-ко-многим (1:N)
- **Home ↔ Floor**: Один-ко-многим (1:N)
- **Home ↔ Location**: Один-ко-многим (1:N)
- **Room ↔ Location**: Один-ко-многим (1:N)
- **Home ↔ HomeConfiguration**: Один-ко-многим (1:N)

#### Device Service
- **DeviceType ↔ Device**: Один-ко-многим (1:N)
- **Manufacturer ↔ Device**: Один-ко-многим (1:N)
- **Device ↔ DeviceCommand**: Один-ко-многим (1:N)
- **Device ↔ DeviceCapability**: Один-ко-многим (1:N)

#### Automation Service
- **Scenario ↔ ScenarioExecution**: Один-ко-многим (1:N)
- **Scenario ↔ Trigger**: Один-ко-многим (1:N)
- **Scenario ↔ Condition**: Один-ко-многим (1:N)
- **Scenario ↔ Action**: Один-ко-многим (1:N)
- **ScenarioExecution ↔ ActionExecution**: Один-ко-многим (1:N)

#### Notification Service
- **NotificationTemplate ↔ Notification**: Один-ко-многим (1:N)
- **Notification ↔ DeliveryAttempt**: Один-ко-многим (1:N)
- **Notification ↔ NotificationQueue**: Один-к-одному (1:1)

### 3.2 Межсервисные связи (External FK)

| Связь | Тип | Описание |
|-------|-----|----------|
| **User → Home** | 1:N | Пользователь владеет домами |
| **User → DeviceCommand** | 1:N | Пользователь выдает команды устройствам |
| **User → Scenario** | 1:N | Пользователь создает сценарии |
| **User → Notification** | 1:N | Пользователь получает уведомления |
| **Home → Device** | 1:N | Дом содержит устройства |
| **Room → Device** | 1:N | Комната содержит устройства |
| **Home → Scenario** | 1:N | Дом автоматизируется сценариями |
| **Device → Measurement** | 1:N | Устройство генерирует измерения |

## 4. Особенности проектирования базы данных

### 4.1 Database per Service Pattern

**Преимущества**:
- **Независимость** развертывания и масштабирования
- **Технологическое разнообразие** (PostgreSQL, InfluxDB, Redis)
- **Изоляция данных** и безопасность
- **Автономность команд** разработки

**Вызовы**:
- **Eventual Consistency** между сервисами
- **Отсутствие ACID** на уровне системы
- **Сложность запросов** через несколько сервисов

### 4.2 Стратегии обеспечения целостности

#### Referential Integrity
- **Внутри сервиса**: Стандартные FK constraints
- **Между сервисами**: Логическая целостность через события

#### Consistency Patterns
- **Strong Consistency**: Внутри микросервиса
- **Eventual Consistency**: Между микросервисами
- **Saga Pattern**: Для распределенных транзакций

### 4.3 Специализированные решения

#### PostgreSQL (Транзакционные данные)
- **ACID** транзакции
- **JSONB** для гибких данных
- **Индексы** на JSONB полях
- **Партиционирование** для больших таблиц

#### InfluxDB (Временные ряды)
- **Оптимизация** для time-series данных
- **Автоматическое сжатие** старых данных
- **Retention policies** для управления объемом
- **Continuous queries** для агрегации

#### Redis (Кэширование и очереди)
- **In-memory** производительность
- **Pub/Sub** для real-time уведомлений
- **Sorted sets** для приоритетных очередей
- **TTL** для автоматической очистки

### 4.4 Индексная стратегия

#### Обязательные индексы
- **Primary Keys** (UUID)
- **Foreign Keys** для joins
- **Unique constraints** (email, serial_number)

#### Производительные индексы
- **Composite indexes** для частых запросов
- **Partial indexes** для условных выборок
- **JSONB indexes** для поиска в JSON данных
- **Time-based indexes** для временных запросов

## 5. Миграционная стратегия

### 5.1 Из монолита в микросервисы

**Этап 1: Анализ данных**
- Аудит существующих данных в монолитной БД
- Выявление зависимостей и связей
- Планирование разделения данных

**Этап 2: Создание схем**
- Создание БД для каждого микросервиса
- Применение DDL скриптов
- Настройка индексов и constraints

**Этап 3: Миграция данных**
- Поэтапная миграция по сервисам
- Проверка целостности данных
- Синхронизация во время переходного периода

**Этап 4: Переключение**
- Постепенное переключение трафика
- Мониторинг производительности
- Откат при необходимости

### 5.2 Обеспечение Zero Downtime

- **Blue-Green Deployment** для БД
- **Read Replicas** для минимизации простоя
- **Event Sourcing** для критических данных
- **Compensating Actions** при сбоях

## 6. Мониторинг и обслуживание

### 6.1 Database Health Monitoring

**Метрики производительности**:
- Connection pool utilization
- Query execution time
- Index usage statistics
- Disk space utilization

**Алерты**:
- Slow queries (> 1s)
- High connection count
- Replication lag
- Disk space < 20%

### 6.2 Data Quality Monitoring

**Проверки целостности**:
- Orphaned records detection
- Data consistency checks
- Schema drift monitoring
- Backup verification

## 7. Безопасность данных

### 7.1 Access Control

- **Database users** для каждого сервиса
- **Minimal privileges** principle
- **Connection encryption** (TLS)
- **Network isolation** через VPC

### 7.2 Data Protection

- **Encryption at rest** для sensitive данных
- **PII data masking** в non-prod средах
- **Audit logging** для критических операций
- **Regular security scans**

## 8. Производительность и масштабирование

### 8.1 Horizontal Scaling

**Read Replicas**:
- User Service: 2 read replicas
- Device Service: 3 read replicas (высокая нагрузка на чтение)
- Telemetry Service: Кластер InfluxDB

**Sharding Strategy**:
- User Service: По user_id
- Device Service: По home_id
- Telemetry Service: По времени (time-based partitioning)

### 8.2 Caching Strategy

**Redis Caching**:
- User sessions (TTL: 24h)
- Device states (TTL: 5min)
- Scenario states (TTL: 1h)
- Notification queues (persistent)

## Заключение

Разработанная модель данных обеспечивает:

✅ **Четкое разделение** данных между микросервисами
✅ **Масштабируемость** каждого сервиса независимо
✅ **Гибкость** в выборе технологий БД
✅ **Производительность** через специализированные решения
✅ **Целостность данных** на уровне системы
✅ **Готовность к реализации** MVP

Модель готова для перехода к следующему этапу - проектированию API микросервисов.

---

**Созданные ER-диаграммы**:
- [`task3-er-diagram-analysis.md`](./task3-er-diagram-analysis.md) - детальный анализ сущностей
- [`er-user-service.puml`](./er-user-service.puml) - User Service ER диаграмма
- [`er-home-service.puml`](./er-home-service.puml) - Home Service ER диаграмма
- [`er-device-service.puml`](./er-device-service.puml) - Device Service ER диаграмма
- [`er-automation-service.puml`](./er-automation-service.puml) - Automation Service ER диаграмма
- [`er-notification-service.puml`](./er-notification-service.puml) - Notification Service ER диаграмма
- [`er-microservices-overview.puml`](./er-microservices-overview.puml) - обзорная диаграмма всех сервисов