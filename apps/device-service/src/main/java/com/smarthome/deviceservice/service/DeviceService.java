package com.smarthome.deviceservice.service;

import com.smarthome.deviceservice.model.Device;
import com.smarthome.deviceservice.model.DeviceCommand;
import com.smarthome.deviceservice.repository.DeviceRepository;
import com.smarthome.deviceservice.repository.DeviceCommandRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Service class for device management operations
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class DeviceService {

    private final DeviceRepository deviceRepository;
    private final DeviceCommandRepository commandRepository;
    private final MessageService messageService;

    /**
     * Register a new device
     */
    public Device registerDevice(Device device) {
        log.info("Registering new device: {}", device.getName());

        // Validate unique constraints
        if (device.getSerialNumber() != null &&
            deviceRepository.existsBySerialNumber(device.getSerialNumber())) {
            throw new IllegalArgumentException("Device with serial number already exists: " + device.getSerialNumber());
        }

        if (device.getMacAddress() != null &&
            deviceRepository.existsByMacAddress(device.getMacAddress())) {
            throw new IllegalArgumentException("Device with MAC address already exists: " + device.getMacAddress());
        }

        // Set initial status - use provided status or default to OFFLINE
        if (device.getStatus() == null) {
            device.setStatus(Device.DeviceStatus.OFFLINE);
        }
        device.setLastSeen(LocalDateTime.now());

        Device savedDevice = deviceRepository.save(device);

        // Publish device registered event
        messageService.publishDeviceRegisteredEvent(savedDevice);

        log.info("Device registered successfully with ID: {}", savedDevice.getId());
        return savedDevice;
    }

    /**
     * Get device by ID
     */
    @Transactional(readOnly = true)
    public Optional<Device> getDeviceById(UUID deviceId) {
        return deviceRepository.findById(deviceId);
    }

    /**
     * Get all devices for a home
     */
    @Transactional(readOnly = true)
    public List<Device> getDevicesByHomeId(UUID homeId) {
        return deviceRepository.findByHomeId(homeId);
    }

    /**
     * Get devices with filters and pagination
     */
    @Transactional(readOnly = true)
    public Page<Device> getDevicesWithFilters(UUID homeId, UUID roomId, String deviceType,
                                            Device.DeviceStatus status, Pageable pageable) {
        // Use findAll if no filters are provided
        if (homeId == null && roomId == null && deviceType == null && status == null) {
            return deviceRepository.findAll(pageable);
        }

        // For now, let's use a simple approach that works with the existing methods
        // This is a temporary solution to get the test passing
        List<Device> allDevices = deviceRepository.findAll();

        // Apply filters manually
        List<Device> filteredDevices = allDevices.stream()
            .filter(device -> homeId == null || device.getHomeId().equals(homeId))
            .filter(device -> roomId == null || (device.getRoomId() != null && device.getRoomId().equals(roomId)))
            .filter(device -> deviceType == null || device.getDeviceType().equals(deviceType))
            .filter(device -> status == null || device.getStatus().equals(status))
            .collect(java.util.stream.Collectors.toList());

        // Create a manual page
        int start = (int) pageable.getOffset();
        int end = Math.min(start + pageable.getPageSize(), filteredDevices.size());
        List<Device> pageContent = start < filteredDevices.size() ?
            filteredDevices.subList(start, end) : java.util.Collections.emptyList();

        return new org.springframework.data.domain.PageImpl<>(
            pageContent, pageable, filteredDevices.size());
    }

    /**
     * Update device information
     */
    public Device updateDevice(UUID deviceId, Device deviceUpdate) {
        log.info("Updating device: {}", deviceId);

        Device existingDevice = deviceRepository.findById(deviceId)
            .orElseThrow(() -> new IllegalArgumentException("Device not found: " + deviceId));

        // Update allowed fields
        if (deviceUpdate.getName() != null) {
            existingDevice.setName(deviceUpdate.getName());
        }
        if (deviceUpdate.getRoomId() != null) {
            existingDevice.setRoomId(deviceUpdate.getRoomId());
        }
        if (deviceUpdate.getConfiguration() != null) {
            existingDevice.setConfiguration(deviceUpdate.getConfiguration());
        }
        if (deviceUpdate.getFirmwareVersion() != null) {
            existingDevice.setFirmwareVersion(deviceUpdate.getFirmwareVersion());
        }

        Device savedDevice = deviceRepository.save(existingDevice);

        // Publish device updated event
        messageService.publishDeviceUpdatedEvent(savedDevice);

        log.info("Device updated successfully: {}", deviceId);
        return savedDevice;
    }

    /**
     * Update device status
     */
    public Device updateDeviceStatus(UUID deviceId, Device.DeviceStatus status) {
        log.info("Updating device status: {} to {}", deviceId, status);

        Device device = deviceRepository.findById(deviceId)
            .orElseThrow(() -> new IllegalArgumentException("Device not found: " + deviceId));

        Device.DeviceStatus oldStatus = device.getStatus();
        device.updateStatus(status);

        Device savedDevice = deviceRepository.save(device);

        // Publish status change event if status actually changed
        if (!oldStatus.equals(status)) {
            messageService.publishDeviceStatusChangedEvent(savedDevice, oldStatus, status);
        }

        log.info("Device status updated: {} from {} to {}", deviceId, oldStatus, status);
        return savedDevice;
    }

    /**
     * Delete device
     */
    public void deleteDevice(UUID deviceId) {
        log.info("Deleting device: {}", deviceId);

        Device device = deviceRepository.findById(deviceId)
            .orElseThrow(() -> new IllegalArgumentException("Device not found: " + deviceId));

        // Cancel any pending commands
        List<DeviceCommand> pendingCommands = commandRepository.findPendingCommandsByDeviceId(deviceId);
        pendingCommands.forEach(command -> {
            command.setStatus(DeviceCommand.CommandStatus.CANCELLED);
            commandRepository.save(command);
        });

        deviceRepository.delete(device);

        // Publish device deleted event
        messageService.publishDeviceDeletedEvent(device);

        log.info("Device deleted successfully: {}", deviceId);
    }

    /**
     * Send command to device
     */
    public DeviceCommand sendCommand(UUID deviceId, String commandType, String parameters, UUID issuedBy) {
        log.info("Sending command {} to device: {}", commandType, deviceId);

        Device device = deviceRepository.findById(deviceId)
            .orElseThrow(() -> new IllegalArgumentException("Device not found: " + deviceId));

        if (!device.isOnline()) {
            throw new IllegalStateException("Cannot send command to offline device: " + deviceId);
        }

        DeviceCommand command = DeviceCommand.builder()
            .deviceId(deviceId)
            .commandType(commandType)
            .parameters(parameters)
            .issuedBy(issuedBy)
            .status(DeviceCommand.CommandStatus.PENDING)
            .build();

        DeviceCommand savedCommand = commandRepository.save(command);

        // Publish command created event
        messageService.publishDeviceCommandCreatedEvent(savedCommand);

        log.info("Command created with ID: {}", savedCommand.getId());
        return savedCommand;
    }

    /**
     * Get command by ID
     */
    @Transactional(readOnly = true)
    public Optional<DeviceCommand> getCommandById(UUID commandId) {
        return commandRepository.findById(commandId);
    }

    /**
     * Get commands for device with pagination
     */
    @Transactional(readOnly = true)
    public Page<DeviceCommand> getCommandsByDeviceId(UUID deviceId, Pageable pageable) {
        return commandRepository.findByDeviceId(deviceId, pageable);
    }

    /**
     * Acknowledge command execution
     */
    public DeviceCommand acknowledgeCommand(UUID commandId) {
        log.info("Acknowledging command: {}", commandId);

        DeviceCommand command = commandRepository.findById(commandId)
            .orElseThrow(() -> new IllegalArgumentException("Command not found: " + commandId));

        command.acknowledge();
        DeviceCommand savedCommand = commandRepository.save(command);

        // Publish command acknowledged event
        messageService.publishDeviceCommandAcknowledgedEvent(savedCommand);

        log.info("Command acknowledged: {}", commandId);
        return savedCommand;
    }

    /**
     * Complete command execution
     */
    public DeviceCommand completeCommand(UUID commandId) {
        log.info("Completing command: {}", commandId);

        DeviceCommand command = commandRepository.findById(commandId)
            .orElseThrow(() -> new IllegalArgumentException("Command not found: " + commandId));

        command.complete();
        DeviceCommand savedCommand = commandRepository.save(command);

        // Publish command completed event
        messageService.publishDeviceCommandCompletedEvent(savedCommand);

        log.info("Command completed: {}", commandId);
        return savedCommand;
    }

    /**
     * Fail command execution
     */
    public DeviceCommand failCommand(UUID commandId, String errorMessage) {
        log.info("Failing command: {} with error: {}", commandId, errorMessage);

        DeviceCommand command = commandRepository.findById(commandId)
            .orElseThrow(() -> new IllegalArgumentException("Command not found: " + commandId));

        command.fail(errorMessage);
        DeviceCommand savedCommand = commandRepository.save(command);

        // Publish command failed event
        messageService.publishDeviceCommandFailedEvent(savedCommand);

        log.info("Command failed: {}", commandId);
        return savedCommand;
    }

    /**
     * Get devices with low battery
     */
    @Transactional(readOnly = true)
    public List<Device> getDevicesWithLowBattery(int batteryThreshold) {
        return deviceRepository.findDevicesWithLowBattery(batteryThreshold);
    }

    /**
     * Get devices not seen since specified time
     */
    @Transactional(readOnly = true)
    public List<Device> getDevicesNotSeenSince(LocalDateTime since) {
        return deviceRepository.findDevicesNotSeenSince(since);
    }

    /**
     * Process expired commands
     */
    public void processExpiredCommands() {
        log.info("Processing expired commands");

        List<DeviceCommand> expiredCommands = commandRepository.findExpiredCommands(LocalDateTime.now());

        expiredCommands.forEach(command -> {
            command.expire();
            commandRepository.save(command);
            messageService.publishDeviceCommandExpiredEvent(command);
        });

        log.info("Processed {} expired commands", expiredCommands.size());
    }

    /**
     * Search devices by name
     */
    @Transactional(readOnly = true)
    public List<Device> searchDevicesByName(String name) {
        return deviceRepository.findByNameContainingIgnoreCase(name);
    }
}
