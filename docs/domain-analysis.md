# Анализ доменов и границ контекстов (Domain-Driven Design)

## 1. Текущее состояние монолита

### 1.1 Выявленные проблемы в текущей архитектуре
- **Отсутствие четких доменных границ**: Вся логика смешана в одном приложении
- **Слабая модель предметной области**: Только базовая сущность Sensor
- **Отсутствие бизнес-логики**: Преимущественно CRUD операции
- **Нет разделения ответственности**: Один сервис делает все

### 1.2 Анализ текущего кода с точки зрения DDD

#### Текущие сущности (Entities):
- `Sensor` - основная сущность, представляющая датчик

#### Отсутствующие концепции:
- **Агрегаты (Aggregates)**: Нет группировки связанных сущностей
- **Доменные сервисы**: Бизнес-логика размазана по handlers
- **Value Objects**: Примитивные типы вместо доменных объектов
- **Доменные события**: Отсутствует событийная модель

## 2. Целевая доменная модель

### 2.1 Bounded Context: Device Management (Управление устройствами)

#### Агрегат: Device
```
Device (Aggregate Root)
├── DeviceId (Value Object)
├── DeviceName (Value Object)  
├── DeviceType (Value Object)
├── Location (Value Object)
├── Status (Value Object)
├── Capabilities (Value Object Collection)
└── LastActivity (Value Object)
```

#### Сущности:
- **Device** - базовое устройство (датчик или исполнительное устройство)
- **Sensor** - специализация Device для датчиков
- **Actuator** - специализация Device для исполнительных устройств

#### Value Objects:
- **DeviceId** - уникальный идентификатор устройства
- **DeviceType** - тип устройства (temperature, humidity, relay, switch)
- **Location** - местоположение устройства
- **DeviceStatus** - состояние устройства (active, inactive, error, maintenance)
- **Capability** - возможности устройства

#### Доменные сервисы:
- **DeviceRegistrationService** - регистрация новых устройств
- **DeviceCommandService** - отправка команд устройствам
- **DeviceHealthService** - мониторинг состояния устройств

#### Доменные события:
- **DeviceRegistered** - устройство зарегистрировано
- **DeviceStatusChanged** - изменилось состояние устройства
- **DeviceCommandSent** - отправлена команда устройству
- **DeviceError** - ошибка устройства

### 2.2 Bounded Context: Telemetry (Телеметрия)

#### Агрегат: Measurement
```
Measurement (Aggregate Root)
├── MeasurementId (Value Object)
├── DeviceId (Value Object)
├── MetricType (Value Object)
├── Value (Value Object)
├── Unit (Value Object)
├── Timestamp (Value Object)
├── Quality (Value Object)
└── Metadata (Value Object)
```

#### Сущности:
- **Measurement** - единичное измерение с датчика
- **MetricSeries** - временной ряд измерений
- **Alert** - предупреждение на основе данных

#### Value Objects:
- **MetricType** - тип метрики (temperature, humidity, pressure)
- **MeasurementValue** - значение измерения с валидацией
- **Unit** - единица измерения
- **Quality** - качество данных (good, bad, uncertain)
- **TimeRange** - временной диапазон

#### Доменные сервисы:
- **MeasurementCollectionService** - сбор данных с устройств
- **DataValidationService** - валидация входящих данных
- **AlertingService** - генерация предупреждений
- **AggregationService** - агрегация данных

#### Доменные события:
- **MeasurementReceived** - получено новое измерение
- **AlertTriggered** - сработало предупреждение
- **DataQualityIssue** - проблема с качеством данных

### 2.3 Bounded Context: User Management (Управление пользователями)

#### Агрегат: User
```
User (Aggregate Root)
├── UserId (Value Object)
├── Email (Value Object)
├── Profile (Entity)
├── Subscription (Entity)
├── Permissions (Value Object Collection)
└── Preferences (Value Object)
```

#### Сущности:
- **User** - пользователь системы
- **Profile** - профиль пользователя
- **Subscription** - подписка пользователя

#### Value Objects:
- **Email** - email с валидацией
- **Permission** - разрешение пользователя
- **SubscriptionType** - тип подписки (basic, premium, enterprise)
- **UserPreferences** - настройки пользователя

#### Доменные сервисы:
- **AuthenticationService** - аутентификация
- **AuthorizationService** - авторизация
- **SubscriptionService** - управление подписками

#### Доменные события:
- **UserRegistered** - пользователь зарегистрирован
- **UserAuthenticated** - пользователь аутентифицирован
- **SubscriptionChanged** - изменилась подписка

### 2.4 Bounded Context: Home Management (Управление домами)

