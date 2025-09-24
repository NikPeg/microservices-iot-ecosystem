# Задание 3. Разработка ER-диаграммы

## 1. Идентификация сущностей

На основе анализа предметной области и спроектированных микросервисов определены следующие ключевые сущности для каждого микросервиса:

### 1.1 User Service Database

#### Основные сущности:
- **User** - пользователь системы
- **Profile** - профиль пользователя
- **Subscription** - подписка пользователя
- **Role** - роль пользователя
- **Permission** - разрешения

### 1.2 Home Service Database

#### Основные сущности:
- **Home** - дом пользователя
- **Room** - комната в доме
- **Floor** - этаж дома
- **Location** - местоположение в доме
- **HomeConfiguration** - конфигурация дома

### 1.3 Device Service Database

#### Основные сущности:
- **Device** - устройство IoT
- **DeviceType** - тип устройства
- **DeviceCapability** - возможности устройства
- **DeviceCommand** - команда устройству
- **DeviceStatus** - статус устройства
- **Manufacturer** - производитель устройства

### 1.4 Telemetry Service Database (InfluxDB)

#### Основные сущности:
- **Measurement** - измерение с датчика
- **MetricType** - тип метрики
- **Alert** - предупреждение
- **AlertRule** - правило предупреждения

### 1.5 Automation Service Database

#### Основные сущности:
- **Scenario** - сценарий автоматизации
- **Trigger** - триггер сценария
- **Condition** - условие выполнения
- **Action** - действие сценария
- **ScenarioExecution** - история выполнения сценария

### 1.6 Notification Service Database

#### Основные сущности:
- **Notification** - уведомление
- **NotificationTemplate** - шаблон уведомления
- **DeliveryChannel** - канал доставки
- **DeliveryAttempt** - попытка доставки

## 2. Определение атрибутов

### 2.1 User Service Entities

#### User
- `id` (UUID, PK) - уникальный идентификатор пользователя
- `email` (VARCHAR(255), UNIQUE) - email пользователя
- `password_hash` (VARCHAR(255)) - хэш пароля
- `first_name` (VARCHAR(100)) - имя
- `last_name` (VARCHAR(100)) - фамилия
- `phone` (VARCHAR(20)) - телефон
- `status` (ENUM) - статус пользователя (active, inactive, suspended)
- `email_verified` (BOOLEAN) - подтверждение email
- `created_at` (TIMESTAMP) - дата создания
- `updated_at` (TIMESTAMP) - дата обновления

#### Profile
- `id` (UUID, PK) - уникальный идентификатор профиля
- `user_id` (UUID, FK) - ссылка на пользователя
- `avatar_url` (VARCHAR(500)) - URL аватара
- `timezone` (VARCHAR(50)) - часовой пояс
- `language` (VARCHAR(10)) - язык интерфейса
- `preferences` (JSONB) - настройки пользователя
- `created_at` (TIMESTAMP) - дата создания
- `updated_at` (TIMESTAMP) - дата обновления

#### Subscription
- `id` (UUID, PK) - уникальный идентификатор подписки
- `user_id` (UUID, FK) - ссылка на пользователя
- `plan` (ENUM) - тарифный план (basic, premium, enterprise)
- `status` (ENUM) - статус подписки (active, expired, cancelled)
- `started_at` (TIMESTAMP) - дата начала
- `expires_at` (TIMESTAMP) - дата окончания
- `auto_renew` (BOOLEAN) - автопродление
- `created_at` (TIMESTAMP) - дата создания

### 2.2 Home Service Entities

#### Home
- `id` (UUID, PK) - уникальный идентификатор дома
- `owner_id` (UUID) - ссылка на пользователя (User Service)
- `name` (VARCHAR(100)) - название дома
- `address` (TEXT) - адрес
- `city` (VARCHAR(100)) - город
- `country` (VARCHAR(100)) - страна
- `postal_code` (VARCHAR(20)) - почтовый индекс
- `timezone` (VARCHAR(50)) - часовой пояс
- `area_sqm` (DECIMAL(10,2)) - площадь в кв.м
- `floors_count` (INTEGER) - количество этажей
- `configuration` (JSONB) - конфигурация дома
- `created_at` (TIMESTAMP) - дата создания
- `updated_at` (TIMESTAMP) - дата обновления

#### Room
- `id` (UUID, PK) - уникальный идентификатор комнаты
- `home_id` (UUID, FK) - ссылка на дом
- `name` (VARCHAR(100)) - название комнаты
- `type` (ENUM) - тип комнаты (living_room, bedroom, kitchen, bathroom, etc.)
- `floor` (INTEGER) - этаж
- `area_sqm` (DECIMAL(8,2)) - площадь комнаты
- `description` (TEXT) - описание
- `created_at` (TIMESTAMP) - дата создания
- `updated_at` (TIMESTAMP) - дата обновления

