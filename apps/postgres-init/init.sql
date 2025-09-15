-- PostgreSQL initialization script for Smart Home IoT Ecosystem
-- This script creates the basic database structure for the smart home application

-- Create database if it doesn't exist
-- Note: This will be executed by the postgres user in the container
-- The database 'smarthome' is already created by POSTGRES_DB environment variable

-- Connect to the smarthome database
\c smarthome;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create homes table
CREATE TABLE IF NOT EXISTS homes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    address TEXT,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create rooms table
CREATE TABLE IF NOT EXISTS rooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    home_id UUID NOT NULL REFERENCES homes(id) ON DELETE CASCADE,
    room_type VARCHAR(50), -- living_room, bedroom, kitchen, bathroom, etc.
    floor_number INTEGER DEFAULT 1,
    area_sqm DECIMAL(8,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create device_types table
CREATE TABLE IF NOT EXISTS device_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL, -- sensor, actuator, controller
    description TEXT,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    capabilities JSONB, -- JSON array of capabilities
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create devices table
CREATE TABLE IF NOT EXISTS devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    device_type_id UUID NOT NULL REFERENCES device_types(id),
    room_id UUID NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    serial_number VARCHAR(100) UNIQUE,
    mac_address VARCHAR(17),
    ip_address INET,
    firmware_version VARCHAR(50),
    status VARCHAR(20) DEFAULT 'offline', -- online, offline, error, maintenance
    last_seen TIMESTAMP WITH TIME ZONE,
    battery_level INTEGER CHECK (battery_level >= 0 AND battery_level <= 100),
    configuration JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create sensor_readings table for storing sensor data
CREATE TABLE IF NOT EXISTS sensor_readings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    sensor_type VARCHAR(50) NOT NULL, -- temperature, humidity, motion, light, etc.
    value DECIMAL(10,4) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    quality_score DECIMAL(3,2) DEFAULT 1.0 CHECK (quality_score >= 0 AND quality_score <= 1),
    metadata JSONB
);

-- Create device_commands table for storing commands sent to devices
CREATE TABLE IF NOT EXISTS device_commands (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    command_type VARCHAR(50) NOT NULL, -- turn_on, turn_off, set_temperature, etc.
    parameters JSONB,
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, acknowledged, completed, failed
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0
);

-- Create automation_rules table
CREATE TABLE IF NOT EXISTS automation_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    home_id UUID NOT NULL REFERENCES homes(id) ON DELETE CASCADE,
    description TEXT,
    trigger_conditions JSONB NOT NULL, -- JSON object defining trigger conditions
    actions JSONB NOT NULL, -- JSON array of actions to execute
    is_active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_executed TIMESTAMP WITH TIME ZONE
);

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL, -- info, warning, error, alert
    priority VARCHAR(20) DEFAULT 'normal', -- low, normal, high, critical
    is_read BOOLEAN DEFAULT false,
    related_device_id UUID REFERENCES devices(id),
    related_rule_id UUID REFERENCES automation_rules(id),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_homes_owner_id ON homes(owner_id);
CREATE INDEX IF NOT EXISTS idx_rooms_home_id ON rooms(home_id);
CREATE INDEX IF NOT EXISTS idx_devices_room_id ON devices(room_id);
CREATE INDEX IF NOT EXISTS idx_devices_device_type_id ON devices(device_type_id);
CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_id ON sensor_readings(device_id);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_type ON sensor_readings(sensor_type);
CREATE INDEX IF NOT EXISTS idx_device_commands_device_id ON device_commands(device_id);
CREATE INDEX IF NOT EXISTS idx_device_commands_status ON device_commands(status);
CREATE INDEX IF NOT EXISTS idx_automation_rules_home_id ON automation_rules(home_id);
CREATE INDEX IF NOT EXISTS idx_automation_rules_is_active ON automation_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);

-- Insert sample data for testing

