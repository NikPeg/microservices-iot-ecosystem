package com.smarthome.deviceservice.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * DeviceCommand entity representing commands sent to IoT devices
 */
@Entity
@Table(name = "device_commands")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@EntityListeners(AuditingEntityListener.class)
public class DeviceCommand {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @NotNull(message = "Device ID is required")
    @Column(name = "device_id", nullable = false)
    private UUID deviceId;

    @NotBlank(message = "Command type is required")
    @Column(name = "command_type", nullable = false, length = 50)
    private String commandType;

    @Column(columnDefinition = "TEXT")
    private String parameters;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private CommandStatus status = CommandStatus.PENDING;

    @Column(name = "issued_by")
    private UUID issuedBy;

    @CreatedDate
    @Column(name = "sent_at", nullable = false, updatable = false)
    private LocalDateTime sentAt;

    @Column(name = "acknowledged_at")
    private LocalDateTime acknowledgedAt;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    @Column(name = "expires_at")
    private LocalDateTime expiresAt;

    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;

    @Column(name = "retry_count")
    @Builder.Default
    private Integer retryCount = 0;

    @Column(name = "max_retries")
    @Builder.Default
    private Integer maxRetries = 3;

    @Column(name = "timeout_seconds")
    @Builder.Default
    private Integer timeoutSeconds = 30;

    /**
     * Command status enumeration
     */
    public enum CommandStatus {
        PENDING,
        SENT,
        ACKNOWLEDGED,
        COMPLETED,
        FAILED,
        EXPIRED,
        CANCELLED
    }

    /**
     * Mark command as acknowledged
     */
    public void acknowledge() {
        this.status = CommandStatus.ACKNOWLEDGED;
        this.acknowledgedAt = LocalDateTime.now();
    }

    /**
     * Mark command as completed
     */
    public void complete() {
        this.status = CommandStatus.COMPLETED;
        this.completedAt = LocalDateTime.now();
    }

    /**
     * Mark command as failed with error message
     */
    public void fail(String errorMessage) {
        this.status = CommandStatus.FAILED;
        this.errorMessage = errorMessage;
        this.completedAt = LocalDateTime.now();
    }

    /**
     * Mark command as expired
     */
    public void expire() {
        this.status = CommandStatus.EXPIRED;
        this.completedAt = LocalDateTime.now();
    }

    /**
     * Increment retry count
     */
    public void incrementRetryCount() {
        this.retryCount++;
    }

    /**
     * Check if command has expired
     */
    public boolean isExpired() {
        return expiresAt != null && LocalDateTime.now().isAfter(expiresAt);
    }

    /**
     * Check if command can be retried
     */
    public boolean canRetry() {
        return retryCount < maxRetries && !isExpired();
    }

    /**
     * Check if command is in terminal state
     */
    public boolean isTerminal() {
        return status == CommandStatus.COMPLETED || 
               status == CommandStatus.FAILED || 
               status == CommandStatus.EXPIRED || 
               status == CommandStatus.CANCELLED;
    }

    /**
     * Set expiration time based on timeout
     */
    @PrePersist
    public void setExpirationTime() {
        if (expiresAt == null && timeoutSeconds != null) {
            expiresAt = LocalDateTime.now().plusSeconds(timeoutSeconds);
        }
    }
}