### 2.3 Device Service Entities

#### Device
- `id` (UUID, PK) - уникальный идентификатор устройства
- `name` (VARCHAR(100)) - название устройства
- `serial_number` (VARCHAR(100), UNIQUE) - серийный номер
- `device_type_id` (UUID, FK) - ссылка на тип устройства
- `manufacturer_id` (UUID, FK) - ссылка на производителя
- `model` (VARCHAR(100)) - модель устройства
- `firmware_version` (VARCHAR(50)) - версия прошивки
- `home_id` (UUID) - ссылка на дом (Home Service)
- `room_id` (UUID) - ссылка на комнату (Home Service)
- `status` (ENUM) - статус устройства (active, inactive, error, maintenance, offline)
- `ip_address` (INET) - IP адрес устройства
- `mac_address` (VARCHAR(17)) - MAC адрес
- `protocol` (ENUM) - протокол связи (mqtt, coap, http, zigbee, zwave)
- `configuration` (JSONB) - конфигурация устройства
- `capabilities` (JSONB) - возможности устройства
- `last_seen` (TIMESTAMP) - последняя активность
- `installed_at` (TIMESTAMP) - дата установки
- `created_at` (TIMESTAMP) - дата создания
- `updated_at` (TIMESTAMP) - дата обновления

#### DeviceType
- `id` (UUID, PK) - уникальный идентификатор типа
- `name` (VARCHAR(100)) - название типа
- `category` (ENUM) - категория (sensor, actuator, controller, gateway)
- `description` (TEXT) - описание
- `default_capabilities` (JSONB) - стандартные возможности
- `icon` (VARCHAR(100)) - иконка
- `created_at` (TIMESTAMP) - дата создания

#### DeviceCommand
- `id` (UUID, PK) - уникальный идентификатор команды
- `device_id` (UUID, FK) - ссылка на устройство
- `command` (VARCHAR(50)) - команда
- `parameters` (JSONB) - параметры команды
- `status` (ENUM) - статус команды (pending, executing, completed, failed, expired)
- `result` (JSONB) - результат выполнения
- `error_message` (TEXT) - сообщение об ошибке
- `issued_by` (UUID) - кто выдал команду (User Service)
- `issued_at` (TIMESTAMP) - время выдачи
- `executed_at` (TIMESTAMP) - время выполнения
- `expires_at` (TIMESTAMP) - время истечения

#### Manufacturer
- `id` (UUID, PK) - уникальный идентификатор производителя
- `name` (VARCHAR(100)) - название производителя
- `website` (VARCHAR(255)) - веб-сайт
- `support_email` (VARCHAR(255)) - email поддержки
- `created_at` (TIMESTAMP) - дата создания

### 2.4 Automation Service Entities

#### Scenario
- `id` (UUID, PK) - уникальный идентификатор сценария
- `user_id` (UUID) - ссылка на пользователя (User Service)
- `home_id` (UUID) - ссылка на дом (Home Service)
- `name` (VARCHAR(100)) - название сценария
- `description` (TEXT) - описание
- `enabled` (BOOLEAN) - включен ли сценарий
- `priority` (INTEGER) - приоритет выполнения
- `triggers` (JSONB) - триггеры сценария
- `conditions` (JSONB) - условия выполнения
- `actions` (JSONB) - действия сценария
- `schedule` (JSONB) - расписание выполнения
- `created_at` (TIMESTAMP) - дата создания
- `updated_at` (TIMESTAMP) - дата обновления

#### ScenarioExecution
- `id` (UUID, PK) - уникальный идентификатор выполнения
- `scenario_id` (UUID, FK) - ссылка на сценарий
- `triggered_by` (VARCHAR(100)) - что запустило сценарий
- `trigger_data` (JSONB) - данные триггера
- `status` (ENUM) - статус выполнения (running, completed, failed, cancelled)
- `started_at` (TIMESTAMP) - время начала
- `completed_at` (TIMESTAMP) - время завершения
- `duration_ms` (INTEGER) - длительность выполнения в мс
- `actions_executed` (INTEGER) - количество выполненных действий
- `actions_failed` (INTEGER) - количество неудачных действий
- `error_message` (TEXT) - сообщение об ошибке
- `execution_log` (JSONB) - лог выполнения

### 2.5 Notification Service Entities

