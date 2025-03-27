import paho.mqtt.client as mqtt
import json
import time
import socket
import uuid
from datetime import datetime

# Configuración de conexión
BROKER_ADDRESS = "localhost"
PORT = 1883
TOPICS = ["test/1", "test/2"]

# Generar un ID único para este suscriptor
SUBSCRIBER_ID = f"subscriber_{socket.gethostname()}_{uuid.uuid4().hex[:6]}"

def on_connect(client, userdata, flags, rc):
    print(f"[{SUBSCRIBER_ID}] Conectado al broker con código: {rc}")
    if rc == 0:
        print(f"[{SUBSCRIBER_ID}] Conexión exitosa al broker MQTT en {BROKER_ADDRESS}:{PORT}")
        # Suscribirse a los temas
        for topic in TOPICS:
            client.subscribe(topic, qos=1)
            print(f"[{SUBSCRIBER_ID}] Suscrito al tema: {topic}")
    else:
        print(f"[{SUBSCRIBER_ID}] Error de conexión, código: {rc}")

def on_message(client, userdata, msg):
    # Obtener metadata del mensaje
    topic = msg.topic
    qos = msg.qos
    retain = msg.retain
    
    # Convertir el payload de bytes a string
    try:
        payload = msg.payload.decode("utf-8")
        
        # Interpretar el mensaje como JSON
        datos = json.loads(payload)
        
        # Obtener información de origen si está disponible
        origen = datos.get("source_id", "Desconocido")
        
        # Imprimir información detallada
        print("\n" + "=" * 70)
        print(f"[{SUBSCRIBER_ID}] MENSAJE RECIBIDO:")
        print("-" * 70)
        print(f"  → Hora recepción: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        print(f"  → Topic: {topic}")
        print(f"  → QoS: {qos}")
        print(f"  → Retain: {retain}")
        print(f"  → Origen: {origen}")
        print("-" * 70)
        print("  → Contenido:")
        
        # Mostrar contenido formateado
        for clave, valor in datos.items():
            if clave != "source_id":  # Ya mostramos el origen arriba
                if clave == "timestamp" and isinstance(valor, (int, float)):
                    tiempo = datetime.fromtimestamp(valor).strftime('%H:%M:%S')
                    print(f"     • {clave}: {valor} ({tiempo})")
                else:
                    print(f"     • {clave}: {valor}")
        
        print("=" * 70)
        
    except json.JSONDecodeError:
        print(f"[{SUBSCRIBER_ID}] MENSAJE RECIBIDO (formato no JSON):")
        print(f"  → Topic: {topic}")
        print(f"  → Contenido: {payload}")
    except Exception as e:
        print(f"[{SUBSCRIBER_ID}] Error al procesar mensaje: {e}")

def suscribir():
    # Crear cliente
    cliente = mqtt.Client(client_id=SUBSCRIBER_ID)
    cliente.on_connect = on_connect
    cliente.on_message = on_message
    
    # Conectar al broker
    print(f"[{SUBSCRIBER_ID}] Intentando conectar a {BROKER_ADDRESS}:{PORT}...")
    cliente.connect(BROKER_ADDRESS, PORT, 60)
    
    # Iniciar bucle de procesamiento de mensajes
    try:
        print(f"[{SUBSCRIBER_ID}] Suscriptor iniciado. Esperando mensajes...")
        print("-" * 70)
        cliente.loop_forever()
    except KeyboardInterrupt:
        print(f"\n[{SUBSCRIBER_ID}] Suscripción detenida por el usuario")
    finally:
        cliente.disconnect()
        print(f"[{SUBSCRIBER_ID}] Desconectado del broker")

if __name__ == "__main__":
    print("-" * 70)
    print(f"SUSCRIPTOR MQTT - ID: {SUBSCRIBER_ID}")
    print("-" * 70)
    suscribir()