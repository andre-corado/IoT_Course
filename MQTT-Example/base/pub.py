import paho.mqtt.client as mqtt
import time
import json
import random
import socket
import uuid

# Configuración de conexión
BROKER_ADDRESS = "localhost"
PORT = 1883
TOPICS = ["test/1", "test/2"]

# Generar un ID único para este publicador
PUBLISHER_ID = f"publisher_{socket.gethostname()}_{uuid.uuid4().hex[:6]}"

def on_connect(client, userdata, flags, rc):
    print(f"[{PUBLISHER_ID}] Conectado al broker con código: {rc}")
    if rc == 0:
        print(f"[{PUBLISHER_ID}] Conexión exitosa al broker MQTT en {BROKER_ADDRESS}:{PORT}")
    else:
        print(f"[{PUBLISHER_ID}] Error de conexión, código: {rc}")

def on_publish(client, userdata, mid):
    print(f"[{PUBLISHER_ID}] Mensaje {mid} entregado correctamente al broker")

def generar_datos_aleatorios():
    """Genera datos aleatorios para publicar en los temas"""
    sensor_id = f"sensor_{random.randint(1, 5)}"
    return {
        "source_id": PUBLISHER_ID,
        "sensor_id": sensor_id,
        "valor": round(random.uniform(0, 100), 2),
        "unidad": random.choice(["°C", "%", "hPa", "lux"]),
        "estado": random.choice(["normal", "alerta", "crítico"]),
        "timestamp": time.time(),
        "mensaje": f"Lectura de {sensor_id} a las {time.strftime('%H:%M:%S')}"
    }

def publicar():
    # Crear cliente
    cliente = mqtt.Client(client_id=PUBLISHER_ID)
    cliente.on_connect = on_connect
    cliente.on_publish = on_publish
    
    # Conectar al broker
    print(f"[{PUBLISHER_ID}] Intentando conectar a {BROKER_ADDRESS}:{PORT}...")
    cliente.connect(BROKER_ADDRESS, PORT, 60)
    cliente.loop_start()
    
    # Esperar un momento para asegurar conexión
    time.sleep(1)
    
    try:
        print(f"[{PUBLISHER_ID}] Iniciando publicación de mensajes...")
        print("-" * 70)
        mensaje_contador = 0
        
        while True:
            # Elegir un tema aleatorio de la lista
            topic = random.choice(TOPICS)
            mensaje_contador += 1
            
            # Generar datos aleatorios
            datos = generar_datos_aleatorios()
            mensaje = json.dumps(datos, indent=2)
            
            # Mostrar información detallada en consola
            print(f"\n[{PUBLISHER_ID}] ENVIANDO MENSAJE #{mensaje_contador}:")
            print(f"  → Topic: {topic}")
            print(f"  → Contenido: {mensaje}")
            
            # Publicar mensaje
            result = cliente.publish(topic, mensaje, qos=1)
            
            # Esperar un tiempo entre publicaciones
            time.sleep(random.uniform(10.0, 20.0))
            print("-" * 70)
            
    except KeyboardInterrupt:
        print(f"\n[{PUBLISHER_ID}] Publicación detenida por el usuario")
    finally:
        cliente.loop_stop()
        cliente.disconnect()
        print(f"[{PUBLISHER_ID}] Desconectado del broker")

if __name__ == "__main__":
    print("-" * 70)
    print(f"PUBLICADOR MQTT - ID: {PUBLISHER_ID}")
    print("-" * 70)
    publicar()