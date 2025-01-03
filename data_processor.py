import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime
import threading
import warnings
import socket
from typing import List

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Constantes
BROKER_ADDRESS = "localhost"
GRAPHITE_HOST = "graphite"
GRAPHITE_PORT = 2003
QOS = 1
WINDOW_SIZE_FOR_AV = 30

# Variáveis globais
last_measures_ava_mem = [0] * WINDOW_SIZE_FOR_AV
index_circ_buffer = 0
init_config_ok = False
sensor_ids = ["sensor1", "sensor2", "sensor3"]
frequencies = [0, 0, 0]
last_timestamps = [None, None, None]
sensors_inactive = [False, False, False]
mutex_send = threading.Lock()
mutex_vec = threading.Lock()

def iso8601_to_unix(timestamp_iso8601):
    try:
        dt = datetime.strptime(timestamp_iso8601, "%Y-%m-%dT%H:%M:%SZ")
        print("Funcionando")
        return int(dt.timestamp())
    except ValueError:
        print("Erro ao converter timestamp ISO 8601.")
        return None

def post_metric(machine_id, sensor_id, timestamp_str, value):
    try:
        with socket.create_connection((GRAPHITE_HOST, GRAPHITE_PORT)) as sock:
            data = f"{machine_id}.{sensor_id} {value} {iso8601_to_unix(timestamp_str)}\n"
            with mutex_send:
                sock.sendall(data.encode('utf-8'))
                print("Funcionando")
    except Exception as e:
        print(f"Erro ao enviar métricas: {e}")

def post_inactivity_alarms(machine_id, timestamp_str):
    try:
        with socket.create_connection((GRAPHITE_HOST, GRAPHITE_PORT)) as sock:
            with mutex_send:
                for i, sensor_id in enumerate(sensor_ids):
                    data = f"{machine_id}.alarms.inactivity.{sensor_id} {int(sensors_inactive[i])} {iso8601_to_unix(timestamp_str)}\n"
                    sock.sendall(data.encode('utf-8'))
                    print("Funcionando")
    except Exception as e:
        print(f"Erro ao enviar alarmes de inatividade: {e}")

def post_moving_av(machine_id, timestamp_str, moving_av):
    try:
        with socket.create_connection((GRAPHITE_HOST, GRAPHITE_PORT)) as sock:
            with mutex_send:
                data = f"{machine_id}.moving_av {moving_av} {iso8601_to_unix(timestamp_str)}\n"
                sock.sendall(data.encode('utf-8'))
                print("Funcionando")
    except Exception as e:
        print(f"Erro ao enviar média móvel: {e}")

def check_inactivity(machine_id):
    global sensors_inactive
    while True:
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        for i in range(3):
            if last_timestamps[i]:
                diff = (datetime.utcnow() - last_timestamps[i]).total_seconds() * 1000
                if diff >= 10 * frequencies[i] and not sensors_inactive[i]:
                    sensors_inactive[i] = True
                elif diff < 10 * frequencies[i] and sensors_inactive[i]:
                    sensors_inactive[i] = False
        post_inactivity_alarms(machine_id, now)
        time.sleep(1)

def calculate_moving_av(machine_id):
    global index_circ_buffer
    while True:
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        with mutex_vec:
            moving_av = sum(last_measures_ava_mem) // WINDOW_SIZE_FOR_AV
        post_moving_av(machine_id, now, moving_av)
        time.sleep(frequencies[0] / 1000)

def on_message(client, userdata, msg):
    global init_config_ok, last_measures_ava_mem, index_circ_buffer
    payload = json.loads(msg.payload.decode('utf-8'))
    if msg.topic == "/sensor_monitors" and not init_config_ok:
        machine_id = payload["machine_id"]
        for i, sensor in enumerate(payload["sensors"]):
            sensor_ids[i] = sensor["sensor_id"]
            frequencies[i] = sensor["data_interval"]
        for i in range(3):
            last_timestamps[i] = datetime.utcnow()
        threading.Thread(target=check_inactivity, args=(machine_id,)).start()
        threading.Thread(target=calculate_moving_av, args=(machine_id,)).start()
        init_config_ok = True
    else:
        topic_parts = msg.topic.split('/')
        machine_id, sensor_id = topic_parts[2], topic_parts[3]
        timestamp, value = payload["timestamp"], payload["value"]
        if sensor_id == sensor_ids[0]:
            last_timestamps[0] = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
            with mutex_vec:
                last_measures_ava_mem[index_circ_buffer] = value
                index_circ_buffer = (index_circ_buffer + 1) % WINDOW_SIZE_FOR_AV
        post_metric(machine_id, sensor_id, timestamp, value)

def main():
     # Criar cliente MQTT com protocolo MQTTv5
    client = mqtt.Client(protocol=mqtt.MQTTv5)
    # Configurar callback para mensagens
    client.message_callback_add("/sensor_monitors", on_message)
    # Conectar ao broker
    client.connect(BROKER_ADDRESS)
    # Inscrever-se em tópicos
    client.subscribe("/sensor_monitors", qos=QOS)
    # Iniciar o loop
    client.loop_start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
