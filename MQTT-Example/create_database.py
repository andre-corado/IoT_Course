import mysql.connector

try:
    # Conectar al servidor MySQL sin especificar base de datos para crear la DB
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin"
    )
    cursor = conn.cursor()

    # Crear la base de datos 'sensores_sistema' si no existe
    cursor.execute("CREATE DATABASE IF NOT EXISTS sensores_sistema")
    conn.commit()
    print("Base de datos 'sensores_sistema' creada o ya existente.")

    cursor.close()
    conn.close()

    # Conectar a la base de datos 'sensores_sistema'
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="sensores_sistema"
    )
    cursor = conn.cursor()

    # Tabla para datos de temperatura
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temperatura (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            valor FLOAT,           -- Temperatura en °C
            ubicacion VARCHAR(50), -- Ubicación del sensor
            estado VARCHAR(20)     -- Normal, Alerta, etc.
        )
    """)
    print("Tabla 'temperatura' creada o ya existente.")

    # Tabla para datos de humedad
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS humedad (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            valor FLOAT,           -- Humedad en %
            ubicacion VARCHAR(50), -- Ubicación del sensor
            estado VARCHAR(20)     -- Normal, Alerta, etc.
        )
    """)
    print("Tabla 'humedad' creada o ya existente.")

    # Tabla para estado de ventiladores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventilador (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado BOOLEAN,        -- TRUE = Encendido, FALSE = Apagado
            velocidad INT,         -- Velocidad (0-100%)
            id_ventilador VARCHAR(50), -- Identificador único del ventilador
            ubicacion VARCHAR(50)  -- Ubicación del ventilador
        )
    """)
    print("Tabla 'ventilador' creada o ya existente.")

    # Tabla para historial de cambios en actuadores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_actuadores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tipo_actuador VARCHAR(50),   -- Tipo: Ventilador, Calefactor, etc.
            id_actuador VARCHAR(50),     -- Identificador único del actuador
            accion VARCHAR(100),         -- Descripción de la acción realizada
            valor_anterior VARCHAR(50),  -- Estado anterior
            valor_nuevo VARCHAR(50),     -- Nuevo estado
            usuario VARCHAR(50)          -- Usuario que realizó el cambio
        )
    """)
    print("Tabla 'historial_actuadores' creada o ya existente.")

except mysql.connector.Error as err:
    print("Error:", err)

finally:
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'conn' in locals() and conn:
        conn.close()