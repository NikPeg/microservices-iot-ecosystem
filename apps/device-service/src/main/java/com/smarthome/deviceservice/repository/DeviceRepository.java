package com.smarthome.deviceservice.repository;

import com.smarthome.deviceservice.model.Device;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository interface for Device entity operations
 */
@Repository
public interface DeviceRepository extends JpaRepository<Device, UUID> {

    /**
     * Find device by serial number
     */
    Optional<Device> findBySerialNumber(String serialNumber);

    /**
     * Find all devices by home ID
     */
    List<Device> findByHomeId(UUID homeId);

    /**
     * Find all devices by room ID
     */
    List<Device> findByRoomId(UUID roomId);

    /**
     * Find all devices by user ID
     */
    List<Device> findByUserId(UUID userId);

    /**
     * Find devices by status
     */
    List<Device> findByStatus(Device.DeviceStatus status);

    /**
     * Find devices by device type
     */
    List<Device> findByDeviceType(String deviceType);

    /**
     * Find devices by home ID and status
     */
    List<Device> findByHomeIdAndStatus(UUID homeId, Device.DeviceStatus status);

    /**
     * Find devices by room ID and device type
     */
    List<Device> findByRoomIdAndDeviceType(UUID roomId, String deviceType);

    /**
     * Find devices with low battery (below specified level)
     */
    @Query("SELECT d FROM Device d WHERE d.batteryLevel IS NOT NULL AND d.batteryLevel < :batteryLevel")
    List<Device> findDevicesWithLowBattery(@Param("batteryLevel") Integer batteryLevel);

    /**
     * Find devices that haven't been seen since specified time
     */
    @Query("SELECT d FROM Device d WHERE d.lastSeen IS NULL OR d.lastSeen < :since")
    List<Device> findDevicesNotSeenSince(@Param("since") LocalDateTime since);

    /**
     * Find online devices by home ID
     */
    @Query("SELECT d FROM Device d WHERE d.homeId = :homeId AND d.status = 'ONLINE'")
    List<Device> findOnlineDevicesByHomeId(@Param("homeId") UUID homeId);

    /**
     * Count devices by status
     */
    long countByStatus(Device.DeviceStatus status);

    /**
     * Count devices by home ID
     */
    long countByHomeId(UUID homeId);

    /**
     * Find devices with pagination and filtering
     */
    @Query("SELECT d FROM Device d WHERE " +
           "(:homeId IS NULL OR d.homeId = :homeId) AND " +
           "(:roomId IS NULL OR d.roomId = :roomId) AND " +
           "(:deviceType IS NULL OR d.deviceType = :deviceType) AND " +
           "(:status IS NULL OR d.status = :status)")
    Page<Device> findDevicesWithFilters(
            @Param("homeId") UUID homeId,
            @Param("roomId") UUID roomId,
            @Param("deviceType") String deviceType,
            @Param("status") Device.DeviceStatus status,
            Pageable pageable
    );

    /**
     * Search devices by name (case-insensitive)
     */
    @Query("SELECT d FROM Device d WHERE LOWER(d.name) LIKE LOWER(CONCAT('%', :name, '%'))")
    List<Device> findByNameContainingIgnoreCase(@Param("name") String name);

    /**
     * Check if device exists by serial number
     */
    boolean existsBySerialNumber(String serialNumber);

    /**
     * Check if device exists by MAC address
     */
    boolean existsByMacAddress(String macAddress);

    /**
     * Find devices by multiple IDs
     */
    List<Device> findByIdIn(List<UUID> ids);

    /**
     * Update device status by ID
     */
    @Query("UPDATE Device d SET d.status = :status, d.lastSeen = :lastSeen WHERE d.id = :deviceId")
    void updateDeviceStatus(@Param("deviceId") UUID deviceId, 
                           @Param("status") Device.DeviceStatus status, 
                           @Param("lastSeen") LocalDateTime lastSeen);
}