#### Notification
- `id` (UUID, PK) - уникальный идентификатор уведомления
- `user_id` (UUID) - ссылка на пользователя (User Service)
- `type` (ENUM) - тип уведомления (info, warning, error, alert)
- `title` (VARCHAR(200)) - заголовок
- `message` (TEXT) - текст сообщения
- `channels` (VARCHAR(100)[]) - каналы доставки (email, sms, push, in_app)
- `priority` (ENUM) - приоритет (low, normal, high, urgent)
- `status` (ENUM) - статус (pending, sent, delivered, failed, cancelled)
- `template_id` (UUID, FK) - ссылка на шаблон
- `template_data` (JSONB) - данные для шаблона
- `scheduled_at` (TIMESTAMP) - время планируемой отправки
- `sent_at` (TIMESTAMP) - время отправки
- `delivered_at` (TIMESTAMP) - время доставки
- `expires_at` (TIMESTAMP) - время истечения
- `created_at` (TIMESTAMP) - дата создания

#### NotificationTemplate
- `id` (UUID, PK) - уникальный идентификатор шаблона
- `name` (VARCHAR(100)) - название шаблона
- `type` (ENUM) - тип уведомления
- `channel` (ENUM) - канал доставки
- `subject_template` (TEXT) - шаблон заголовка
- `body_template` (TEXT) - шаблон тела сообщения
- `variables` (JSONB) - переменные шаблона
- `active` (BOOLEAN) - активен ли шаблон
- `created_at` (TIMESTAMP) - дата создания
- `updated_at` (TIMESTAMP) - дата обновления

## 3. Описание связей между сущностями

### 3.1 User Service Relationships

- **User → Profile**: Один-к-одному (1:1)
  - Каждый пользователь имеет один профиль
- **User → Subscription**: Один-ко-многим (1:N)
  - Пользователь может иметь несколько подписок (история)

### 3.2 Home Service Relationships

- **Home → Room**: Один-ко-многим (1:N)
  - Дом содержит множество комнат
  - Каждая комната принадлежит одному дому

### 3.3 Device Service Relationships

- **DeviceType → Device**: Один-ко-многим (1:N)
  - Тип устройства может иметь множество экземпляров
- **Manufacturer → Device**: Один-ко-многим (1:N)
  - Производитель может выпускать множество устройств
- **Device → DeviceCommand**: Один-ко-многим (1:N)
  - Устройство может получать множество команд

### 3.4 Automation Service Relationships

- **Scenario → ScenarioExecution**: Один-ко-многим (1:N)
  - Сценарий может иметь множество выполнений

### 3.5 Notification Service Relationships

- **NotificationTemplate → Notification**: Один-ко-многим (1:N)
  - Шаблон может использоваться для множества уведомлений

### 3.6 Межсервисные связи (через внешние ключи)

- **User Service → Home Service**: 
  - `Home.owner_id` → `User.id` (1:N)
- **Home Service → Device Service**:
  - `Device.home_id` → `Home.id` (1:N)
  - `Device.room_id` → `Room.id` (1:N)
- **User Service → Device Service**:
  - `DeviceCommand.issued_by` → `User.id` (1:N)
- **User Service → Automation Service**:
  - `Scenario.user_id` → `User.id` (1:N)
- **Home Service → Automation Service**:
  - `Scenario.home_id` → `Home.id` (1:N)
- **User Service → Notification Service**:
  - `Notification.user_id` → `User.id` (1:N)

## 4. Особенности проектирования

### 4.1 Database per Service Pattern
Каждый микросервис имеет собственную базу данных, что обеспечивает:
- Независимость развертывания
- Технологическое разнообразие
- Изоляцию данных

### 4.2 Внешние ключи между сервисами
Связи между сервисами реализуются через:
- UUID идентификаторы
- Eventual consistency
- Компенсирующие транзакции при необходимости

### 4.3 Специализированные типы данных
- **JSONB** для гибких конфигураций и метаданных
- **TIMESTAMP WITH TIME ZONE** для временных меток
- **ENUM** для ограниченных наборов значений
- **UUID** для глобально уникальных идентификаторов

### 4.4 Индексы и производительность
Планируются индексы на:
- Внешние ключи
- Поля для поиска (email, serial_number)
- Временные поля для аналитики
- Составные индексы для частых запросов

## 5. Стратегия миграции данных

### 5.1 Из монолита в микросервисы
1. **Анализ существующих данных** в монолитной БД
2. **Создание скриптов миграции** для каждого сервиса
3. **Поэтапная миграция** с проверкой целостности
4. **Синхронизация данных** во время переходного периода

### 5.2 Обеспечение целостности
- **Saga Pattern** для распределенных транзакций
- **Event Sourcing** для критических операций
- **Компенсирующие действия** при сбоях

## Заключение

Разработанная модель данных обеспечивает:
- **Четкое разделение** данных между микросервисами
- **Гибкость** в развитии каждого сервиса
- **Масштабируемость** и производительность
- **Целостность данных** на уровне системы

Модель готова для реализации в виде ER-диаграмм и SQL-схем.