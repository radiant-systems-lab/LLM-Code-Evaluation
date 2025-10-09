# IoT and Sensor Networks
import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime
import requests
import socket
import threading
import queue

def mqtt_client_operations():
    """MQTT client for IoT communication"""
    try:
        # MQTT configuration
        broker_host = "localhost"
        broker_port = 1883
        client_id = "iot_device_001"
        
        # Topics
        topics = {
            'temperature': 'sensors/temperature',
            'humidity': 'sensors/humidity',
            'motion': 'sensors/motion',
            'light': 'sensors/light',
            'control': 'devices/control'
        }
        
        # Simulate MQTT client
        class MockMQTTClient:
            def __init__(self, client_id):
                self.client_id = client_id
                self.is_connected = False
                self.subscribed_topics = []
                self.published_messages = []
            
            def connect(self, host, port, keepalive=60):
                self.is_connected = True
                return 0
            
            def subscribe(self, topic, qos=0):
                self.subscribed_topics.append({'topic': topic, 'qos': qos})
                return (0, 1)
            
            def publish(self, topic, payload, qos=0, retain=False):
                message = {
                    'topic': topic,
                    'payload': payload,
                    'qos': qos,
                    'retain': retain,
                    'timestamp': datetime.now().isoformat()
                }
                self.published_messages.append(message)
                return mqtt.MQTTMessageInfo(1)
            
            def disconnect(self):
                self.is_connected = False
        
        # Create and configure client
        client = MockMQTTClient(client_id)
        client.connect(broker_host, broker_port)
        
        # Subscribe to topics
        for topic_name, topic_path in topics.items():
            client.subscribe(topic_path)
        
        # Publish sensor data
        sensor_data = [
            {'topic': topics['temperature'], 'data': {'value': 23.5, 'unit': 'C', 'sensor_id': 'TEMP_001'}},
            {'topic': topics['humidity'], 'data': {'value': 65.2, 'unit': '%', 'sensor_id': 'HUM_001'}},
            {'topic': topics['motion'], 'data': {'detected': True, 'sensor_id': 'MOT_001'}},
            {'topic': topics['light'], 'data': {'value': 450, 'unit': 'lux', 'sensor_id': 'LIGHT_001'}}
        ]
        
        for sensor in sensor_data:
            payload = json.dumps(sensor['data'])
            client.publish(sensor['topic'], payload)
        
        # Publish control commands
        control_commands = [
            {'device_id': 'LED_001', 'action': 'on', 'brightness': 80},
            {'device_id': 'FAN_001', 'action': 'set_speed', 'speed': 3},
            {'device_id': 'THERMOSTAT_001', 'action': 'set_temperature', 'temperature': 22}
        ]
        
        for command in control_commands:
            payload = json.dumps(command)
            client.publish(topics['control'], payload)
        
        client.disconnect()
        
        return {
            'client_id': client_id,
            'topics_subscribed': len(client.subscribed_topics),
            'messages_published': len(client.published_messages),
            'sensor_readings': len(sensor_data),
            'control_commands': len(control_commands)
        }
        
    except Exception as e:
        return {'error': str(e), 'simulation': True}

