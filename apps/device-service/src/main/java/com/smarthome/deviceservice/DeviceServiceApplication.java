package com.smarthome.deviceservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * Main application class for Device Management Service
 * 
 * This microservice handles IoT device management including:
 * - Device registration and lifecycle management
 * - Device command execution
 * - Device status monitoring
 * - Integration with message broker for event-driven communication
 */
@SpringBootApplication
@EnableJpaAuditing
@EnableAsync
public class DeviceServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(DeviceServiceApplication.class, args);
    }
}