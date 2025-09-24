# Проектная работа 1 спринта - "Тёплый дом"

## Задание 1. Анализ и планирование

### 1.1 Анализ функциональности монолитного приложения

#### Текущая функциональность системы

**Управление отоплением:**
- Удалённое включение/выключение отопления через REST API
- Управление статусом отопительных устройств
- Базовые операции CRUD для управления датчиками

**Мониторинг температуры:**
- Сбор данных с температурных датчиков через внешний Temperature API
- Хранение информации о датчиках в PostgreSQL
- Веб-интерфейс для просмотра текущей температуры
- REST API для получения данных о температуре по местоположению

#### Ограничения текущей системы
- Поддержка только температурных датчиков
- Отсутствие системы пользователей и домов
- Нет автоматизации и сценариев
- Требуется выезд специалиста для подключения каждого датчика

### 1.2 Анализ архитектуры монолитного приложения

#### Технологический стек
- **Язык программирования:** Go
- **База данных:** PostgreSQL
- **Web-фреймворк:** Gin
- **Архитектурный паттерн:** Layered Architecture
- **Контейнеризация:** Docker

#### Структура приложения
```
smart_home/
├── main.go                    # Точка входа, инициализация
├── handlers/                  # HTTP обработчики
│   └── sensors.go            # API для работы с датчиками
├── services/                  # Бизнес-логика
│   └── temperature_service.go # Интеграция с внешним API
├── models/                    # Модели данных
│   └── sensor.go             # Модель датчика
├── db/                        # Слой доступа к данным
│   └── db.go                 # Database Access Layer
└── init.sql                  # Схема базы данных
```

#### Сильные стороны монолита
- **Простота разработки:** Все компоненты в одном приложении
- **Простота развертывания:** Один исполняемый файл
- **Производительность:** Отсутствие сетевых вызовов между компонентами
- **Консистентность данных:** ACID транзакции в рамках одной БД
- **Отладка:** Легко отслеживать выполнение запросов

#### Слабые стороны монолита
- **Масштабируемость:** Невозможно масштабировать компоненты независимо
- **Развертывание:** Требует остановки всего приложения для обновления
- **Технологическая гибкость:** Привязка к одному стеку технологий
- **Команды разработки:** Сложно распараллелить работу между командами
- **Отказоустойчивость:** Сбой одного компонента влияет на всю систему
- **Взаимодействие:** Только синхронная обработка запросов

### 1.3 Определение доменов и границ контекстов (DDD)

#### Выделенные Bounded Contexts

**1. Device Management (Управление устройствами)**
- **Ответственность:** Регистрация, управление и мониторинг IoT устройств
- **Ключевые сущности:** Device, Sensor, Actuator, DeviceType
- **Основные операции:** Регистрация устройств, отправка команд, мониторинг состояния

**2. Telemetry (Телеметрия и мониторинг)**
- **Ответственность:** Сбор, хранение и анализ данных с датчиков
- **Ключевые сущности:** Measurement, MetricType, TimeSeriesData, Alert
- **Основные операции:** Сбор данных, агрегация, генерация предупреждений

**3. User Management (Управление пользователями)**
- **Ответственность:** Аутентификация, авторизация, управление профилями
- **Ключевые сущности:** User, Role, Permission, Subscription
- **Основные операции:** Регистрация, аутентификация, управление подписками

**4. Home Management (Управление домами)**
- **Ответственность:** Организация устройств по домам и комнатам
- **Ключевые сущности:** Home, Room, Location, Floor
- **Основные операции:** Создание структуры дома, привязка устройств

**5. Automation (Автоматизация и сценарии)**
- **Ответственность:** Создание и выполнение сценариев автоматизации
- **Ключевые сущности:** Scenario, Rule, Trigger, Action, Schedule
- **Основные операции:** Создание сценариев, выполнение правил, обработка событий

**6. Notifications (Система уведомлений)**
- **Ответственность:** Отправка уведомлений пользователям
- **Ключевые сущности:** Notification, NotificationChannel, Alert, Template
- **Основные операции:** Отправка уведомлений, управление каналами связи

#### Context Map (Взаимодействие контекстов)
```
[User Management] ---> [Home Management] : Customer/Supplier
[Home Management] ---> [Device Management] : Customer/Supplier  
[Device Management] ---> [Telemetry] : Publisher/Subscriber
[Telemetry] ---> [Automation] : Publisher/Subscriber
[Automation] ---> [Device Management] : Customer/Supplier
[Automation] ---> [Notifications] : Customer/Supplier
[User Management] <--- [Notifications] : Customer/Supplier
```

### 1.4 Диаграмма контекста системы (C4 Model)

Создана диаграмма контекста в формате PlantUML, которая показывает:

**Внешние пользователи:**
- **Пользователь** - владелец умного дома
- **Администратор** - специалист по настройке системы

**Основная система:**
- **Smart Home Monolith** - текущее монолитное приложение

**Внешние системы:**
- **Temperature API** - внешний сервис для получения данных с датчиков
- **PostgreSQL Database** - база данных системы
- **Температурные датчики** - физические IoT устройства
- **Реле отопления** - исполнительные устройства

**Основные потоки взаимодействия:**
- Пользователи управляют системой через HTTPS/REST API
- Приложение получает данные от внешнего Temperature API
- Система отправляет команды на физические устройства
- Данные сохраняются в PostgreSQL

