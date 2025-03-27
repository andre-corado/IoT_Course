import paho.mqtt.client as mqtt
import time
import json
import random
import mysql.connector
from datetime import datetime

# Configuración de conexión MQTT
BROKER_ADDRESS = "localhost"
PORT = 1883
TOPIC_TEMPERATURA = "temperatura"
TOPIC_VENTILADOR = "ventilador"

# Configuración de la base de datos
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "admin",
    "database": "sensores_sistema"
}

# Configuración de umbrales de temperatura
TEMP_MIN = 25.0
TEMP_MAX = 32.0

# ID y ubicación del ventilador
ID_VENTILADOR = "vent-001"
UBICACION_VENTILADOR = "Sala principal"

# Variables globales
ventilador_estado = False
ventilador_velocidad = 0
ultimo_cambio = time.time()

# Conexión a la base de datos - Conexión global para evitar abrir y cerrar constantemente
db_conexion = None

def inicializar_conexion_db():
    global db_conexion
    try:
        if db_conexion is None or not db_conexion.is_connected():
            db_conexion = mysql.connector.connect(**DB_CONFIG)
            print("Conexión a la base de datos establecida")
        return True
    except mysql.connector.Error as error:
        print(f"Error al conectar a la base de datos: {error}")
        return False

# Actualizar la tabla ventilador
def actualizar_ventilador(estado, velocidad):
    global db_conexion
    
    if not inicializar_conexion_db():
        print("No se pudo establecer conexión con la base de datos")
        return
    
    try:
        cursor = db_conexion.cursor()
        
        # Insertar el nuevo estado en la tabla ventilador
        query = "INSERT INTO ventilador (estado, velocidad, id_ventilador, ubicacion) VALUES (%s, %s, %s, %s)"
        valores = (estado, velocidad, ID_VENTILADOR, UBICACION_VENTILADOR)
        
        cursor.execute(query, valores)
        db_conexion.commit()
        
        print(f"Tabla 'ventilador' actualizada: estado={estado}, velocidad={velocidad}")
        cursor.close()
    except mysql.connector.Error as error:
        print(f"Error al actualizar la tabla ventilador: {error}")
        # Intentar reconectar en caso de error de conexión
        if "MySQL Connection not available" in str(error):
            db_conexion = None
            print("Conexión perdida, se intentará reconectar en la próxima operación")

