import mysql.connector

try:
    # Conectar al servidor MySQL sin especificar base de datos para crear la DB
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin"
    )
    cursor = conn.cursor()

    # Crear la base de datos 'test' si no existe
    cursor.execute("CREATE DATABASE IF NOT EXISTS test")
    conn.commit()
    print("Base de datos 'test' creada o ya existente.")

    cursor.close()
    conn.close()

    # Conectar a la base de datos 'test'
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="test"
    )
    cursor = conn.cursor()

    # Tabla para datos meteorológicos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            temperature FLOAT,
            humidity FLOAT,
            pressure FLOAT
        )
    """)
    print("Tabla 'weather_data' creada o ya existente.")

    # Tabla para estado del servidor
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS server_status (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cpu_usage FLOAT,
            memory_usage FLOAT
        )
    """)
    print("Tabla 'server_status' creada o ya existente.")

    # Tabla para calidad del aire
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS air_quality (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            co2 FLOAT,      -- ppm
            pm25 FLOAT,     -- µg/m³
            pm10 FLOAT,     -- µg/m³
            voc FLOAT       -- ppb (Compuestos Orgánicos Volátiles)
        )
    """)
    print("Tabla 'air_quality' creada o ya existente.")

    # Tabla para consumo energético
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS energy_consumption (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            voltage FLOAT,       -- Voltaje en V
            current FLOAT,       -- Corriente en A
            power FLOAT,         -- Potencia en W
            energy_usage FLOAT   -- Consumo en kWh
        )
    """)
    print("Tabla 'energy_consumption' creada o ya existente.")

    # Tabla para tracking de vehículos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_tracking (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            vehicle_id VARCHAR(50),
            latitude FLOAT,
            longitude FLOAT,
            speed FLOAT           -- Velocidad en km/h
        )
    """)
    conn.commit()
    print("Tabla 'vehicle_tracking' creada o ya existente.")

except mysql.connector.Error as err:
    print("Error:", err)

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