### 1.5 Рекомендации по переходу к микросервисной архитектуре

#### Целевая архитектура (MVP)
1. **Device Service** - управление устройствами и датчиками
2. **Telemetry Service** - сбор и хранение телеметрии
3. **User Service** - аутентификация и управление пользователями
4. **Home Service** - управление структурой домов
5. **Automation Service** - базовые сценарии автоматизации
6. **Notification Service** - система уведомлений
7. **API Gateway** - единая точка входа

#### Стратегия миграции: Strangler Fig Pattern
**Фаза 1:** Подготовка инфраструктуры
- Настройка CI/CD pipeline
- Развертывание мониторинга (Prometheus + Grafana)
- Создание API Gateway

**Фаза 2:** Выделение Device Service
- Миграция логики управления устройствами
- Создание отдельной базы данных
- Настройка межсервисного взаимодействия

**Фаза 3:** Последовательное выделение остальных сервисов
- User Service → Home Service → Telemetry Service → Automation Service → Notification Service

**Фаза 4:** Оптимизация и масштабирование
- Внедрение Event Sourcing
- Горизонтальное масштабирование
- Оптимизация производительности

#### Технологические решения
- **Message Broker:** Apache Kafka для асинхронного взаимодействия
- **Service Discovery:** Consul или Kubernetes DNS
- **Configuration Management:** Consul KV или ConfigMaps
- **Monitoring:** Prometheus + Grafana + Jaeger
- **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana)
- **Databases:** PostgreSQL, MongoDB, InfluxDB (для телеметрии)

#### Архитектурные паттерны
- **Database per Service** - отдельная БД для каждого микросервиса
- **Event-Driven Architecture** - асинхронное взаимодействие через события
- **CQRS** - разделение команд и запросов для сложных доменов
- **Circuit Breaker** - повышение отказоустойчивости
- **Saga Pattern** - управление распределенными транзакциями

### 1.6 Ожидаемые результаты

#### Бизнес-преимущества
- **Масштабируемость:** Независимое масштабирование компонентов по нагрузке
- **Гибкость:** Быстрое внедрение новых функций и модулей
- **Надежность:** Изоляция отказов, graceful degradation
- **Time-to-Market:** Параллельная разработка разными командами

#### Технические преимущества
- **Технологическое разнообразие:** Оптимальный выбор технологий для каждой задачи
- **Независимое развертывание:** Обновления без остановки всей системы
- **Горизонтальное масштабирование:** Масштабирование по требованию
- **Улучшенная отказоустойчивость:** Система продолжает работать при сбоях отдельных компонентов

## Заключение по Заданию 1

Проведенный анализ показал, что текущая монолитная архитектура не соответствует требованиям масштабируемой экосистемы умных домов. Применение принципов Domain-Driven Design позволило выделить 6 четких доменных границ, которые станут основой для микросервисной архитектуры.

Предложенная стратегия поэтапной миграции с использованием Strangler Fig Pattern минимизирует риски и обеспечивает плавный переход к целевой архитектуре. Внедрение event-driven подхода и современных инфраструктурных решений позволит создать масштабируемую, надежную и гибкую систему, соответствующую бизнес-целям компании "Тёплый дом".

## Задание 2. Проектирование микросервисной архитектуры

### 2.1 Декомпозиция приложения на микросервисы

На основе доменного анализа из Задания 1 была выполнена декомпозиция монолитного приложения на следующие микросервисы:

#### Основные микросервисы

**1. Device Service (Порт: 8081)**
- **Ответственность**: Управление IoT устройствами, отправка команд, мониторинг состояния
- **База данных**: PostgreSQL (device_db)
- **Ключевые сущности**: Device, Sensor, Actuator, DeviceCommand, DeviceCapability

**2. Telemetry Service (Порт: 8082)**
- **Ответственность**: Сбор и анализ данных телеметрии, временные ряды, предупреждения
- **База данных**: InfluxDB (telemetry_db) + Redis (кэш)
- **Ключевые сущности**: Measurement, MetricType, TimeSeriesData, Alert

**3. User Service (Порт: 8083)**
- **Ответственность**: Аутентификация, управление пользователями, подписки
- **База данных**: PostgreSQL (user_db)
- **Ключевые сущности**: User, Profile, Role, Subscription

**4. Home Service (Порт: 8084)**
- **Ответственность**: Управление структурой домов, комнат, привязка устройств
- **База данных**: PostgreSQL (home_db)
- **Ключевые сущности**: Home, Room, Floor, Location

**5. Automation Service (Порт: 8085)**
- **Ответственность**: Сценарии автоматизации, триггеры, выполнение правил
- **База данных**: PostgreSQL (automation_db) + Redis (состояния)
- **Ключевые сущности**: Scenario, Trigger, Condition, Action

**6. Notification Service (Порт: 8086)**
- **Ответственность**: Отправка уведомлений, управление каналами доставки
- **База данных**: PostgreSQL (notification_db) + Redis (очереди)
- **Ключевые сущности**: Notification, NotificationTemplate, DeliveryChannel

**7. API Gateway (Порт: 8080)**
- **Ответственность**: Единая точка входа, маршрутизация, аутентификация, rate limiting

