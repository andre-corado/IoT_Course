import paho.mqtt.client as mqtt
import json
import mysql.connector
from datetime import datetime

# Configuración de conexión MQTT
BROKER_ADDRESS = "localhost"
PORT = 1883
TOPIC = "temperatura"

# Configuración de MySQL
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "admin"
MYSQL_DB = "sensores_sistema"

def conectar_mysql():
    """Establece conexión con la base de datos MySQL"""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        print(f"Conexión establecida con la base de datos '{MYSQL_DB}'")
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexión a MySQL: {err}")
        return None

def insertar_temperatura(conn, valor, ubicacion, estado, timestamp=None):
    """Inserta un registro de temperatura en la base de datos"""
    try:
        cursor = conn.cursor()
        
        if timestamp:
            # Convertir timestamp epoch a datetime
            dt_objeto = datetime.fromtimestamp(timestamp)
            fecha_hora = dt_objeto.strftime('%Y-%m-%d %H:%M:%S')
            query = """
                INSERT INTO temperatura (timestamp, valor, ubicacion, estado)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (fecha_hora, valor, ubicacion, estado))
        else:
            # Usar timestamp actual de MySQL
            query = """
                INSERT INTO temperatura (valor, ubicacion, estado)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (valor, ubicacion, estado))
        
        conn.commit()
        print(f"Registro de temperatura insertado: {valor}°C, {ubicacion}, {estado}")
        cursor.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error al insertar datos: {err}")
        return False

def on_connect(client, userdata, flags, rc):
    print(f"Conectado al broker MQTT con código: {rc}")
    if rc == 0:
        print(f"Suscrito al topic: {TOPIC}")
        client.subscribe(TOPIC)
    else:
        print(f"Error de conexión al broker, código: {rc}")

def on_message(client, userdata, msg):
    try:
        # Decodificar el mensaje JSON
        payload = msg.payload.decode("utf-8")
        datos = json.loads(payload)
        
        # Extraer datos
        valor = datos.get("valor")
        ubicacion = datos.get("ubicacion", "Desconocida")
        estado = datos.get("estado", "Normal")
        timestamp = datos.get("timestamp")
        
        # Guardar en MySQL
        if conn:
            insertar_temperatura(conn, valor, ubicacion, estado, timestamp)
        else:
            print("Error: No hay conexión a MySQL disponible")
            
        # Mostrar información recibida
        print(f"\nTemperatura recibida: {valor}°C")
        print(f"Ubicación: {ubicacion}")
        print(f"Estado: {estado}")
        if timestamp:
            dt_objeto = datetime.fromtimestamp(timestamp)
            print(f"Timestamp: {dt_objeto.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
    except json.JSONDecodeError:
        print(f"Error: Mensaje no es JSON válido: {msg.payload}")
    except Exception as e:
        print(f"Error al procesar mensaje: {e}")

if __name__ == "__main__":
    # Establecer conexión con MySQL
    conn = conectar_mysql()
    
    if not conn:
        print("No se pudo conectar a MySQL. Saliendo...")
        exit(1)
    
    # Crear cliente MQTT
    cliente = mqtt.Client()
    cliente.on_connect = on_connect
    cliente.on_message = on_message
    
    try:
        print(f"Conectando al broker MQTT en {BROKER_ADDRESS}:{PORT}...")
        cliente.connect(BROKER_ADDRESS, PORT, 60)
        
        print(f"Iniciando suscriptor para datos de temperatura...")
        print("Presiona Ctrl+C para detener")
        print("-" * 50)
        
        # Iniciar loop para recibir mensajes
        cliente.loop_forever()
        
    except KeyboardInterrupt:
        print("\nSuscriptor detenido por el usuario")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()
            print("Conexión a MySQL cerrada")
        cliente.disconnect()
        print("Desconectado del broker MQTT")