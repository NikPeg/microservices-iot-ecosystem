package main

import (
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
)

// TemperatureResponse represents the response structure for temperature data
type TemperatureResponse struct {
	Value       float64   `json:"value"`
	Unit        string    `json:"unit"`
	Timestamp   time.Time `json:"timestamp"`
	Location    string    `json:"location"`
	Status      string    `json:"status"`
	SensorID    string    `json:"sensor_id"`
	SensorType  string    `json:"sensor_type"`
	Description string    `json:"description"`
}

// HealthResponse represents the health check response
type HealthResponse struct {
	Status    string    `json:"status"`
	Timestamp time.Time `json:"timestamp"`
	Version   string    `json:"version"`
}

func main() {
	// Initialize random seed
	rand.Seed(time.Now().UnixNano())

	// Set up Gin router
	router := gin.Default()

	// Add CORS middleware
	router.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})

	// Health check endpoint
	router.GET("/health", healthCheck)

	// Temperature endpoint
	router.GET("/temperature", getTemperature)

	// Temperature by sensor ID endpoint
	router.GET("/temperature/:sensorId", getTemperatureBySensorID)

	// Get server port from environment or use default
	port := getEnv("PORT", "8081")
	if port[0] != ':' {
		port = ":" + port
	}

	log.Printf("Temperature API server starting on port %s", port)
	log.Fatal(http.ListenAndServe(port, router))
}

// healthCheck handles the health check endpoint
func healthCheck(c *gin.Context) {
	response := HealthResponse{
		Status:    "ok",
		Timestamp: time.Now(),
		Version:   "1.0.0",
	}
	c.JSON(http.StatusOK, response)
}

// getTemperature handles the /temperature endpoint with location parameter
func getTemperature(c *gin.Context) {
	location := c.Query("location")
	if location == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "location parameter is required",
		})
		return
	}

	// Generate random temperature based on location
	temperature := generateTemperatureForLocation(location)

	response := TemperatureResponse{
		Value:       temperature,
		Unit:        "°C",
		Timestamp:   time.Now(),
		Location:    location,
		Status:      "active",
		SensorID:    fmt.Sprintf("sensor-%s-%d", location, rand.Intn(1000)),
		SensorType:  "temperature",
		Description: fmt.Sprintf("Temperature reading for %s", location),
	}

	c.JSON(http.StatusOK, response)
}

// getTemperatureBySensorID handles the /temperature/{sensorId} endpoint
func getTemperatureBySensorID(c *gin.Context) {
	sensorID := c.Param("sensorId")
	if sensorID == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "sensor ID is required",
		})
		return
	}

	// Check if sensor ID is valid
	if !isValidSensorID(sensorID) {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "sensor not found",
		})
		return
	}

	// Extract location from sensor ID or use default
	location := extractLocationFromSensorID(sensorID)

	// Generate random temperature
	temperature := generateTemperatureForLocation(location)

	response := TemperatureResponse{
		Value:       temperature,
		Unit:        "°C",
		Timestamp:   time.Now(),
		Location:    location,
		Status:      "active",
		SensorID:    sensorID,
		SensorType:  "temperature",
		Description: fmt.Sprintf("Temperature reading from sensor %s", sensorID),
	}

	c.JSON(http.StatusOK, response)
}

// generateTemperatureForLocation generates a realistic temperature based on location
func generateTemperatureForLocation(location string) float64 {
	// Base temperature ranges for different locations
	var baseTemp, variance float64

	switch location {
	case "living_room", "Living Room", "livingroom":
		baseTemp = 22.0
		variance = 3.0
	case "bedroom", "Bedroom":
		baseTemp = 20.0
		variance = 2.5
	case "kitchen", "Kitchen":
		baseTemp = 24.0
		variance = 4.0
	case "bathroom", "Bathroom":
		baseTemp = 23.0
		variance = 2.0
	case "garage", "Garage":
		baseTemp = 15.0
		variance = 8.0
	case "outdoor", "Outdoor", "outside":
		baseTemp = 10.0
		variance = 15.0
	default:
		baseTemp = 21.0
		variance = 4.0
	}

	// Add some time-based variation (simulate day/night cycle)
	hour := time.Now().Hour()
	timeVariation := 0.0
	if hour >= 6 && hour <= 18 {
		// Daytime - slightly warmer
		timeVariation = 1.0
	} else {
		// Nighttime - slightly cooler
		timeVariation = -1.0
	}

	// Generate random temperature within realistic range
	randomVariation := (rand.Float64() - 0.5) * 2 * variance
	temperature := baseTemp + timeVariation + randomVariation

	// Round to 1 decimal place
	return float64(int(temperature*10)) / 10
}

// isValidSensorID checks if a sensor ID is valid
func isValidSensorID(sensorID string) bool {
	// Define valid sensor ID patterns
	validSensorIDs := []string{
		"sensor-living_room-001",
		"sensor-bedroom-001",
		"sensor-kitchen-001",
		"sensor-bathroom-001",
		"sensor-garage-001",
		"sensor-outdoor-001",
	}

	// Check if sensor ID matches any valid pattern
	for _, validID := range validSensorIDs {
		if sensorID == validID {
			return true
		}
	}

	// Also accept sensor IDs that follow the pattern sensor-{location}-{number}
	if len(sensorID) > 7 && sensorID[:7] == "sensor-" {
		parts := sensorID[7:] // Remove "sensor-" prefix
		// Find the last dash
		lastDashIndex := -1
		for i := len(parts) - 1; i >= 0; i-- {
			if parts[i] == '-' {
				lastDashIndex = i
				break
			}
		}

		if lastDashIndex > 0 {
			location := parts[:lastDashIndex]
			numberPart := parts[lastDashIndex+1:]

			// Check if location is valid and number part is numeric
			validLocations := []string{"living_room", "bedroom", "kitchen", "bathroom", "garage", "outdoor"}
			for _, validLocation := range validLocations {
				if location == validLocation {
					if _, err := strconv.Atoi(numberPart); err == nil {
						return true
					}
				}
			}
		}
	}

	return false
}

// extractLocationFromSensorID extracts location information from sensor ID
func extractLocationFromSensorID(sensorID string) string {
	// Try to parse sensor ID to extract location
	// Format: sensor-{location}-{number} or just use sensor ID as location
	if len(sensorID) > 7 && sensorID[:7] == "sensor-" {
		parts := sensorID[7:] // Remove "sensor-" prefix
		// Find the last dash and take everything before it as location
		for i := len(parts) - 1; i >= 0; i-- {
			if parts[i] == '-' {
				return parts[:i]
			}
		}
		return parts
	}

	// If sensor ID is numeric, use default location
	if _, err := strconv.Atoi(sensorID); err == nil {
		return "unknown"
	}

	return sensorID
}

// getEnv gets an environment variable or returns a default value
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}