#### Инфраструктурные компоненты
- **Apache Kafka** - асинхронная коммуникация между сервисами
- **Consul** - service discovery и configuration management
- **Redis** - кэширование, сессии, очереди
- **Prometheus + Grafana** - мониторинг и метрики
- **ELK Stack** - централизованное логирование
- **Jaeger** - distributed tracing

### 2.2 Определение взаимодействия

#### Синхронное взаимодействие (REST API)
- **User Service ↔ Home Service**: Управление домами пользователя
- **Home Service ↔ Device Service**: Привязка устройств к комнатам
- **Device Service ↔ Telemetry Service**: Получение данных устройств
- **Automation Service ↔ Device Service**: Отправка команд устройствам

#### Асинхронное взаимодействие (Events через Kafka)
- **Device Service → Telemetry Service**: События данных устройств
- **Telemetry Service → Automation Service**: События превышения порогов
- **Automation Service → Device Service**: Команды выполнения действий
- **Automation Service → Notification Service**: Запросы на отправку уведомлений

#### Основные топики Kafka
- `device.events` - события устройств
- `telemetry.data` - данные телеметрии
- `automation.triggers` - триггеры автоматизации
- `notifications.queue` - очередь уведомлений

### 2.3 Визуализация архитектуры

#### C4 - Уровень контейнеров (Containers)
Создана диаграмма [`c4-container-diagram.puml`](docs/c4-container-diagram.puml), показывающая:
- Все микросервисы и их взаимодействие
- Специализированные базы данных для каждого сервиса
- Инфраструктурные компоненты (Kafka, Redis, мониторинг)
- Внешние системы (IoT устройства, мобильные приложения)

#### C4 - Уровень компонентов (Components)
Детализированы ключевые микросервисы:

**Device Service Components** ([`c4-device-service-components.puml`](docs/c4-device-service-components.puml)):
- Device API Controller - REST API для управления устройствами
- Device Command Handler - обработка команд устройствам
- Device State Manager - управление состоянием устройств
- Device Registry - регистрация и каталог устройств
- Device Health Monitor - мониторинг состояния устройств
- IoT Protocol Adapter - адаптер для IoT протоколов

**Automation Service Components** ([`c4-automation-service-components.puml`](docs/c4-automation-service-components.puml)):
- Scenario Manager - управление жизненным циклом сценариев
- Trigger Engine - обработка триггеров и условий
- Rule Evaluator - оценка правил и условий
- Action Executor - выполнение действий сценариев
- Scheduler - планировщик задач по времени
- Event Processor - обработка входящих событий

#### C4 - Уровень кода (Code)
Для критических частей системы созданы детальные диаграммы:

**Device Service Domain Model** ([`c4-device-service-code-level.puml`](docs/c4-device-service-code-level.puml)):
- Доменные сущности: Device, Sensor, Actuator, DeviceCommand
- Value Objects: DeviceId, DeviceType, DeviceStatus, CommandResult
- Domain Services: DeviceRegistrationService, DeviceCommandService
- Domain Events: DeviceRegisteredEvent, DeviceCommandExecutedEvent
- Repository Interfaces: DeviceRepository, CommandRepository

**Device Command Execution Sequence** ([`device-command-sequence.puml`](docs/device-command-sequence.puml)):
- Полная последовательность выполнения команды устройству
- От пользователя через Mobile App → API Gateway → Device Service → IoT Device
- Асинхронная обработка событий через Kafka
- Интеграция с Automation и Telemetry сервисами

### 2.4 Архитектурные решения и паттерны

#### Применяемые паттерны
- **Database per Service** - отдельная БД для каждого микросервиса
- **Event-Driven Architecture** - асинхронное взаимодействие через события
- **Hexagonal Architecture** - чистая архитектура внутри каждого сервиса
- **CQRS** - разделение команд и запросов для высоконагруженных сервисов
- **Circuit Breaker** - защита от каскадных сбоев
- **Saga Pattern** - управление распределенными транзакциями

#### Стратегии консистентности данных
- **Eventual Consistency** - для большинства межсервисных операций
- **Strong Consistency** - для критических операций внутри сервиса
- **Компенсирующие транзакции** - при сбоях в распределенных операциях

#### Безопасность
- **OAuth 2.0 + JWT** - централизованная аутентификация
- **mTLS** - межсервисное взаимодействие
- **API Gateway** - централизованная авторизация и rate limiting

### 2.5 Преимущества новой архитектуры

#### Масштабируемость
- Независимое масштабирование каждого сервиса по нагрузке
- Специализированные базы данных (PostgreSQL, InfluxDB, Redis)
- Горизонтальное масштабирование по требованию

#### Отказоустойчивость
- Изоляция сбоев в рамках одного сервиса
- Circuit Breaker Pattern для защиты от каскадных сбоев
- Graceful degradation при недоступности компонентов

#### Гибкость разработки
- Независимые команды разработки для каждого сервиса
- Технологическое разнообразие для разных задач
- Быстрое внедрение новых функций без влияния на другие сервисы

#### Производительность
- Асинхронная обработка тяжелых операций через Kafka
- Кэширование на уровне сервисов с Redis
- Оптимизированные запросы к специализированным БД

### 2.6 Стратегия миграции

#### Фазы внедрения
**Фаза 1: Инфраструктура**
- Настройка Kafka, Redis, мониторинга
- Развертывание API Gateway
- Настройка CI/CD pipeline

**Фаза 2: Базовые сервисы**
- User Service (аутентификация)
- Device Service (управление устройствами)
- Home Service (структура домов)

