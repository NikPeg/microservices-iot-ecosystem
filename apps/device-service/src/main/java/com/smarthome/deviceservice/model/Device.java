package com.smarthome.deviceservice.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Device entity representing an IoT device in the smart home system
 */
@Entity
@Table(name = "devices")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@EntityListeners(AuditingEntityListener.class)
public class Device {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @NotBlank(message = "Device name is required")
    @Column(nullable = false, length = 100)
    private String name;

    @NotBlank(message = "Device type is required")
    @Column(name = "device_type", nullable = false, length = 50)
    private String deviceType;

    @Column(name = "serial_number", unique = true, length = 100)
    private String serialNumber;

    @Column(name = "mac_address", length = 17)
    private String macAddress;

    @Column(name = "ip_address", length = 45)
    private String ipAddress;

    @Column(name = "firmware_version", length = 50)
    private String firmwareVersion;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private DeviceStatus status = DeviceStatus.OFFLINE;

    @Column(name = "last_seen")
    private LocalDateTime lastSeen;

    @Column(name = "battery_level")
    private Integer batteryLevel;

    // External references to other services
    @NotNull(message = "Home ID is required")
    @Column(name = "home_id", nullable = false)
    private UUID homeId;

    @Column(name = "room_id")
    private UUID roomId;

    @Column(name = "user_id", nullable = false)
    private UUID userId;

    // JSON configuration stored as text
    @Column(columnDefinition = "TEXT")
    private String configuration;

    @Column(columnDefinition = "TEXT")
    private String capabilities;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    /**
     * Device status enumeration
     */
    public enum DeviceStatus {
        ONLINE,
        OFFLINE,
        ERROR,
        MAINTENANCE,
        UNKNOWN
    }

    /**
     * Update device status and last seen timestamp
     */
    public void updateStatus(DeviceStatus newStatus) {
        this.status = newStatus;
        this.lastSeen = LocalDateTime.now();
    }

    /**
     * Check if device is online
     */
    public boolean isOnline() {
        return DeviceStatus.ONLINE.equals(this.status);
    }

    /**
     * Check if device has low battery (below 20%)
     */
    public boolean hasLowBattery() {
        return batteryLevel != null && batteryLevel < 20;
    }
}