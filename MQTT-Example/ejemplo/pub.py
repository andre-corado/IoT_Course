import paho.mqtt.client as mqtt
import time
import json
import random


# Configuración de conexión
BROKER_ADDRESS = "localhost"
PORT = 1883
TOPIC_TEMPERATURA = "temperatura"
TOPIC_HUMEDAD = "humedad"

def on_connect(client, userdata, flags, rc):
    print(f"Conectado al broker con código: {rc}")

def publicar_datos():
    # Crear cliente
    cliente = mqtt.Client()
    cliente.on_connect = on_connect
    
    # Conectar al broker
    print(f"Conectando al broker MQTT en {BROKER_ADDRESS}:{PORT}...")
    cliente.connect(BROKER_ADDRESS, PORT, 60)
    cliente.loop_start()
    
    try:
        print("Iniciando publicación de datos de temperatura y humedad...")
        print("Presiona Ctrl+C para detener")
        print("-" * 50)
        
        while True:
            # Generar datos de temperatura (entre 18°C y 32°C)
            temperatura = round(random.uniform(18.0, 32.0), 1)
            datos_temperatura = {
                "valor": temperatura,
                "ubicacion": "Sala principal",
                "estado": "Normal" if 25 <= temperatura <= 32 else "Alerta",
                "timestamp": time.time()
            }
            
            # Generar datos de humedad (entre 30% y 80%)
            humedad = round(random.uniform(30.0, 80.0), 1)
            datos_humedad = {
                "valor": humedad,
                "ubicacion": "Sala principal",
                "estado": "Normal" if 40 <= humedad <= 60 else "Alerta",
                "timestamp": time.time()
            }
            
            # Publicar temperatura
            mensaje_temperatura = json.dumps(datos_temperatura)
            cliente.publish(TOPIC_TEMPERATURA, mensaje_temperatura)
            print(f"Temperatura publicada: {temperatura}°C - Estado: {datos_temperatura['estado']}")
            
            # Publicar humedad
            mensaje_humedad = json.dumps(datos_humedad)
            cliente.publish(TOPIC_HUMEDAD, mensaje_humedad)
            print(f"Humedad publicada: {humedad}% - Estado: {datos_humedad['estado']}")
            
            print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 50)
            
            # Esperar 5 segundos
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nPublicación detenida por el usuario")
    finally:
        cliente.loop_stop()
        cliente.disconnect()
        print("Desconectado del broker")

if __name__ == "__main__":
    publicar_datos()