**Фаза 3: Расширенная функциональность**
- Telemetry Service (сбор данных)
- Automation Service (сценарии)
- Notification Service (уведомления)

**Фаза 4: Оптимизация**
- Performance tuning
- Горизонтальное масштабирование
- Advanced monitoring

## Заключение по Заданию 2

Разработанная микросервисная архитектура обеспечивает четкое разделение ответственности между доменами, масштабируемость и отказоустойчивость системы. Применение современных архитектурных паттернов и технологий позволяет создать гибкую и производительную экосистему умных домов.

Созданная документация включает диаграммы C4 на всех уровнях детализации - от высокоуровневого обзора контейнеров до детальных доменных моделей и последовательностей взаимодействия. Это обеспечивает полное понимание архитектуры для всех участников проекта.

## Задание 3. Разработка ER-диаграммы

### 3.1 Идентификация сущностей

На основе спроектированных микросервисов определены ключевые сущности для каждой базы данных в соответствии с принципом Database per Service:

#### Распределение сущностей по микросервисам

| Микросервис | Основные сущности | База данных |
|-------------|-------------------|-------------|
| **User Service** | User, Profile, Subscription, Role, UserRole, Session | PostgreSQL |
| **Home Service** | Home, Room, Floor, Location, HomeConfiguration | PostgreSQL |
| **Device Service** | Device, DeviceType, DeviceCommand, DeviceCapability, Manufacturer | PostgreSQL |
| **Automation Service** | Scenario, ScenarioExecution, Trigger, Condition, Action, ActionExecution | PostgreSQL |
| **Notification Service** | Notification, NotificationTemplate, DeliveryAttempt, DeliveryChannel, NotificationPreference, NotificationQueue | PostgreSQL |
| **Telemetry Service** | Measurement, MetricType, Alert, AlertRule | InfluxDB |

**Общее количество сущностей**: 32

### 3.2 Определение атрибутов

Для каждой сущности определены детальные атрибуты с учетом:

#### Ключевые принципы проектирования атрибутов:
- **UUID** для всех первичных ключей (глобальная уникальность)
- **TIMESTAMP WITH TIME ZONE** для временных меток
- **JSONB** для гибких конфигураций и метаданных
- **ENUM** для ограниченных наборов значений
- **Обязательные поля** created_at и updated_at для аудита

#### Примеры ключевых сущностей:

**Device (Device Service)**:
- `id` (UUID, PK) - уникальный идентификатор устройства
- `name` (VARCHAR(100)) - название устройства
- `serial_number` (VARCHAR(100), UNIQUE) - серийный номер
- `device_type_id` (UUID, FK) - тип устройства
- `home_id` (UUID, External FK) - ссылка на дом (Home Service)
- `room_id` (UUID, External FK) - ссылка на комнату (Home Service)
- `status` (ENUM) - статус устройства (active, inactive, error, offline)
- `configuration` (JSONB) - конфигурация устройства
- `capabilities` (JSONB) - возможности устройства

**Scenario (Automation Service)**:
- `id` (UUID, PK) - уникальный идентификатор сценария
- `user_id` (UUID, External FK) - ссылка на пользователя (User Service)
- `home_id` (UUID, External FK) - ссылка на дом (Home Service)
- `name` (VARCHAR(100)) - название сценария
- `enabled` (BOOLEAN) - включен ли сценарий
- `triggers` (JSONB) - триггеры сценария
- `conditions` (JSONB) - условия выполнения
- `actions` (JSONB) - действия сценария

### 3.3 Описание связей между сущностями

#### Внутрисервисные связи:
- **User ↔ Profile**: Один-к-одному (1:1)
- **User ↔ Subscription**: Один-ко-многим (1:N)
- **Home ↔ Room**: Один-ко-многим (1:N)
- **DeviceType ↔ Device**: Один-ко-многим (1:N)
- **Device ↔ DeviceCommand**: Один-ко-многим (1:N)
- **Scenario ↔ ScenarioExecution**: Один-ко-многим (1:N)
- **NotificationTemplate ↔ Notification**: Один-ко-многим (1:N)

#### Межсервисные связи (External FK):
- **User → Home**: Пользователь владеет домами (1:N)
- **User → DeviceCommand**: Пользователь выдает команды устройствам (1:N)
- **User → Scenario**: Пользователь создает сценарии (1:N)
- **User → Notification**: Пользователь получает уведомления (1:N)
- **Home → Device**: Дом содержит устройства (1:N)
- **Room → Device**: Комната содержит устройства (1:N)
- **Device → Measurement**: Устройство генерирует измерения (1:N)

### 3.4 Построение ER-диаграмм

Созданы детальные ER-диаграммы для каждого микросервиса:

#### User Service ER Diagram
**Файл**: [`er-user-service.puml`](docs/er-user-service.puml)
- Полная модель пользователей с профилями, подписками и ролями
- Система сессий для безопасности
- Поддержка множественных подписок и ролей

#### Home Service ER Diagram
**Файл**: [`er-home-service.puml`](docs/er-home-service.puml)
- Иерархическая структура: Home → Floor → Room → Location
- Поддержка координат для точного позиционирования устройств
- Гибкая конфигурация домов через JSONB

