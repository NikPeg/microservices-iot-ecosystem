package com.smarthome.deviceservice.repository;

import com.smarthome.deviceservice.model.DeviceCommand;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

/**
 * Repository interface for DeviceCommand entity operations
 */
@Repository
public interface DeviceCommandRepository extends JpaRepository<DeviceCommand, UUID> {

    /**
     * Find all commands for a specific device
     */
    List<DeviceCommand> findByDeviceId(UUID deviceId);

    /**
     * Find commands by device ID with pagination
     */
    Page<DeviceCommand> findByDeviceId(UUID deviceId, Pageable pageable);

    /**
     * Find commands by status
     */
    List<DeviceCommand> findByStatus(DeviceCommand.CommandStatus status);

    /**
     * Find commands by device ID and status
     */
    List<DeviceCommand> findByDeviceIdAndStatus(UUID deviceId, DeviceCommand.CommandStatus status);

    /**
     * Find commands issued by specific user
     */
    List<DeviceCommand> findByIssuedBy(UUID userId);

    /**
     * Find pending commands for a device
     */
    @Query("SELECT c FROM DeviceCommand c WHERE c.deviceId = :deviceId AND c.status IN ('PENDING', 'SENT')")
    List<DeviceCommand> findPendingCommandsByDeviceId(@Param("deviceId") UUID deviceId);

    /**
     * Find expired commands that haven't been processed
     */
    @Query("SELECT c FROM DeviceCommand c WHERE c.expiresAt < :now AND c.status NOT IN ('COMPLETED', 'FAILED', 'EXPIRED', 'CANCELLED')")
    List<DeviceCommand> findExpiredCommands(@Param("now") LocalDateTime now);

    /**
     * Find commands that can be retried
     */
    @Query("SELECT c FROM DeviceCommand c WHERE c.status = 'FAILED' AND c.retryCount < c.maxRetries AND c.expiresAt > :now")
    List<DeviceCommand> findRetryableCommands(@Param("now") LocalDateTime now);

    /**
     * Find recent commands for a device (within last N hours)
     */
    @Query("SELECT c FROM DeviceCommand c WHERE c.deviceId = :deviceId AND c.sentAt > :since ORDER BY c.sentAt DESC")
    List<DeviceCommand> findRecentCommandsByDeviceId(@Param("deviceId") UUID deviceId, @Param("since") LocalDateTime since);

    /**
     * Count commands by status
     */
    long countByStatus(DeviceCommand.CommandStatus status);

    /**
     * Count commands by device ID and status
     */
    long countByDeviceIdAndStatus(UUID deviceId, DeviceCommand.CommandStatus status);

    /**
     * Find commands by command type
     */
    List<DeviceCommand> findByCommandType(String commandType);

    /**
     * Find commands by device ID and command type
     */
    List<DeviceCommand> findByDeviceIdAndCommandType(UUID deviceId, String commandType);

    /**
     * Find commands sent within time range
     */
    @Query("SELECT c FROM DeviceCommand c WHERE c.sentAt BETWEEN :startTime AND :endTime")
    List<DeviceCommand> findCommandsBetween(@Param("startTime") LocalDateTime startTime, 
                                          @Param("endTime") LocalDateTime endTime);

    /**
     * Find latest command for each device
     */
    @Query("SELECT c FROM DeviceCommand c WHERE c.sentAt = (SELECT MAX(c2.sentAt) FROM DeviceCommand c2 WHERE c2.deviceId = c.deviceId)")
    List<DeviceCommand> findLatestCommandForEachDevice();

    /**
     * Find commands with filters and pagination
     */
    @Query("SELECT c FROM DeviceCommand c WHERE " +
           "(:deviceId IS NULL OR c.deviceId = :deviceId) AND " +
           "(:status IS NULL OR c.status = :status) AND " +
           "(:commandType IS NULL OR c.commandType = :commandType) AND " +
           "(:issuedBy IS NULL OR c.issuedBy = :issuedBy)")
    Page<DeviceCommand> findCommandsWithFilters(
            @Param("deviceId") UUID deviceId,
            @Param("status") DeviceCommand.CommandStatus status,
            @Param("commandType") String commandType,
            @Param("issuedBy") UUID issuedBy,
            Pageable pageable
    );

    /**
     * Delete old completed commands (cleanup)
     */
    @Query("DELETE FROM DeviceCommand c WHERE c.status IN ('COMPLETED', 'FAILED', 'EXPIRED') AND c.completedAt < :cutoffDate")
    void deleteOldCompletedCommands(@Param("cutoffDate") LocalDateTime cutoffDate);

    /**
     * Find commands that need acknowledgment timeout check
     */
    @Query("SELECT c FROM DeviceCommand c WHERE c.status = 'SENT' AND c.sentAt < :timeoutThreshold")
    List<DeviceCommand> findCommandsNeedingTimeoutCheck(@Param("timeoutThreshold") LocalDateTime timeoutThreshold);

    /**
     * Get command statistics for a device
     */
    @Query("SELECT c.status, COUNT(c) FROM DeviceCommand c WHERE c.deviceId = :deviceId GROUP BY c.status")
    List<Object[]> getCommandStatisticsByDeviceId(@Param("deviceId") UUID deviceId);

    /**
     * Find commands by multiple device IDs
     */
    List<DeviceCommand> findByDeviceIdIn(List<UUID> deviceIds);

    /**
     * Check if device has pending commands
     */
    @Query("SELECT COUNT(c) > 0 FROM DeviceCommand c WHERE c.deviceId = :deviceId AND c.status IN ('PENDING', 'SENT')")
    boolean hasPendingCommands(@Param("deviceId") UUID deviceId);
}