def sensor_data_collection():
    """Collect and process sensor data"""
    # Define sensor types
    sensor_types = {
        'temperature': {'range': (-20, 50), 'unit': 'Celsius', 'accuracy': 0.1},
        'humidity': {'range': (0, 100), 'unit': 'Percent', 'accuracy': 1.0},
        'pressure': {'range': (900, 1100), 'unit': 'hPa', 'accuracy': 0.5},
        'light': {'range': (0, 10000), 'unit': 'Lux', 'accuracy': 10},
        'noise': {'range': (30, 120), 'unit': 'dB', 'accuracy': 1},
        'air_quality': {'range': (0, 500), 'unit': 'AQI', 'accuracy': 5},
        'soil_moisture': {'range': (0, 100), 'unit': 'Percent', 'accuracy': 2},
        'ph_level': {'range': (0, 14), 'unit': 'pH', 'accuracy': 0.1}
    }
    
    # Generate sensor network
    sensors = []
    for i in range(20):
        sensor_type = random.choice(list(sensor_types.keys()))
        sensor_config = sensor_types[sensor_type]
        
        sensor = {
            'id': f"{sensor_type.upper()}_{i+1:03d}",
            'type': sensor_type,
            'location': {
                'latitude': round(random.uniform(40.0, 41.0), 6),
                'longitude': round(random.uniform(-74.0, -73.0), 6),
                'altitude': random.randint(0, 100)
            },
            'config': sensor_config,
            'status': random.choice(['active', 'active', 'active', 'maintenance', 'offline'])
        }
        sensors.append(sensor)
    
    # Simulate data collection
    collected_data = []
    for sensor in sensors:
        if sensor['status'] == 'active':
            config = sensor['config']
            base_value = random.uniform(*config['range'])
            
            # Generate multiple readings
            for reading_num in range(5):
                # Add some noise
                noise = random.uniform(-config['accuracy'], config['accuracy'])
                value = base_value + noise
                
                # Ensure value is within range
                value = max(config['range'][0], min(config['range'][1], value))
                
                reading = {
                    'sensor_id': sensor['id'],
                    'timestamp': datetime.now().isoformat(),
                    'value': round(value, 2),
                    'unit': config['unit'],
                    'quality': random.choice(['good', 'good', 'good', 'fair', 'poor'])
                }
                collected_data.append(reading)
    
    # Data aggregation
    sensor_summary = {}
    for reading in collected_data:
        sensor_id = reading['sensor_id']
        if sensor_id not in sensor_summary:
            sensor_summary[sensor_id] = {
                'readings_count': 0,
                'values': [],
                'quality_scores': []
            }
        
        sensor_summary[sensor_id]['readings_count'] += 1
        sensor_summary[sensor_id]['values'].append(reading['value'])
        sensor_summary[sensor_id]['quality_scores'].append(reading['quality'])
    
    # Calculate statistics
    for sensor_id, summary in sensor_summary.items():
        values = summary['values']
        summary['avg_value'] = sum(values) / len(values)
        summary['min_value'] = min(values)
        summary['max_value'] = max(values)
        summary['good_quality_ratio'] = summary['quality_scores'].count('good') / len(summary['quality_scores'])
    
    return {
        'total_sensors': len(sensors),
        'active_sensors': len([s for s in sensors if s['status'] == 'active']),
        'sensor_types': len(sensor_types),
        'total_readings': len(collected_data),
        'sensor_summary': len(sensor_summary),
        'data_collected': collected_data[:10]  # Sample of first 10 readings
    }

def iot_device_management():
    """IoT device management system"""
    # Device categories
    device_categories = {
        'sensors': ['temperature', 'humidity', 'motion', 'light', 'camera', 'microphone'],
        'actuators': ['led', 'servo', 'relay', 'buzzer', 'motor', 'valve'],
        'controllers': ['arduino', 'raspberry_pi', 'esp32', 'plc'],
        'communication': ['wifi_module', 'bluetooth', 'lora', 'zigbee', 'cellular']
    }
    
    # Generate device inventory
    devices = []
    device_id = 1
    
    for category, device_types in device_categories.items():
        for device_type in device_types:
            num_devices = random.randint(2, 8)
            
            for i in range(num_devices):
                device = {
                    'id': f"DEV_{device_id:04d}",
                    'name': f"{device_type}_{i+1}",
                    'category': category,
                    'type': device_type,
                    'mac_address': ':'.join([f"{random.randint(0, 255):02x}" for _ in range(6)]),
                    'ip_address': f"192.168.1.{device_id % 254 + 1}",
                    'firmware_version': f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                    'status': random.choice(['online', 'online', 'online', 'offline', 'error']),
                    'last_seen': datetime.now().isoformat(),
                    'power_consumption': round(random.uniform(0.1, 50.0), 2),  # Watts
                    'uptime': random.randint(0, 30 * 24 * 3600)  # Seconds
                }
                devices.append(device)
                device_id += 1
    
    # Device management operations
    management_operations = {
        'firmware_updates': random.randint(5, 15),
        'configuration_changes': random.randint(10, 25),
        'reboots': random.randint(2, 8),
        'diagnostics_run': random.randint(20, 40)
    }
    
    # Network topology
    network_segments = [
        {'name': 'sensor_network', 'devices': 25, 'protocol': 'ZigBee'},
        {'name': 'actuator_network', 'devices': 18, 'protocol': 'WiFi'},
        {'name': 'controller_network', 'devices': 8, 'protocol': 'Ethernet'},
        {'name': 'gateway_network', 'devices': 3, 'protocol': 'Cellular'}
    ]
    
    # Calculate statistics
    online_devices = len([d for d in devices if d['status'] == 'online'])
    total_power = sum(d['power_consumption'] for d in devices if d['status'] == 'online')
    avg_uptime = sum(d['uptime'] for d in devices) / len(devices)
    
    return {
        'total_devices': len(devices),
        'online_devices': online_devices,
        'device_categories': len(device_categories),
        'network_segments': len(network_segments),
        'total_power_consumption': round(total_power, 2),
        'average_uptime_hours': round(avg_uptime / 3600, 1),
        'management_operations': management_operations
    }