#### Device Service ER Diagram
**Файл**: [`er-device-service.puml`](docs/er-device-service.puml)
- Центральная модель IoT устройств с типизацией
- Система команд с отслеживанием выполнения
- Гибкие возможности устройств через DeviceCapability
- Поддержка различных IoT протоколов

#### Automation Service ER Diagram
**Файл**: [`er-automation-service.puml`](docs/er-automation-service.puml)
- Сложная модель сценариев с триггерами, условиями и действиями
- Детальное логирование выполнения сценариев
- Поддержка retry механизмов и тайм-аутов
- Приоритизация и планирование выполнения

#### Notification Service ER Diagram
**Файл**: [`er-notification-service.puml`](docs/er-notification-service.puml)
- Система уведомлений с множественными каналами доставки
- Шаблонизация сообщений
- Персональные настройки пользователей
- Очереди и повторные попытки доставки

#### Microservices Overview ER Diagram
**Файл**: [`er-microservices-overview.puml`](docs/er-microservices-overview.puml)
- Высокоуровневая диаграмма всех микросервисов
- Визуализация межсервисных связей
- Обзор основных сущностей каждого сервиса

### 3.5 Особенности проектирования базы данных

#### Database per Service Pattern
**Преимущества**:
- Независимость развертывания и масштабирования
- Технологическое разнообразие (PostgreSQL, InfluxDB, Redis)
- Изоляция данных и безопасность
- Автономность команд разработки

**Стратегии обеспечения целостности**:
- **Strong Consistency** внутри микросервиса
- **Eventual Consistency** между микросервисами
- **Saga Pattern** для распределенных транзакций
- **Компенсирующие действия** при сбоях

#### Специализированные решения
- **PostgreSQL** - для транзакционных данных с ACID гарантиями
- **InfluxDB** - для временных рядов телеметрии с оптимизацией производительности
- **Redis** - для кэширования, сессий и очередей с in-memory производительностью

#### Индексная стратегия
- **Primary Keys** (UUID) для уникальной идентификации
- **Foreign Keys** для связей между сущностями
- **Composite indexes** для частых запросов
- **JSONB indexes** для поиска в JSON данных
- **Time-based indexes** для временных запросов

### 3.6 Миграционная стратегия

#### Поэтапная миграция из монолита:
1. **Анализ данных** - аудит существующих данных и зависимостей
2. **Создание схем** - DDL скрипты для каждого микросервиса
3. **Миграция данных** - поэтапное перенесение с проверкой целостности
4. **Переключение** - постепенное переключение трафика с мониторингом

#### Обеспечение Zero Downtime:
- Blue-Green Deployment для баз данных
- Read Replicas для минимизации простоя
- Event Sourcing для критических данных
- Compensating Actions при сбоях

## Заключение по Заданию 3

Разработанная модель данных обеспечивает четкое разделение данных между микросервисами при сохранении логической целостности всей системы. Применение принципа Database per Service позволяет каждому микросервису использовать оптимальные технологии баз данных для своих задач.

Созданные ER-диаграммы предоставляют полное представление о структуре данных на всех уровнях - от детальных схем отдельных сервисов до высокоуровневого обзора всей экосистемы. Модель готова для реализации и поддерживает все требования масштабируемой IoT платформы.

## Задание 4. Создание и документирование API

### 4.1 Выбор типов API

Для обеспечения эффективного взаимодействия между микросервисами выбраны два типа API:

#### REST API (Синхронное взаимодействие)
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

#### AsyncAPI (Асинхронное взаимодействие)
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

### 4.2 Проектирование и документирование API

#### Device Service API
**Файл**: [`device-service-openapi.yaml`](docs/device-service-openapi.yaml)

**Ключевые endpoints**:

**Управление устройствами**:
- `GET /devices` - получение списка устройств с фильтрацией по дому, комнате, типу, статусу
- `GET /devices/{deviceId}` - получение детальной информации об устройстве
- `POST /devices` - регистрация нового устройства в системе
- `PUT /devices/{deviceId}` - обновление информации об устройстве
- `DELETE /devices/{deviceId}` - удаление устройства из системы

**Управление командами**:
- `POST /devices/{deviceId}/commands` - отправка команды устройству (асинхронная обработка)
- `GET /devices/{deviceId}/commands/{commandId}` - получение статуса выполнения команды

**Пример запроса отправки команды**:
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

**Пример ответа**:
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

#### User Service API
**Ключевые endpoints**:
- `POST /auth/login` - аутентификация пользователя с получением JWT токена
- `GET /users/me` - получение информации о текущем пользователе
- `PUT /users/me` - обновление профиля пользователя

#### Home Service API
**Ключевые endpoints**:
- `GET /homes` - получение списка домов пользователя
- `GET /homes/{homeId}/rooms` - получение списка комнат в доме
- `POST /homes` - создание нового дома
- `POST /homes/{homeId}/rooms` - создание новой комнаты

#### Automation Service API
**Ключевые endpoints**:
- `GET /scenarios` - получение списка сценариев автоматизации
- `POST /scenarios` - создание нового сценария
- `POST /scenarios/{scenarioId}/execute` - ручное выполнение сценария
- `GET /scenarios/{scenarioId}/executions` - история выполнения сценария

### 4.3 AsyncAPI спецификация

**Файл**: [`smart-home-asyncapi.yaml`](docs/smart-home-asyncapi.yaml)

#### Основные каналы событий:

**device.events** - События устройств:
- `DeviceStatusChanged` - изменение статуса устройства
- `DeviceCommandExecuted` - выполнение команды устройства
- `DeviceRegistered` - регистрация нового устройства

**Пример события изменения статуса устройства**:
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

**telemetry.data** - Данные телеметрии:
- `MeasurementReceived` - получение новых измерений с датчиков
- `AlertTriggered` - срабатывание предупреждения по пороговым значениям

**automation.events** - События автоматизации:
- `ScenarioTriggered` - запуск сценария автоматизации
- `ScenarioExecuted` - завершение выполнения сценария
- `ExecuteDeviceCommand` - команда выполнения действия на устройстве

**notification.events** - События уведомлений:
- `SendNotification` - запрос на отправку уведомления пользователю
- `NotificationDelivered` - подтверждение доставки уведомления

### 4.4 Контракты взаимодействия

#### Стандартизация форматов

**Коды ответов HTTP**:
- **200 OK** - запрос выполнен успешно
- **201 Created** - ресурс создан успешно
- **202 Accepted** - запрос принят к обработке (асинхронные операции)
- **400 Bad Request** - некорректный запрос
- **401 Unauthorized** - требуется аутентификация
- **403 Forbidden** - доступ запрещен
- **404 Not Found** - ресурс не найден
- **422 Unprocessable Entity** - ошибка валидации данных
- **500 Internal Server Error** - внутренняя ошибка сервера

**Стандартный формат ошибок**:
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

#### Аутентификация и авторизация

**JWT Bearer Token**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Области доступа (Scopes)**:
- `devices:read` - чтение информации об устройствах
- `devices:write` - управление устройствами
- `devices:command` - отправка команд устройствам
- `homes:read` - чтение информации о домах
- `homes:write` - управление домами
- `scenarios:read` - чтение сценариев
- `scenarios:write` - управление сценариями
- `scenarios:execute` - выполнение сценариев

#### Версионирование и Rate Limiting

**Версионирование**: URL-based (`/api/v1/`, `/api/v2/`)
**Rate Limiting**:
- Аутентифицированные пользователи: 1000 запросов/час
- Команды устройствам: 100 команд/час на устройство
- Создание сценариев: 50 операций/час

### 4.5 Примеры интеграции

#### Сценарий: Автоматическое управление температурой

1. **Получение данных телеметрии** (AsyncAPI):
```json
{
  "eventType": "MeasurementReceived",
  "deviceId": "thermostat-001",
  "measurements": [
    {"type": "temperature", "value": 18.0, "unit": "°C"}
  ]
}
```

2. **Срабатывание сценария** (AsyncAPI):
```json
{
  "eventType": "ScenarioTriggered",
  "scenarioId": "heating-scenario",
  "triggeredBy": "temperature_threshold"
}
```

3. **Выполнение команды устройству** (REST API):
```http
POST /api/v1/devices/thermostat-001/commands
{
  "command": "set_temperature",
  "parameters": {"temperature": 22.0}
}
```

## Заключение по Заданию 4

Разработанные API спецификации обеспечивают полноценное взаимодействие между микросервисами экосистемы "Тёплый дом":

- **REST API** для синхронных операций CRUD и управления устройствами
- **AsyncAPI** для событийно-ориентированной архитектуры и реактивной обработки
- **Стандартизированные контракты** с детальными примерами запросов и ответов
- **Безопасность** через JWT аутентификацию и scope-based авторизацию
- **Масштабируемость** через версионирование и rate limiting
- **Наблюдаемость** через трассировку запросов и стандартизированное логирование

API готовы для реализации и обеспечивают надежное взаимодействие между всеми компонентами микросервисной архитектуры.

## Задание 5. Создание Dockerfile и интеграция с PostgreSQL

### 5.1 Реализация Temperature API Service

#### Технические характеристики
- **Язык программирования**: Go 1.21
- **Web-фреймворк**: Gin (высокопроизводительный HTTP роутер)
- **Порт**: 8081 (согласно требованиям)
- **Архитектура**: RESTful API с JSON ответами
- **Контейнеризация**: Docker с multi-stage build

#### Основная функциональность
Создан полнофункциональный микросервис [`apps/temperature-api/`](apps/temperature-api/) со следующими возможностями:

**API Endpoints**:
- `GET /health` - проверка состояния сервиса
- `GET /temperature?location={location}` - получение температуры по местоположению
- `GET /temperature/{sensorId}` - получение температуры по ID датчика

**Алгоритм симуляции температуры**:
- **Базовые температуры по локациям**:
  - Гостиная: 22°C ± 3°C
  - Спальня: 20°C ± 2.5°C
  - Кухня: 24°C ± 4°C
  - Ванная: 23°C ± 2°C
  - Гараж: 15°C ± 8°C
  - Улица: 10°C ± 15°C
- **Временные вариации**: ±1°C для дневного/ночного цикла
- **Случайные отклонения**: в пределах реалистичных диапазонов

**Пример ответа API**:
```json
{
  "value": 22.3,
  "unit": "°C",
  "timestamp": "2025-09-15T12:30:00Z",
  "location": "living_room",
  "status": "active",
  "sensor_id": "sensor-living_room-456",
  "sensor_type": "temperature",
  "description": "Temperature reading for living_room"
}
```

### 5.2 Docker Implementation

#### Dockerfile Architecture
Создан оптимизированный [`apps/temperature-api/Dockerfile`](apps/temperature-api/Dockerfile) с использованием:

