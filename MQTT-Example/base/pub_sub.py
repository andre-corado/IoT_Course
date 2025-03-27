import paho.mqtt.client as mqtt
import time
import json
import random
import threading
import socket
import uuid
from datetime import datetime

# Configuración de conexión
BROKER_ADDRESS = "localhost"
PORT = 1883
TOPICS = ["test/1", "test/2"]

# Generar IDs únicos para publicador y suscriptor
PUB_ID = f"pub_{socket.gethostname()}_{uuid.uuid4().hex[:4]}"
SUB_ID = f"sub_{socket.gethostname()}_{uuid.uuid4().hex[:4]}"

# Formateo de salida en consola
class Colores:
    RESET = "\033[0m"
    ROJO = "\033[91m"
    VERDE = "\033[92m"
    AMARILLO = "\033[93m"
    AZUL = "\033[94m"
    MAGENTA = "\033[95m"
    CIAN = "\033[96m"

# Callbacks para el suscriptor
def on_connect_sub(client, userdata, flags, rc):
    print(f"{Colores.VERDE}[{SUB_ID}] Conectado al broker con código: {rc}{Colores.RESET}")
    if rc == 0:
        # Suscribirse a ambos temas
        for topic in TOPICS:
            client.subscribe(topic, qos=1)
            print(f"{Colores.VERDE}[{SUB_ID}] Suscrito al tema: {topic}{Colores.RESET}")
    else:
        print(f"{Colores.ROJO}[{SUB_ID}] Error de conexión, código: {rc}{Colores.RESET}")