def edge_computing_simulation():
    """Edge computing for IoT data processing"""
    # Edge nodes configuration
    edge_nodes = [
        {
            'id': 'EDGE_001',
            'location': 'Building_A',
            'cpu_cores': 4,
            'memory_gb': 8,
            'storage_gb': 64,
            'connected_devices': 25
        },
        {
            'id': 'EDGE_002',
            'location': 'Building_B',
            'cpu_cores': 8,
            'memory_gb': 16,
            'storage_gb': 128,
            'connected_devices': 40
        },
        {
            'id': 'EDGE_003',
            'location': 'Parking_Lot',
            'cpu_cores': 2,
            'memory_gb': 4,
            'storage_gb': 32,
            'connected_devices': 15
        }
    ]
    
    # Processing tasks
    processing_tasks = [
        {
            'task_type': 'image_recognition',
            'input_size_mb': 2.5,
            'processing_time_ms': 150,
            'cpu_usage': 75,
            'memory_usage_mb': 512
        },
        {
            'task_type': 'anomaly_detection',
            'input_size_mb': 0.1,
            'processing_time_ms': 50,
            'cpu_usage': 30,
            'memory_usage_mb': 128
        },
        {
            'task_type': 'data_aggregation',
            'input_size_mb': 1.0,
            'processing_time_ms': 25,
            'cpu_usage': 15,
            'memory_usage_mb': 64
        },
        {
            'task_type': 'ml_inference',
            'input_size_mb': 0.5,
            'processing_time_ms': 100,
            'cpu_usage': 60,
            'memory_usage_mb': 256
        }
    ]
    
    # Simulate task distribution
    task_distribution = []
    total_tasks = 1000
    
    for _ in range(total_tasks):
        edge_node = random.choice(edge_nodes)
        task = random.choice(processing_tasks)
        
        # Calculate if edge node can handle the task
        can_process = (
            task['memory_usage_mb'] <= edge_node['memory_gb'] * 1024 * 0.8  # 80% memory limit
        )
        
        task_execution = {
            'edge_node_id': edge_node['id'],
            'task_type': task['task_type'],
            'can_process_locally': can_process,
            'processing_time_ms': task['processing_time_ms'] if can_process else task['processing_time_ms'] * 3,  # Cloud processing penalty
            'location': edge_node['location']
        }
        task_distribution.append(task_execution)
    
    # Calculate performance metrics
    local_processing = len([t for t in task_distribution if t['can_process_locally']])
    cloud_processing = total_tasks - local_processing
    
    avg_local_time = np.mean([t['processing_time_ms'] for t in task_distribution if t['can_process_locally']])
    avg_cloud_time = np.mean([t['processing_time_ms'] for t in task_distribution if not t['can_process_locally']])
    
    # Data transfer simulation
    total_data_processed = sum(task['input_size_mb'] for task in processing_tasks) * (total_tasks / len(processing_tasks))
    data_kept_local = total_data_processed * (local_processing / total_tasks)
    data_sent_cloud = total_data_processed - data_kept_local
    
    return {
        'edge_nodes': len(edge_nodes),
        'total_connected_devices': sum(node['connected_devices'] for node in edge_nodes),
        'task_types': len(processing_tasks),
        'total_tasks_processed': total_tasks,
        'local_processing_ratio': local_processing / total_tasks,
        'average_local_processing_time': avg_local_time,
        'average_cloud_processing_time': avg_cloud_time,
        'data_locality_ratio': data_kept_local / total_data_processed,
        'bandwidth_saved_mb': data_sent_cloud * 2  # Round-trip savings
    }