**Multi-stage Build**:
- **Build Stage**: Golang 1.21 Alpine для компиляции
- **Runtime Stage**: Alpine Linux для минимального размера образа

**Безопасность**:
- Выполнение от имени non-root пользователя
- Минимальная атака поверхность с Alpine Linux
- Health check для мониторинга состояния

**Оптимизация**:
- Статическая компиляция для портабельности
- Кэширование слоев Docker для быстрой пересборки
- Размер финального образа ~20MB

### 5.3 PostgreSQL Integration

#### Database Configuration
Настроена полная интеграция с PostgreSQL:

**Конфигурация сервиса**:
- **Image**: PostgreSQL 16 Alpine
- **Database**: `smarthome`
- **Credentials**: postgres/postgres (для разработки)
- **Port**: 5432
- **Volume**: Persistent storage для данных

#### Database Schema
Создан комплексный скрипт инициализации [`apps/postgres-init/init.sql`](apps/postgres-init/init.sql):

**Основные таблицы**:
- `users` - пользователи системы с аутентификацией
- `homes` - дома пользователей
- `rooms` - комнаты в домах
- `device_types` - типы IoT устройств
- `devices` - IoT устройства с привязкой к комнатам
- `sensor_readings` - данные с датчиков (временные ряды)
- `device_commands` - команды устройствам с отслеживанием статуса
- `automation_rules` - правила автоматизации
- `notifications` - система уведомлений

**Ключевые особенности**:
- **UUID** для всех первичных ключей
- **JSONB** для гибких конфигураций
- **Временные метки** с часовыми поясами
- **Индексы** для оптимизации производительности
- **Триггеры** для автоматического обновления timestamp
- **Тестовые данные** для разработки

### 5.4 Service Orchestration

#### Docker Compose Configuration
Обновлен [`apps/docker-compose.yml`](apps/docker-compose.yml) для полной оркестрации:

**Сервисы**:
```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=smarthome
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres-init:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d smarthome"]
      interval: 10s
      timeout: 5s
      retries: 5

  temperature-api:
    build:
      context: ./temperature-api
      dockerfile: Dockerfile
    environment:
      - PORT=8081
      - GIN_MODE=release
    ports:
      - "8081:8081"
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:8081/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  app:
    build:
      context: ./smart_home
      dockerfile: Dockerfile
    depends_on:
      postgres:
        condition: service_healthy
      temperature-api:
        condition: service_started
    environment:
      - DATABASE_URL=postgres://postgres:postgres@postgres:5432/smarthome
      - TEMPERATURE_API_URL=http://temperature-api:8081
    ports:
      - "8080:8080"
```

**Ключевые возможности**:
- **Health checks** для всех сервисов
- **Service dependencies** с правильным порядком запуска
- **Network isolation** с пользовательской сетью
- **Volume persistence** для данных PostgreSQL
- **Environment configuration** через переменные окружения

### 5.5 Integration Architecture

#### Service Communication Flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Smart Home    │    │  Temperature API │    │   PostgreSQL    │
│   Application   │◄──►│    Service       │    │    Database     │
│   (Port 8080)   │    │   (Port 8081)    │    │   (Port 5432)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                        ┌─────────▼─────────┐
                        │  Docker Network   │
                        │ smarthome-network │
                        └───────────────────┘
```

#### Data Flow Scenarios
1. **Client Request** → Smart Home App (8080)
2. **Temperature Query** → Smart Home App → Temperature API (8081)
3. **Database Operations** → Smart Home App → PostgreSQL (5432)
4. **Response Chain** → PostgreSQL → Smart Home App → Client

### 5.6 Testing and Validation

#### Manual Testing Commands
```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка состояния сервисов
curl http://localhost:8081/health
curl http://localhost:8080/health

# Тестирование Temperature API
curl "http://localhost:8081/temperature?location=living_room"
curl "http://localhost:8081/temperature/TEMP001"

# Проверка подключения к базе данных
docker-compose exec postgres psql -U postgres -d smarthome -c "SELECT COUNT(*) FROM devices;"
```

#### Expected Results
**Temperature API Response**:
```json
{
  "value": 22.7,
  "unit": "°C",
  "timestamp": "2025-09-15T12:30:00Z",
  "location": "living_room",
  "status": "active",
  "sensor_id": "sensor-living_room-789",
  "sensor_type": "temperature",
  "description": "Temperature reading for living_room"
}
```

**Database Verification**:
- Таблицы созданы успешно
- Тестовые данные загружены
- Индексы и триггеры функционируют
- Foreign key constraints работают корректно

### 5.7 Postman Collection Integration

#### Testing Scenarios
Существующая коллекция [`apps/smarthome-api.postman_collection.json`](apps/smarthome-api.postman_collection.json) может быть использована для тестирования:

1. **Smart Home API endpoints** (порт 8080)
2. **Temperature API endpoints** (порт 8081)
3. **Database integration** через основное приложение
4. **End-to-end workflows** с реальными данными

#### Integration Test Flow
1. **Аутентификация** в основном приложении
2. **Получение списка устройств** из базы данных
3. **Запрос температуры** через Temperature API
4. **Сохранение данных** в PostgreSQL
5. **Проверка консистентности** данных

### 5.8 Deployment Instructions

#### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Доступные порты: 8080, 8081, 5432

#### Step-by-Step Deployment
```bash
# 1. Клонирование репозитория
git clone <repository-url>
cd microservices-iot-ecosystem/apps

