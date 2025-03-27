import mysql.connector
import random
import time

try:
    # Conectar a la base de datos 'test'
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="test"
    )
    cursor = conn.cursor()
    print("Conexión a la base de datos 'test' exitosa.")

    while True:
        # --- Weather Data ---
        temperature = round(random.uniform(15.0, 35.0), 2)  # °C
        humidity = round(random.uniform(20.0, 90.0), 2)      # %
        pressure = round(random.uniform(950.0, 1050.0), 2)   # hPa
        weather_query = """
            INSERT INTO weather_data (temperature, humidity, pressure)
            VALUES (%s, %s, %s)
        """
        weather_data = (temperature, humidity, pressure)
        cursor.execute(weather_query, weather_data)
        conn.commit()
        print(f"Weather Data: Temp={temperature}°C, Hum={humidity}%, Pressure={pressure} hPa")

        # --- Server Status ---
        cpu_usage = round(random.uniform(0.0, 100.0), 2)       # %
        memory_usage = round(random.uniform(0.0, 100.0), 2)    # %
        server_query = """
            INSERT INTO server_status (cpu_usage, memory_usage)
            VALUES (%s, %s)
        """
        server_data = (cpu_usage, memory_usage)
        cursor.execute(server_query, server_data)
        conn.commit()
        print(f"Server Status: CPU={cpu_usage}%, Mem={memory_usage}%")

        # --- Air Quality ---
        co2 = round(random.uniform(350, 1000), 2)    # ppm
        pm25 = round(random.uniform(0, 100), 2)        # µg/m³
        pm10 = round(random.uniform(0, 150), 2)        # µg/m³
        voc = round(random.uniform(50, 500), 2)        # ppb
        air_query = """
            INSERT INTO air_quality (co2, pm25, pm10, voc)
            VALUES (%s, %s, %s, %s)
        """
        air_data = (co2, pm25, pm10, voc)
        cursor.execute(air_query, air_data)
        conn.commit()
        print(f"Air Quality: CO₂={co2}ppm, PM2.5={pm25}µg/m³, PM10={pm10}µg/m³, VOC={voc}ppb")

        # --- Energy Consumption ---
        voltage = round(random.uniform(210, 240), 2)   # V
        current = round(random.uniform(0, 20), 2)        # A
        power = round(random.uniform(100, 5000), 2)      # W
        energy_usage = round(random.uniform(0.1, 10), 2) # kWh
        energy_query = """
            INSERT INTO energy_consumption (voltage, current, power, energy_usage)
            VALUES (%s, %s, %s, %s)
        """
        energy_data = (voltage, current, power, energy_usage)
        cursor.execute(energy_query, energy_data)
        conn.commit()
        print(f"Energy Consumption: Voltage={voltage}V, Current={current}A, Power={power}W, Usage={energy_usage}kWh")

        # --- Vehicle Tracking ---
        vehicle_id = f"V{random.randint(1, 10)}"  # Simula diferentes vehículos
        # Para una simulación más localizada, se pueden usar rangos de coordenadas reales
        latitude = round(random.uniform(40.0, 41.0), 6)
        longitude = round(random.uniform(-74.0, -73.0), 6)
        speed = round(random.uniform(0, 120), 2)       # km/h
        vehicle_query = """
            INSERT INTO vehicle_tracking (vehicle_id, latitude, longitude, speed)
            VALUES (%s, %s, %s, %s)
        """
        vehicle_data = (vehicle_id, latitude, longitude, speed)
        cursor.execute(vehicle_query, vehicle_data)
        conn.commit()
        print(f"Vehicle Tracking: ID={vehicle_id}, Lat={latitude}, Lon={longitude}, Speed={speed} km/h")

        # Espera 5 segundos antes de insertar nuevos datos
        time.sleep(5)

except mysql.connector.Error as err:
    print("Error:", err)

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
