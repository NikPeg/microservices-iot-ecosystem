package com.smarthome.deviceservice.controller;

import com.smarthome.deviceservice.model.Device;
import com.smarthome.deviceservice.model.DeviceCommand;
import com.smarthome.deviceservice.service.DeviceService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * REST Controller for device management operations
 */
@RestController
@RequestMapping("/api/v1/devices")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Device Management", description = "APIs for managing IoT devices")
public class DeviceController {

    private final DeviceService deviceService;

    @Operation(summary = "Register a new device", description = "Register a new IoT device in the system")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "201", description = "Device registered successfully"),
        @ApiResponse(responseCode = "400", description = "Invalid device data"),
        @ApiResponse(responseCode = "409", description = "Device already exists")
    })
    @PostMapping
    public ResponseEntity<Device> registerDevice(@Valid @RequestBody Device device) {
        log.info("Received request to register device: {}", device.getName());
        Device registeredDevice = deviceService.registerDevice(device);
        return ResponseEntity.status(HttpStatus.CREATED).body(registeredDevice);
    }

    @Operation(summary = "Get device by ID", description = "Retrieve device information by device ID")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Device found"),
        @ApiResponse(responseCode = "404", description = "Device not found")
    })
    @GetMapping("/{deviceId}")
    public ResponseEntity<Device> getDevice(
            @Parameter(description = "Device ID") @PathVariable UUID deviceId) {
        log.info("Received request to get device: {}", deviceId);
        return deviceService.getDeviceById(deviceId)
                .map(device -> ResponseEntity.ok(device))
                .orElse(ResponseEntity.notFound().build());
    }

    @Operation(summary = "Get devices with filters", description = "Retrieve devices with optional filtering and pagination")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Devices retrieved successfully")
    })
    @GetMapping
    public ResponseEntity<Page<Device>> getDevices(
            @Parameter(description = "Home ID filter") @RequestParam(required = false) UUID homeId,
            @Parameter(description = "Room ID filter") @RequestParam(required = false) UUID roomId,
            @Parameter(description = "Device type filter") @RequestParam(required = false) String deviceType,
            @Parameter(description = "Device status filter") @RequestParam(required = false) Device.DeviceStatus status,
            @PageableDefault(size = 20) Pageable pageable) {
        
        log.info("Received request to get devices with filters - homeId: {}, roomId: {}, deviceType: {}, status: {}", 
                homeId, roomId, deviceType, status);
        
        Page<Device> devices = deviceService.getDevicesWithFilters(homeId, roomId, deviceType, status, pageable);
        return ResponseEntity.ok(devices);
    }

    @Operation(summary = "Get devices by home ID", description = "Retrieve all devices for a specific home")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Devices retrieved successfully")
    })
    @GetMapping("/home/{homeId}")
    public ResponseEntity<List<Device>> getDevicesByHome(
            @Parameter(description = "Home ID") @PathVariable UUID homeId) {
        log.info("Received request to get devices for home: {}", homeId);
        List<Device> devices = deviceService.getDevicesByHomeId(homeId);
        return ResponseEntity.ok(devices);
    }

    @Operation(summary = "Update device", description = "Update device information")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Device updated successfully"),
        @ApiResponse(responseCode = "404", description = "Device not found"),
        @ApiResponse(responseCode = "400", description = "Invalid device data")
    })
    @PutMapping("/{deviceId}")
    public ResponseEntity<Device> updateDevice(
            @Parameter(description = "Device ID") @PathVariable UUID deviceId,
            @Valid @RequestBody Device deviceUpdate) {
        log.info("Received request to update device: {}", deviceId);
        Device updatedDevice = deviceService.updateDevice(deviceId, deviceUpdate);
        return ResponseEntity.ok(updatedDevice);
    }

    @Operation(summary = "Update device status", description = "Update the status of a device")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Device status updated successfully"),
        @ApiResponse(responseCode = "404", description = "Device not found")
    })
    @PatchMapping("/{deviceId}/status")
    public ResponseEntity<Device> updateDeviceStatus(
            @Parameter(description = "Device ID") @PathVariable UUID deviceId,
            @Parameter(description = "New device status") @RequestParam Device.DeviceStatus status) {
        log.info("Received request to update device status: {} to {}", deviceId, status);
        Device updatedDevice = deviceService.updateDeviceStatus(deviceId, status);
        return ResponseEntity.ok(updatedDevice);
    }

    @Operation(summary = "Delete device", description = "Remove a device from the system")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "204", description = "Device deleted successfully"),
        @ApiResponse(responseCode = "404", description = "Device not found")
    })
    @DeleteMapping("/{deviceId}")
    public ResponseEntity<Void> deleteDevice(
            @Parameter(description = "Device ID") @PathVariable UUID deviceId) {
        log.info("Received request to delete device: {}", deviceId);
        deviceService.deleteDevice(deviceId);
        return ResponseEntity.noContent().build();
    }

    @Operation(summary = "Send command to device", description = "Send a command to a specific device")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "202", description = "Command sent successfully"),
        @ApiResponse(responseCode = "404", description = "Device not found"),
        @ApiResponse(responseCode = "400", description = "Invalid command or device offline")
    })
    @PostMapping("/{deviceId}/commands")
    public ResponseEntity<DeviceCommand> sendCommand(
            @Parameter(description = "Device ID") @PathVariable UUID deviceId,
            @RequestBody Map<String, Object> commandRequest) {
        
        String commandType = (String) commandRequest.get("commandType");
        String parameters = commandRequest.get("parameters") != null ? 
                commandRequest.get("parameters").toString() : null;
        UUID issuedBy = commandRequest.get("issuedBy") != null ? 
                UUID.fromString(commandRequest.get("issuedBy").toString()) : null;
        
        log.info("Received request to send command {} to device: {}", commandType, deviceId);
        
        DeviceCommand command = deviceService.sendCommand(deviceId, commandType, parameters, issuedBy);
        return ResponseEntity.status(HttpStatus.ACCEPTED).body(command);
    }

    @Operation(summary = "Get device commands", description = "Retrieve commands for a specific device")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Commands retrieved successfully")
    })
    @GetMapping("/{deviceId}/commands")
    public ResponseEntity<Page<DeviceCommand>> getDeviceCommands(
            @Parameter(description = "Device ID") @PathVariable UUID deviceId,
            @PageableDefault(size = 20) Pageable pageable) {
        log.info("Received request to get commands for device: {}", deviceId);
        Page<DeviceCommand> commands = deviceService.getCommandsByDeviceId(deviceId, pageable);
        return ResponseEntity.ok(commands);
    }

    @Operation(summary = "Get command by ID", description = "Retrieve a specific command by its ID")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Command found"),
        @ApiResponse(responseCode = "404", description = "Command not found")
    })
    @GetMapping("/{deviceId}/commands/{commandId}")
    public ResponseEntity<DeviceCommand> getCommand(
            @Parameter(description = "Device ID") @PathVariable UUID deviceId,
            @Parameter(description = "Command ID") @PathVariable UUID commandId) {
        log.info("Received request to get command: {} for device: {}", commandId, deviceId);
        return deviceService.getCommandById(commandId)
                .map(command -> ResponseEntity.ok(command))
                .orElse(ResponseEntity.notFound().build());
    }

    @Operation(summary = "Acknowledge command", description = "Mark a command as acknowledged by the device")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Command acknowledged successfully"),
        @ApiResponse(responseCode = "404", description = "Command not found")
    })
    @PatchMapping("/{deviceId}/commands/{commandId}/acknowledge")
    public ResponseEntity<DeviceCommand> acknowledgeCommand(
            @Parameter(description = "Device ID") @PathVariable UUID deviceId,
            @Parameter(description = "Command ID") @PathVariable UUID commandId) {
        log.info("Received request to acknowledge command: {} for device: {}", commandId, deviceId);
        DeviceCommand command = deviceService.acknowledgeCommand(commandId);
        return ResponseEntity.ok(command);
    }

    @Operation(summary = "Complete command", description = "Mark a command as completed")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Command completed successfully"),
        @ApiResponse(responseCode = "404", description = "Command not found")
    })
    @PatchMapping("/{deviceId}/commands/{commandId}/complete")
    public ResponseEntity<DeviceCommand> completeCommand(
            @Parameter(description = "Device ID") @PathVariable UUID deviceId,
            @Parameter(description = "Command ID") @PathVariable UUID commandId) {
        log.info("Received request to complete command: {} for device: {}", commandId, deviceId);
        DeviceCommand command = deviceService.completeCommand(commandId);
        return ResponseEntity.ok(command);
    }

    @Operation(summary = "Fail command", description = "Mark a command as failed with error message")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Command marked as failed"),
        @ApiResponse(responseCode = "404", description = "Command not found")
    })
    @PatchMapping("/{deviceId}/commands/{commandId}/fail")
    public ResponseEntity<DeviceCommand> failCommand(
            @Parameter(description = "Device ID") @PathVariable UUID deviceId,
            @Parameter(description = "Command ID") @PathVariable UUID commandId,
            @RequestBody Map<String, String> failureRequest) {
        
        String errorMessage = failureRequest.get("errorMessage");
        log.info("Received request to fail command: {} for device: {} with error: {}", 
                commandId, deviceId, errorMessage);
        
        DeviceCommand command = deviceService.failCommand(commandId, errorMessage);
        return ResponseEntity.ok(command);
    }

    @Operation(summary = "Search devices", description = "Search devices by name")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Search completed successfully")
    })
    @GetMapping("/search")
    public ResponseEntity<List<Device>> searchDevices(
            @Parameter(description = "Search query") @RequestParam String q) {
        log.info("Received request to search devices with query: {}", q);
        List<Device> devices = deviceService.searchDevicesByName(q);
        return ResponseEntity.ok(devices);
    }

    @Operation(summary = "Get devices with low battery", description = "Retrieve devices with battery level below threshold")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Low battery devices retrieved successfully")
    })
    @GetMapping("/low-battery")
    public ResponseEntity<List<Device>> getDevicesWithLowBattery(
            @Parameter(description = "Battery threshold percentage") @RequestParam(defaultValue = "20") int threshold) {
        log.info("Received request to get devices with low battery (threshold: {}%)", threshold);
        List<Device> devices = deviceService.getDevicesWithLowBattery(threshold);
        return ResponseEntity.ok(devices);
    }

    @Operation(summary = "Get offline devices", description = "Retrieve devices that haven't been seen recently")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Offline devices retrieved successfully")
    })
    @GetMapping("/offline")
    public ResponseEntity<List<Device>> getOfflineDevices(
            @Parameter(description = "Hours since last seen") @RequestParam(defaultValue = "24") int hours) {
        log.info("Received request to get offline devices (not seen for {} hours)", hours);
        LocalDateTime since = LocalDateTime.now().minusHours(hours);
        List<Device> devices = deviceService.getDevicesNotSeenSince(since);
        return ResponseEntity.ok(devices);
    }
}