def on_message(client, userdata, msg):
    # Obtener metadata del mensaje
    topic = msg.topic
    qos = msg.qos
    
    try:
        # Convertir el payload de bytes a string
        payload = msg.payload.decode("utf-8")
        
        # Interpretar el mensaje como JSON
        datos = json.loads(payload)
        
        # Obtener información de origen si está disponible
        origen = datos.get("source_id", "Desconocido")
        
        # Imprimir información detallada
        print(f"\n{Colores.VERDE}{'=' * 70}")
        print(f"[{SUB_ID}] MENSAJE RECIBIDO:")
        print(f"{'-' * 70}")
        print(f"  → Hora recepción: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        print(f"  → Topic: {topic}")
        print(f"  → QoS: {qos}")
        print(f"  → Origen: {origen}")
        print(f"{'-' * 70}")
        print(f"  → Contenido:")
        
        # Mostrar contenido formateado
        for clave, valor in datos.items():
            if clave != "source_id":  # Ya mostramos el origen arriba
                print(f"     • {clave}: {valor}")
        
        print(f"{'=' * 70}{Colores.RESET}")
        
    except json.JSONDecodeError:
        print(f"{Colores.ROJO}[{SUB_ID}] Mensaje recibido (formato no JSON):{Colores.RESET}")
        print(f"  → Topic: {topic}")
        print(f"  → Contenido: {payload}")
    except Exception as e:
        print(f"{Colores.ROJO}[{SUB_ID}] Error al procesar mensaje: {e}{Colores.RESET}")

# Callback para el publicador
def on_connect_pub(client, userdata, flags, rc):
    print(f"{Colores.AZUL}[{PUB_ID}] Conectado al broker con código: {rc}{Colores.RESET}")

def generar_datos_aleatorios():
    """Genera datos aleatorios para publicar en los temas"""
    mensaje_tipos = ["lectura", "estado", "alerta", "configuración", "diagnóstico"]
    tipo = random.choice(mensaje_tipos)
    
    datos_base = {
        "source_id": PUB_ID,
        "tipo": tipo,
        "timestamp": time.time(),
        "id_mensaje": uuid.uuid4().hex[:8]
    }
    
    if tipo == "lectura":
        datos_base.update({
            "sensor": f"sensor_{random.randint(1, 10)}",
            "valor": round(random.uniform(0, 100), 2),
            "unidad": random.choice(["°C", "%", "hPa", "lux", "V", "A"]),
        })
    elif tipo == "estado":
        datos_base.update({
            "dispositivo": f"disp_{random.randint(1, 5)}",
            "estado": random.choice(["on", "off", "standby", "error"]),
            "bateria": random.randint(0, 100),
        })
    elif tipo == "alerta":
        datos_base.update({
            "nivel": random.choice(["info", "advertencia", "error", "crítico"]),
            "codigo": f"ALT{random.randint(100, 999)}",
            "mensaje": random.choice([
                "Temperatura fuera de rango",
                "Señal débil",
                "Batería baja",
                "Dispositivo sin respuesta",
                "Actualización disponible"
            ])
        })
    
    return datos_base

def tarea_publicacion(cliente):
    """Función para ejecutar en un hilo separado para publicar mensajes"""
    try:
        print(f"{Colores.AZUL}[{PUB_ID}] Iniciando publicación de mensajes...{Colores.RESET}")
        mensaje_contador = 0
        
        while True:
            # Elegir un tema aleatorio de la lista
            topic = random.choice(TOPICS)
            mensaje_contador += 1
            
            # Generar datos aleatorios
            datos = generar_datos_aleatorios()
            mensaje = json.dumps(datos)
            
            # Mostrar información detallada en consola
            print(f"\n{Colores.AZUL}{'=' * 70}")
            print(f"[{PUB_ID}] ENVIANDO MENSAJE #{mensaje_contador}:")
            print(f"{'-' * 70}")
            print(f"  → Topic: {topic}")
            print(f"  → Hora envío: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
            print(f"  → Tipo: {datos['tipo']}")
            print(f"{'-' * 70}")
            print(f"  → Contenido completo: ")
            for k, v in datos.items():
                if k == "timestamp" and isinstance(v, (int, float)):
                    tiempo = datetime.fromtimestamp(v).strftime('%H:%M:%S')
                    print(f"     • {k}: {v} ({tiempo})")
                else:
                    print(f"     • {k}: {v}")
            print(f"{'=' * 70}{Colores.RESET}")
            
            # Publicar mensaje
            cliente.publish(topic, mensaje, qos=1)
            
            # Esperar un tiempo aleatorio entre publicaciones
            time.sleep(random.uniform(10.0, 20.0))
            
    except Exception as e:
        print(f"{Colores.ROJO}[{PUB_ID}] Error en la tarea de publicación: {e}{Colores.RESET}")

def iniciar_pub_sub():
    # Crear cliente suscriptor
    suscriptor = mqtt.Client(client_id=SUB_ID)
    suscriptor.on_connect = on_connect_sub
    suscriptor.on_message = on_message
    
    # Crear cliente publicador
    publicador = mqtt.Client(client_id=PUB_ID)
    publicador.on_connect = on_connect_pub
    
    try:
        # Conectar ambos clientes
        print(f"{Colores.VERDE}[{SUB_ID}] Conectando al broker MQTT...{Colores.RESET}")
        suscriptor.connect(BROKER_ADDRESS, PORT, 60)
        
        print(f"{Colores.AZUL}[{PUB_ID}] Conectando al broker MQTT...{Colores.RESET}")
        publicador.connect(BROKER_ADDRESS, PORT, 60)
        
        # Iniciar bucle de procesamiento para ambos clientes
        suscriptor.loop_start()
        publicador.loop_start()
        
        # Esperar un momento para que se establezcan las conexiones
        time.sleep(1)
        
        # Iniciar hilo para publicación
        hilo_pub = threading.Thread(target=tarea_publicacion, args=(publicador,))
        hilo_pub.daemon = True
        hilo_pub.start()
        
        print(f"\n{Colores.CIAN}[INFO] Publicador y Suscriptor iniciados.")
        print(f"[INFO] Presiona Ctrl+C para detener...{Colores.RESET}\n")
        
        # Mantener el programa corriendo
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print(f"\n{Colores.AMARILLO}[INFO] Programa detenido por el usuario{Colores.RESET}")
    except Exception as e:
        print(f"{Colores.ROJO}[ERROR] {e}{Colores.RESET}")
    finally:
        # Detener y desconectar ambos clientes
        suscriptor.loop_stop()
        publicador.loop_stop()
        suscriptor.disconnect()
        publicador.disconnect()
        print(f"{Colores.AMARILLO}[INFO] Clientes desconectados{Colores.RESET}")

if __name__ == "__main__":
    print(f"\n{Colores.CIAN}{'=' * 70}")
    print(f"CLIENTE MQTT PUBLICADOR/SUSCRIPTOR")
    print(f"{'=' * 70}")
    print(f"Publicador ID: {PUB_ID}")
    print(f"Suscriptor ID: {SUB_ID}")
    print(f"Broker: {BROKER_ADDRESS}:{PORT}")
    print(f"Topics: {', '.join(TOPICS)}")
    print(f"{'=' * 70}{Colores.RESET}\n")
    
    iniciar_pub_sub()