# Registrar en historial de actuadores
def registrar_historial(tipo_accion, valor_anterior, valor_nuevo):
    global db_conexion
    
    if not inicializar_conexion_db():
        print("No se pudo establecer conexión con la base de datos")
        return
    
    try:
        cursor = db_conexion.cursor()
        
        # Insertar en la tabla historial_actuadores
        query = """
            INSERT INTO historial_actuadores 
            (tipo_actuador, id_actuador, accion, valor_anterior, valor_nuevo, usuario)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = ("Ventilador", ID_VENTILADOR, tipo_accion, valor_anterior, valor_nuevo, "Sistema")
        
        cursor.execute(query, valores)
        db_conexion.commit()
        
        print(f"Historial actualizado: {tipo_accion}")
        cursor.close()
    except mysql.connector.Error as error:
        print(f"Error al actualizar el historial: {error}")
        # Intentar reconectar en caso de error de conexión
        if "MySQL Connection not available" in str(error):
            db_conexion = None
            print("Conexión perdida, se intentará reconectar en la próxima operación")

# Publicar el estado del ventilador en el topic
def publicar_estado_ventilador():
    cliente_pub = mqtt.Client()
    cliente_pub.connect(BROKER_ADDRESS, PORT, 60)
    
    datos_ventilador = {
        "id": ID_VENTILADOR,
        "ubicacion": UBICACION_VENTILADOR,
        "estado": ventilador_estado,
        "velocidad": ventilador_velocidad,
        "timestamp": time.time()
    }
    
    mensaje = json.dumps(datos_ventilador)
    cliente_pub.publish(TOPIC_VENTILADOR, mensaje)
    print(f"Estado ventilador publicado: {'Encendido' if ventilador_estado else 'Apagado'} - Velocidad: {ventilador_velocidad}%")
    cliente_pub.disconnect()


def controlar_ventilador(temperatura):
    global ventilador_estado, ventilador_velocidad, ultimo_cambio
    
    # Evitar cambios demasiado frecuentes (mínimo 10 segundos entre cambios)
    tiempo_actual = time.time()
    if tiempo_actual - ultimo_cambio < 10:
        return
    
    estado_anterior = ventilador_estado
    velocidad_anterior = ventilador_velocidad
    
    # Determinar el nuevo estado basado en la temperatura - LÓGICA SIMPLIFICADA
    if temperatura >= TEMP_MIN:
        # Temperatura >= 25°C - encender ventilador
        nuevo_estado = True
        
        # Calcular velocidad proporcional desde TEMP_MIN hasta TEMP_MAX
        # 0% en TEMP_MIN, 100% en TEMP_MAX
        if temperatura >= TEMP_MAX:
            nueva_velocidad = 100
        else:
            porcentaje = (temperatura - TEMP_MIN) / (TEMP_MAX - TEMP_MIN)
            nueva_velocidad = int(porcentaje * 100)
        
        print(f"Temperatura {temperatura}°C >= {TEMP_MIN}°C - Ventilador ENCENDIDO - Velocidad: {nueva_velocidad}%")
    else:
        # Temperatura < 25°C - apagar ventilador
        nuevo_estado = False
        nueva_velocidad = 0
        print(f"Temperatura {temperatura}°C < {TEMP_MIN}°C - Ventilador APAGADO")
    
    # Si hay cambio, actualizar estado y publicar
    if nuevo_estado != estado_anterior or nueva_velocidad != velocidad_anterior:
        ventilador_estado = nuevo_estado
        ventilador_velocidad = nueva_velocidad
        ultimo_cambio = tiempo_actual
        
        # Determinar tipo de acción para el historial
        if nuevo_estado != estado_anterior:
            tipo_accion = "Encendido" if nuevo_estado else "Apagado"
        else:
            tipo_accion = "Cambio de velocidad"
        
        # Publicar el nuevo estado del ventilador
        publicar_estado_ventilador()
        
        # Actualizar la base de datos
        actualizar_ventilador(int(ventilador_estado), ventilador_velocidad)
        
        # Registrar el cambio en el historial
        valor_anterior = f"Estado: {estado_anterior}, Velocidad: {velocidad_anterior}"
        valor_nuevo = f"Estado: {ventilador_estado}, Velocidad: {ventilador_velocidad}"
        registrar_historial(tipo_accion, valor_anterior, valor_nuevo)
    else:
        print(f"No hay cambios en el estado del ventilador: {'Encendido' if ventilador_estado else 'Apagado'}, Velocidad: {ventilador_velocidad}%")


# Callback cuando se recibe un mensaje
def on_message(client, userdata, msg):
    try:
        if msg.topic == TOPIC_TEMPERATURA:
            datos = json.loads(msg.payload.decode())
            temperatura = datos["valor"]
            estado = datos["estado"]
            
            print(f"Temperatura recibida: {temperatura}°C - Estado: {estado}")
            
            # Controlar el ventilador según la temperatura
            controlar_ventilador(temperatura)
    except Exception as e:
        print(f"Error al procesar mensaje: {e}")

# Callback de conexión
def on_connect(client, userdata, flags, rc):
    print(f"Conectado al broker con código: {rc}")
    client.subscribe(TOPIC_TEMPERATURA)
    print(f"Suscrito al topic: {TOPIC_TEMPERATURA}")

# Función principal para el monitor de temperatura
def monitorear_temperatura():
    cliente = mqtt.Client()
    cliente.on_connect = on_connect
    cliente.on_message = on_message
    
    print(f"Conectando al broker MQTT en {BROKER_ADDRESS}:{PORT}...")
    cliente.connect(BROKER_ADDRESS, PORT, 60)
    
    # Inicializar conexión a la base de datos al arrancar
    inicializar_conexion_db()
    
    try:
        print("Iniciando monitoreo de temperatura...")
        print(f"Rangos de temperatura: Min: {TEMP_MIN}°C, Max: {TEMP_MAX}°C")
        print("Presiona Ctrl+C para detener")
        print("-" * 50)
        
        cliente.loop_forever()
        
    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario")
    finally:
        cliente.disconnect()
        # Cerrar conexión de base de datos
        if db_conexion and db_conexion.is_connected():
            db_conexion.close()
            print("Conexión a la base de datos cerrada")
        print("Desconectado del broker")

# Suscriptor simple para mostrar el estado del ventilador
def suscriptor_ventilador():
    def on_connect_sub(client, userdata, flags, rc):
        print(f"Suscriptor conectado al broker con código: {rc}")
        client.subscribe(TOPIC_VENTILADOR)
        print(f"Suscrito al topic: {TOPIC_VENTILADOR}")
    
    def on_message_sub(client, userdata, msg):
        try:
            datos = json.loads(msg.payload.decode())
            print("\n--- ESTADO DEL VENTILADOR ---")
            print(f"ID: {datos['id']}")
            print(f"Ubicación: {datos['ubicacion']}")
            print(f"Estado: {'Encendido' if datos['estado'] else 'Apagado'}")
            print(f"Velocidad: {datos['velocidad']}%")
            print(f"Timestamp: {datetime.fromtimestamp(datos['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 30)
        except Exception as e:
            print(f"Error al procesar mensaje del ventilador: {e}")
    
    cliente_sub = mqtt.Client()
    cliente_sub.on_connect = on_connect_sub
    cliente_sub.on_message = on_message_sub
    
    print(f"Suscriptor ventilador conectando al broker MQTT en {BROKER_ADDRESS}:{PORT}...")
    cliente_sub.connect(BROKER_ADDRESS, PORT, 60)
    
    try:
        print("Iniciando suscripción a estado del ventilador...")
        print("Presiona Ctrl+C para detener")
        print("-" * 50)
        
        cliente_sub.loop_forever()
        
    except KeyboardInterrupt:
        print("\nSuscripción detenida por el usuario")
    finally:
        cliente_sub.disconnect()
        print("Desconectado del broker")

# Simulador de temperatura para pruebas (envía datos al topic de temperatura)
def simulador_temperatura():
    cliente_pub = mqtt.Client()
    cliente_pub.connect(BROKER_ADDRESS, PORT, 60)
    
    try:
        print("Iniciando simulador de temperatura...")
        print("Presiona Ctrl+C para detener")
        print("-" * 50)
        
        while True:
            # Generar temperatura aleatoria entre 18 y 32 grados
            temperatura = round(random.uniform(18.0, 32.0), 1)
            estado = "Normal"
            
            datos_temperatura = {
                "sensor_id": "temp-001",
                "ubicacion": "Sala principal",
                "valor": temperatura,
                "estado": estado,
                "timestamp": time.time()
            }
            
            mensaje = json.dumps(datos_temperatura)
            cliente_pub.publish(TOPIC_TEMPERATURA, mensaje)
            print(f"Temperatura publicada: {temperatura}°C")
            
            # Esperar entre 5 y 15 segundos para la próxima lectura
            tiempo_espera = random.randint(5, 15)
            time.sleep(tiempo_espera)
            
    except KeyboardInterrupt:
        print("\nSimulador detenido por el usuario")
    finally:
        cliente_pub.disconnect()
        print("Desconectado del broker")

if __name__ == "__main__":
    import threading
    
    # Crear thread para el suscriptor del ventilador
    thread_sub = threading.Thread(target=suscriptor_ventilador)
    thread_sub.daemon = True
    thread_sub.start()
    
    # Crear thread para el simulador de temperatura (opcional para pruebas)
    # Descomentar las siguientes líneas para activar el simulador
    # thread_sim = threading.Thread(target=simulador_temperatura)
    # thread_sim.daemon = True
    # thread_sim.start()
    
    # Iniciar el monitor de temperatura en el thread principal
    monitorear_temperatura()