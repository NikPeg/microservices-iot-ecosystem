package com.smarthome.deviceservice.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.smarthome.deviceservice.model.Device;
import com.smarthome.deviceservice.model.DeviceCommand;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Service for publishing messages to Redis pub/sub for inter-service communication
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class MessageService {

    private final RedisTemplate<String, String> redisTemplate;
    private final ObjectMapper objectMapper;

    // Channel names for different event types
    private static final String DEVICE_EVENTS_CHANNEL = "device.events";
    private static final String COMMAND_EVENTS_CHANNEL = "device.commands";
    private static final String TELEMETRY_CHANNEL = "telemetry.data";

    /**
     * Publish device registered event
     */
    public void publishDeviceRegisteredEvent(Device device) {
        Map<String, Object> event = createBaseDeviceEvent("DeviceRegistered", device);
        publishEvent(DEVICE_EVENTS_CHANNEL, event);
        log.info("Published DeviceRegistered event for device: {}", device.getId());
    }

    /**
     * Publish device updated event
     */
    public void publishDeviceUpdatedEvent(Device device) {
        Map<String, Object> event = createBaseDeviceEvent("DeviceUpdated", device);
        publishEvent(DEVICE_EVENTS_CHANNEL, event);
        log.info("Published DeviceUpdated event for device: {}", device.getId());
    }

    /**
     * Publish device status changed event
     */
    public void publishDeviceStatusChangedEvent(Device device, Device.DeviceStatus oldStatus, Device.DeviceStatus newStatus) {
        Map<String, Object> event = createBaseDeviceEvent("DeviceStatusChanged", device);
        event.put("oldStatus", oldStatus.toString());
        event.put("newStatus", newStatus.toString());
        event.put("statusChangedAt", LocalDateTime.now().toString());

        publishEvent(DEVICE_EVENTS_CHANNEL, event);
        log.info("Published DeviceStatusChanged event for device: {} from {} to {}",
                device.getId(), oldStatus, newStatus);
    }

    /**
     * Publish device deleted event
     */
    public void publishDeviceDeletedEvent(Device device) {
        Map<String, Object> event = createBaseDeviceEvent("DeviceDeleted", device);
        publishEvent(DEVICE_EVENTS_CHANNEL, event);
        log.info("Published DeviceDeleted event for device: {}", device.getId());
    }

    /**
     * Publish device command created event
     */
    public void publishDeviceCommandCreatedEvent(DeviceCommand command) {
        Map<String, Object> event = createBaseCommandEvent("DeviceCommandCreated", command);
        publishEvent(COMMAND_EVENTS_CHANNEL, event);
        log.info("Published DeviceCommandCreated event for command: {}", command.getId());
    }

    /**
     * Publish device command acknowledged event
     */
    public void publishDeviceCommandAcknowledgedEvent(DeviceCommand command) {
        Map<String, Object> event = createBaseCommandEvent("DeviceCommandAcknowledged", command);
        publishEvent(COMMAND_EVENTS_CHANNEL, event);
        log.info("Published DeviceCommandAcknowledged event for command: {}", command.getId());
    }

    /**
     * Publish device command completed event
     */
    public void publishDeviceCommandCompletedEvent(DeviceCommand command) {
        Map<String, Object> event = createBaseCommandEvent("DeviceCommandCompleted", command);
        publishEvent(COMMAND_EVENTS_CHANNEL, event);
        log.info("Published DeviceCommandCompleted event for command: {}", command.getId());
    }

    /**
     * Publish device command failed event
     */
    public void publishDeviceCommandFailedEvent(DeviceCommand command) {
        Map<String, Object> event = createBaseCommandEvent("DeviceCommandFailed", command);
        event.put("errorMessage", command.getErrorMessage());
        publishEvent(COMMAND_EVENTS_CHANNEL, event);
        log.info("Published DeviceCommandFailed event for command: {}", command.getId());
    }

    /**
     * Publish device command expired event
     */
    public void publishDeviceCommandExpiredEvent(DeviceCommand command) {
        Map<String, Object> event = createBaseCommandEvent("DeviceCommandExpired", command);
        publishEvent(COMMAND_EVENTS_CHANNEL, event);
        log.info("Published DeviceCommandExpired event for command: {}", command.getId());
    }

    /**
     * Publish telemetry data event (for integration with telemetry service)
     */
    public void publishTelemetryDataEvent(UUID deviceId, String sensorType, Double value, String unit) {
        Map<String, Object> event = new HashMap<>();
        event.put("eventId", UUID.randomUUID().toString());
        event.put("eventType", "TelemetryDataReceived");
        event.put("deviceId", deviceId.toString());
        event.put("sensorType", sensorType);
        event.put("value", value);
        event.put("unit", unit);
        event.put("timestamp", LocalDateTime.now().toString());
        event.put("source", "device-service");

        publishEvent(TELEMETRY_CHANNEL, event);
        log.info("Published TelemetryDataReceived event for device: {}", deviceId);
    }

    /**
     * Create base device event structure
     */
    private Map<String, Object> createBaseDeviceEvent(String eventType, Device device) {
        Map<String, Object> event = new HashMap<>();
        event.put("eventId", UUID.randomUUID().toString());
        event.put("eventType", eventType);
        event.put("deviceId", device.getId().toString());
        event.put("deviceName", device.getName());
        event.put("deviceType", device.getDeviceType());
        event.put("serialNumber", device.getSerialNumber());
        event.put("status", device.getStatus().toString());
        event.put("homeId", device.getHomeId().toString());
        event.put("roomId", device.getRoomId() != null ? device.getRoomId().toString() : null);
        event.put("userId", device.getUserId().toString());
        event.put("timestamp", LocalDateTime.now().toString());
        event.put("source", "device-service");

        return event;
    }

    /**
     * Create base command event structure
     */
    private Map<String, Object> createBaseCommandEvent(String eventType, DeviceCommand command) {
        Map<String, Object> event = new HashMap<>();
        event.put("eventId", UUID.randomUUID().toString());
        event.put("eventType", eventType);
        event.put("commandId", command.getId().toString());
        event.put("deviceId", command.getDeviceId().toString());
        event.put("commandType", command.getCommandType());
        event.put("parameters", command.getParameters());
        event.put("status", command.getStatus().toString());
        event.put("issuedBy", command.getIssuedBy() != null ? command.getIssuedBy().toString() : null);
        event.put("sentAt", command.getSentAt() != null ? command.getSentAt().toString() : null);
        event.put("acknowledgedAt", command.getAcknowledgedAt() != null ? command.getAcknowledgedAt().toString() : null);
        event.put("completedAt", command.getCompletedAt() != null ? command.getCompletedAt().toString() : null);
        event.put("timestamp", LocalDateTime.now().toString());
        event.put("source", "device-service");

        return event;
    }

    /**
     * Publish event to Redis channel
     */
    private void publishEvent(String channel, Map<String, Object> event) {
        try {
            String eventJson = objectMapper.writeValueAsString(event);
            redisTemplate.convertAndSend(channel, eventJson);
            log.debug("Published event to channel {}: {}", channel, eventJson);
        } catch (JsonProcessingException e) {
            log.error("Failed to serialize event for channel {}: {}", channel, e.getMessage(), e);
        } catch (Exception e) {
            log.error("Failed to publish event to channel {}: {}", channel, e.getMessage(), e);
        }
    }

    /**
     * Publish custom event
     */
    public void publishCustomEvent(String channel, String eventType, Map<String, Object> data) {
        Map<String, Object> event = new HashMap<>();
        event.put("eventId", UUID.randomUUID().toString());
        event.put("eventType", eventType);
        event.put("timestamp", LocalDateTime.now().toString());
        event.put("source", "device-service");
        event.putAll(data);

        publishEvent(channel, event);
        log.info("Published custom event {} to channel: {}", eventType, channel);
    }

    /**
     * Publish device heartbeat event
     */
    public void publishDeviceHeartbeatEvent(Device device) {
        Map<String, Object> event = createBaseDeviceEvent("DeviceHeartbeat", device);
        event.put("lastSeen", device.getLastSeen() != null ? device.getLastSeen().toString() : null);
        event.put("batteryLevel", device.getBatteryLevel());

        publishEvent(DEVICE_EVENTS_CHANNEL, event);
        log.debug("Published DeviceHeartbeat event for device: {}", device.getId());
    }

    /**
     * Publish device low battery alert
     */
    public void publishDeviceLowBatteryAlert(Device device) {
        Map<String, Object> event = createBaseDeviceEvent("DeviceLowBatteryAlert", device);
        event.put("batteryLevel", device.getBatteryLevel());
        event.put("alertLevel", "WARNING");

        publishEvent(DEVICE_EVENTS_CHANNEL, event);
        log.warn("Published DeviceLowBatteryAlert event for device: {} (battery: {}%)",
                device.getId(), device.getBatteryLevel());
    }

    /**
     * Publish device offline alert
     */
    public void publishDeviceOfflineAlert(Device device, LocalDateTime lastSeen) {
        Map<String, Object> event = createBaseDeviceEvent("DeviceOfflineAlert", device);
        event.put("lastSeen", lastSeen != null ? lastSeen.toString() : null);
        event.put("alertLevel", "ERROR");

        publishEvent(DEVICE_EVENTS_CHANNEL, event);
        log.warn("Published DeviceOfflineAlert event for device: {} (last seen: {})",
                device.getId(), lastSeen);
    }
}