-- Insert sample device types
INSERT INTO device_types (name, category, description, manufacturer, capabilities) VALUES
('Temperature Sensor', 'sensor', 'Digital temperature sensor with high precision', 'Generic', '["temperature_reading"]'),
('Humidity Sensor', 'sensor', 'Digital humidity sensor', 'Generic', '["humidity_reading"]'),
('Motion Sensor', 'sensor', 'PIR motion detection sensor', 'Generic', '["motion_detection"]'),
('Smart Light Bulb', 'actuator', 'WiFi-enabled LED light bulb', 'Generic', '["on_off", "dimming", "color_change"]'),
('Smart Thermostat', 'controller', 'WiFi-enabled thermostat with scheduling', 'Generic', '["temperature_control", "scheduling", "remote_access"]'),
('Door Lock', 'actuator', 'Smart door lock with keypad', 'Generic', '["lock_unlock", "access_codes"]')
ON CONFLICT (name) DO NOTHING;

-- Insert sample user
INSERT INTO users (username, email, password_hash, first_name, last_name) VALUES
('admin', 'admin@smarthome.local', crypt('admin123', gen_salt('bf')), 'Admin', 'User')
ON CONFLICT (username) DO NOTHING;

-- Get the admin user ID for further inserts
DO $$
DECLARE
    admin_user_id UUID;
    home_id UUID;
    living_room_id UUID;
    bedroom_id UUID;
    kitchen_id UUID;
    temp_sensor_type_id UUID;
    humidity_sensor_type_id UUID;
    motion_sensor_type_id UUID;
    light_bulb_type_id UUID;
BEGIN
    -- Get admin user ID
    SELECT id INTO admin_user_id FROM users WHERE username = 'admin';
    
    -- Insert sample home
    INSERT INTO homes (name, address, owner_id) VALUES
    ('Demo Smart Home', '123 Smart Street, Tech City', admin_user_id)
    ON CONFLICT DO NOTHING
    RETURNING id INTO home_id;
    
    -- If home already exists, get its ID
    IF home_id IS NULL THEN
        SELECT id INTO home_id FROM homes WHERE owner_id = admin_user_id LIMIT 1;
    END IF;
    
    -- Insert sample rooms
    INSERT INTO rooms (name, home_id, room_type) VALUES
    ('Living Room', home_id, 'living_room'),
    ('Master Bedroom', home_id, 'bedroom'),
    ('Kitchen', home_id, 'kitchen')
    ON CONFLICT DO NOTHING;
    
    -- Get room IDs
    SELECT id INTO living_room_id FROM rooms WHERE name = 'Living Room' AND home_id = home_id;
    SELECT id INTO bedroom_id FROM rooms WHERE name = 'Master Bedroom' AND home_id = home_id;
    SELECT id INTO kitchen_id FROM rooms WHERE name = 'Kitchen' AND home_id = home_id;
    
    -- Get device type IDs
    SELECT id INTO temp_sensor_type_id FROM device_types WHERE name = 'Temperature Sensor';
    SELECT id INTO humidity_sensor_type_id FROM device_types WHERE name = 'Humidity Sensor';
    SELECT id INTO motion_sensor_type_id FROM device_types WHERE name = 'Motion Sensor';
    SELECT id INTO light_bulb_type_id FROM device_types WHERE name = 'Smart Light Bulb';
    
    -- Insert sample devices
    INSERT INTO devices (name, device_type_id, room_id, serial_number, status) VALUES
    ('Living Room Temperature Sensor', temp_sensor_type_id, living_room_id, 'TEMP001', 'online'),
    ('Living Room Humidity Sensor', humidity_sensor_type_id, living_room_id, 'HUM001', 'online'),
    ('Living Room Motion Sensor', motion_sensor_type_id, living_room_id, 'MOT001', 'online'),
    ('Living Room Smart Light', light_bulb_type_id, living_room_id, 'LIGHT001', 'online'),
    ('Bedroom Temperature Sensor', temp_sensor_type_id, bedroom_id, 'TEMP002', 'online'),
    ('Kitchen Temperature Sensor', temp_sensor_type_id, kitchen_id, 'TEMP003', 'online')
    ON CONFLICT (serial_number) DO NOTHING;
    
END $$;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_homes_updated_at BEFORE UPDATE ON homes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_rooms_updated_at BEFORE UPDATE ON rooms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_devices_updated_at BEFORE UPDATE ON devices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_automation_rules_updated_at BEFORE UPDATE ON automation_rules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (the postgres user will have all permissions by default)
-- Additional users can be created and granted specific permissions as needed

COMMIT;