#### Агрегат: Home
```
Home (Aggregate Root)
├── HomeId (Value Object)
├── Address (Value Object)
├── Owner (Value Object)
├── Rooms (Entity Collection)
├── Devices (Value Object Collection)
└── Configuration (Value Object)
```

#### Сущности:
- **Home** - дом пользователя
- **Room** - комната в доме
- **Floor** - этаж дома

#### Value Objects:
- **Address** - адрес дома
- **RoomType** - тип комнаты (living_room, bedroom, kitchen)
- **HomeConfiguration** - конфигурация дома

#### Доменные сервисы:
- **HomeSetupService** - настройка структуры дома
- **DeviceAssignmentService** - привязка устройств к комнатам

#### Доменные события:
- **HomeCreated** - создан дом
- **RoomAdded** - добавлена комната
- **DeviceAssigned** - устройство привязано к комнате

### 2.5 Bounded Context: Automation (Автоматизация)

#### Агрегат: Scenario
```
Scenario (Aggregate Root)
├── ScenarioId (Value Object)
├── Name (Value Object)
├── Triggers (Entity Collection)
├── Conditions (Entity Collection)
├── Actions (Entity Collection)
├── Status (Value Object)
└── Schedule (Value Object)
```

#### Сущности:
- **Scenario** - сценарий автоматизации
- **Trigger** - триггер сценария
- **Condition** - условие выполнения
- **Action** - действие сценария

#### Value Objects:
- **TriggerType** - тип триггера (time, sensor, manual)
- **ConditionOperator** - оператор условия (equals, greater, less)
- **ActionType** - тип действия (device_command, notification)
- **Schedule** - расписание выполнения

#### Доменные сервисы:
- **ScenarioExecutionService** - выполнение сценариев
- **TriggerEvaluationService** - оценка триггеров
- **ConditionEvaluationService** - оценка условий

#### Доменные события:
- **ScenarioTriggered** - сценарий запущен
- **ScenarioExecuted** - сценарий выполнен
- **ScenarioFailed** - сценарий завершился с ошибкой

### 2.6 Bounded Context: Notifications (Уведомления)

#### Агрегат: Notification
```
Notification (Aggregate Root)
├── NotificationId (Value Object)
├── Recipient (Value Object)
├── Message (Value Object)
├── Channel (Value Object)
├── Priority (Value Object)
├── Status (Value Object)
└── Metadata (Value Object)
```

#### Сущности:
- **Notification** - уведомление
- **NotificationTemplate** - шаблон уведомления
- **DeliveryAttempt** - попытка доставки

#### Value Objects:
- **NotificationChannel** - канал доставки (email, sms, push)
- **Priority** - приоритет уведомления
- **NotificationStatus** - статус доставки

#### Доменные сервисы:
- **NotificationDeliveryService** - доставка уведомлений
- **TemplateService** - работа с шаблонами

#### Доменные события:
- **NotificationSent** - уведомление отправлено
- **NotificationDelivered** - уведомление доставлено
- **NotificationFailed** - ошибка доставки

## 3. Взаимодействие между контекстами

### 3.1 Context Map (Карта контекстов)

```
[User Management] ---> [Home Management] : Customer/Supplier
[Home Management] ---> [Device Management] : Customer/Supplier  
[Device Management] ---> [Telemetry] : Publisher/Subscriber
[Telemetry] ---> [Automation] : Publisher/Subscriber
[Automation] ---> [Device Management] : Customer/Supplier
[Automation] ---> [Notifications] : Customer/Supplier
[User Management] <--- [Notifications] : Customer/Supplier
```

### 3.2 Интеграционные события

#### Между Device Management и Telemetry:
- `DeviceDataReceived` - получены данные с устройства
- `DeviceStatusChanged` - изменился статус устройства

#### Между Telemetry и Automation:
- `ThresholdExceeded` - превышен порог значения
- `DataPatternDetected` - обнаружен паттерн в данных

#### Между Automation и Device Management:
- `ExecuteDeviceCommand` - выполнить команду устройства

#### Между Automation и Notifications:
- `SendNotification` - отправить уведомление

## 4. Рекомендации по реализации

### 4.1 Архитектурные паттерны
- **Hexagonal Architecture** для каждого микросервиса
- **CQRS** для разделения команд и запросов
- **Event Sourcing** для критически важных агрегатов
- **Saga Pattern** для распределенных транзакций

### 4.2 Технические решения
- **Event Store** для хранения доменных событий
- **Message Broker** для асинхронной коммуникации
- **API Gateway** для управления внешними запросами
- **Service Mesh** для управления межсервисной коммуникацией

### 4.3 Стратегия миграции
1. **Выделение Device Management** как первого микросервиса
2. **Создание Event Bus** для асинхронной коммуникации
3. **Постепенное выделение** остальных контекстов
4. **Рефакторинг** существующего кода под доменную модель