def industrial_iot_monitoring():
    """Industrial IoT monitoring system"""
    # Industrial equipment
    equipment = [
        {
            'id': 'MOTOR_001',
            'type': 'electric_motor',
            'location': 'Production_Line_A',
            'sensors': ['vibration', 'temperature', 'current', 'voltage'],
            'operating_hours': 15420,
            'maintenance_due': 16000
        },
        {
            'id': 'PUMP_001',
            'type': 'centrifugal_pump',
            'location': 'Cooling_System',
            'sensors': ['pressure', 'flow_rate', 'temperature', 'vibration'],
            'operating_hours': 8750,
            'maintenance_due': 10000
        },
        {
            'id': 'CONVEYOR_001',
            'type': 'belt_conveyor',
            'location': 'Assembly_Line',
            'sensors': ['speed', 'load', 'belt_tension', 'temperature'],
            'operating_hours': 12300,
            'maintenance_due': 15000
        },
        {
            'id': 'COMPRESSOR_001',
            'type': 'air_compressor',
            'location': 'Utility_Room',
            'sensors': ['pressure', 'temperature', 'vibration', 'oil_level'],
            'operating_hours': 6890,
            'maintenance_due': 8000
        }
    ]
    
    # Generate monitoring data
    monitoring_data = []
    alert_conditions = []
    
    for machine in equipment:
        for sensor in machine['sensors']:
            # Generate sensor readings based on type
            if sensor == 'temperature':
                value = random.uniform(40, 85)
                threshold = 80
                unit = 'Celsius'
            elif sensor == 'vibration':
                value = random.uniform(0.1, 5.0)
                threshold = 4.0
                unit = 'mm/s'
            elif sensor == 'pressure':
                value = random.uniform(2.0, 8.0)
                threshold = 7.5
                unit = 'bar'
            elif sensor == 'current':
                value = random.uniform(10, 50)
                threshold = 45
                unit = 'A'
            elif sensor == 'voltage':
                value = random.uniform(380, 420)
                threshold = 410
                unit = 'V'
            elif sensor == 'flow_rate':
                value = random.uniform(50, 200)
                threshold = 180
                unit = 'L/min'
            elif sensor == 'speed':
                value = random.uniform(800, 1200)
                threshold = 1150
                unit = 'RPM'
            elif sensor == 'load':
                value = random.uniform(20, 95)
                threshold = 90
                unit = 'Percent'
            elif sensor == 'belt_tension':
                value = random.uniform(500, 1500)
                threshold = 1400
                unit = 'N'
            elif sensor == 'oil_level':
                value = random.uniform(20, 100)
                threshold = 30  # Low threshold
                unit = 'Percent'
            else:
                value = random.uniform(0, 100)
                threshold = 90
                unit = 'Units'
            
            reading = {
                'equipment_id': machine['id'],
                'sensor_type': sensor,
                'value': round(value, 2),
                'unit': unit,
                'threshold': threshold,
                'status': 'normal' if (value < threshold if sensor != 'oil_level' else value > threshold) else 'alert',
                'timestamp': datetime.now().isoformat()
            }
            monitoring_data.append(reading)
            
            # Check for alert conditions
            if reading['status'] == 'alert':
                alert_conditions.append({
                    'equipment_id': machine['id'],
                    'sensor_type': sensor,
                    'value': value,
                    'threshold': threshold,
                    'severity': 'high' if value > threshold * 1.1 else 'medium'
                })
    
    # Maintenance scheduling
    maintenance_schedule = []
    for machine in equipment:
        hours_until_maintenance = machine['maintenance_due'] - machine['operating_hours']
        urgency = 'high' if hours_until_maintenance < 500 else 'medium' if hours_until_maintenance < 1000 else 'low'
        
        maintenance_schedule.append({
            'equipment_id': machine['id'],
            'type': machine['type'],
            'hours_until_maintenance': hours_until_maintenance,
            'urgency': urgency
        })
    
    return {
        'equipment_count': len(equipment),
        'total_sensors': sum(len(m['sensors']) for m in equipment),
        'monitoring_readings': len(monitoring_data),
        'alert_conditions': len(alert_conditions),
        'high_priority_alerts': len([a for a in alert_conditions if a['severity'] == 'high']),
        'maintenance_items': len(maintenance_schedule),
        'urgent_maintenance': len([m for m in maintenance_schedule if m['urgency'] == 'high'])
    }

if __name__ == "__main__":
    print("IoT and sensor network operations...")
    
    # MQTT operations
    mqtt_result = mqtt_client_operations()
    if 'error' not in mqtt_result:
        print(f"MQTT: {mqtt_result['messages_published']} messages published, {mqtt_result['topics_subscribed']} topics subscribed")
    else:
        print(f"MQTT: Simulation mode")
    
    # Sensor data collection
    sensor_result = sensor_data_collection()
    print(f"Sensors: {sensor_result['active_sensors']}/{sensor_result['total_sensors']} active, {sensor_result['total_readings']} readings")
    
    # Device management
    device_result = iot_device_management()
    print(f"Devices: {device_result['online_devices']}/{device_result['total_devices']} online, {device_result['total_power_consumption']}W total power")
    
    # Edge computing
    edge_result = edge_computing_simulation()
    print(f"Edge Computing: {edge_result['local_processing_ratio']:.1%} local processing, {edge_result['bandwidth_saved_mb']:.1f}MB bandwidth saved")
    
    # Industrial monitoring
    industrial_result = industrial_iot_monitoring()
    print(f"Industrial: {industrial_result['equipment_count']} machines, {industrial_result['alert_conditions']} alerts, {industrial_result['urgent_maintenance']} urgent maintenance")