# 2. Сборка и запуск сервисов
docker-compose up --build -d

# 3. Проверка статуса сервисов
docker-compose ps
docker-compose logs temperature-api
docker-compose logs postgres

# 4. Тестирование интеграции
curl "http://localhost:8081/temperature?location=bedroom"
curl http://localhost:8080/api/devices
```

### 5.9 Performance and Security

#### Resource Requirements
- **Temperature API**: ~50MB RAM, минимальная CPU нагрузка
- **PostgreSQL**: ~100MB RAM, умеренная I/O нагрузка
- **Smart Home App**: ~100MB RAM, умеренная CPU нагрузка
- **Общие требования**: ~250MB RAM минимум

#### Security Implementation
- **Container Security**: Non-root пользователь, минимальные образы
- **Network Security**: Изолированная Docker сеть
- **Database Security**: Подготовленные запросы, хеширование паролей
- **API Security**: CORS поддержка, валидация входных данных

### 5.10 Monitoring and Observability

#### Health Monitoring
- **Health endpoints** для проверки состояния сервисов
- **Docker health checks** для автоматического мониторинга
- **Structured logging** с Gin framework
- **Error handling** с детальными сообщениями

#### Future Enhancements
- **Prometheus metrics** для мониторинга производительности
- **Distributed tracing** с Jaeger
- **Centralized logging** с ELK stack
- **Alerting** при сбоях сервисов

## Заключение по Заданию 5

Задание 5 успешно демонстрирует практическую реализацию концепций микросервисной архитектуры, разработанных в предыдущих заданиях. Temperature API сервис представляет собой рабочий пример:

- **Микросервисной реализации** с современными практиками Go разработки
- **Docker контейнеризации** с безопасностью и оптимизацией
- **Service orchestration** с Docker Compose
- **Database integration** с PostgreSQL
- **API design** следуя REST принципам
- **Testing strategy** для проверки интеграции

Реализация служит фундаментом для полной экосистемы Smart Home IoT, показывая как архитектурные решения трансформируются в работающие программные системы.

**Созданные файлы**:
- [`apps/temperature-api/main.go`](apps/temperature-api/main.go) - основная реализация сервиса
- [`apps/temperature-api/go.mod`](apps/temperature-api/go.mod) - определение Go модуля
- [`apps/temperature-api/go.sum`](apps/temperature-api/go.sum) - контрольные суммы зависимостей
- [`apps/temperature-api/Dockerfile`](apps/temperature-api/Dockerfile) - определение контейнера
- [`apps/temperature-api/README.md`](apps/temperature-api/README.md) - документация сервиса
- [`apps/postgres-init/init.sql`](apps/postgres-init/init.sql) - скрипт инициализации БД
- [`apps/docker-compose.yml`](apps/docker-compose.yml) - обновленная оркестрация сервисов
- [`docs/task5-docker-implementation.md`](docs/task5-docker-implementation.md) - полная документация

---

**Файлы документации:**

**Задание 1:**
- `docs/task1-analysis.md` - детальный анализ текущей системы
- `docs/domain-analysis.md` - анализ доменов с применением DDD
- `docs/c4-context-diagram.puml` - диаграмма контекста системы
- `docs/task1-summary.md` - итоговый отчет и рекомендации

**Задание 2:**
- `docs/task2-microservices-decomposition.md` - детальная декомпозиция на микросервисы
- `docs/c4-container-diagram.puml` - диаграмма контейнеров C4
- `docs/c4-device-service-components.puml` - компоненты Device Service
- `docs/c4-automation-service-components.puml` - компоненты Automation Service
- `docs/c4-device-service-code-level.puml` - доменная модель Device Service
- `docs/device-command-sequence.puml` - последовательность выполнения команды
- `docs/task2-summary.md` - итоговый отчет по проектированию архитектуры

**Задание 3:**
- `docs/task3-er-diagram-analysis.md` - детальный анализ сущностей и атрибутов
- `docs/er-user-service.puml` - ER диаграмма User Service
- `docs/er-home-service.puml` - ER диаграмма Home Service
- `docs/er-device-service.puml` - ER диаграмма Device Service
- `docs/er-automation-service.puml` - ER диаграмма Automation Service
- `docs/er-notification-service.puml` - ER диаграмма Notification Service
- `docs/er-microservices-overview.puml` - обзорная ER диаграмма всех сервисов
- `docs/task3-summary.md` - итоговый отчет по проектированию баз данных

**Задание 4:**
- `docs/task4-api-design.md` - детальное описание дизайна API
- `docs/device-service-openapi.yaml` - OpenAPI спецификация Device Service
- `docs/smart-home-asyncapi.yaml` - AsyncAPI спецификация для событийной архитектуры
- `docs/task4-summary.md` - итоговый отчет по созданию и документированию API

**Задание 5:**
- `docs/task5-docker-implementation.md` - детальная документация по реализации Docker и Temperature API
- `apps/temperature-api/` - полная реализация микросервиса Temperature API
- `apps/postgres-init/init.sql` - скрипт инициализации базы данных PostgreSQL
- `apps/docker-compose.yml` - обновленная конфигурация оркестрации сервисов

**Общее:**
- `docs/README.md` - руководство по работе с документацией