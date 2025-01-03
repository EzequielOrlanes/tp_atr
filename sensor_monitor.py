import paho.mqtt.client as mqtt
import threading
import time
import json
import os
from datetime import datetime
import psutil

# Constantes
BROKER_ADDRESS = "localhost"
QOS = 1

# Funções auxiliares
def get_available_memory():
    mem = psutil.virtual_memory()
    return mem.available // 1024  # Retorna em KB

def get_active_memory():
    mem = psutil.virtual_memory()
    return (mem.total - mem.available) // 1024  # Retorna em KB

def calculate_cpu_usage():
    return psutil.cpu_percent(interval=1)

def publish_initial_message(client, machine_id, freq_init_msg, sensors):
    while True:
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        init_message = {
            "machine_id": machine_id,
            "sensors": sensors
        }
        client.publish("/sensor_monitors", json.dumps(init_message), qos=QOS)
        print(f"[INFO] Initial message published: {init_message}")
        time.sleep(freq_init_msg / 1000)

def read_and_publish(client, machine_id, sensor_id, freq, value_func):
    while True:
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        value = value_func()
        message = {
            "timestamp": now,
            "value": value
        }
        topic = f"/sensors/{machine_id}/{sensor_id}"
        client.publish(topic, json.dumps(message), qos=QOS)
        print(f"[INFO] Published to {topic}: {message}")
        time.sleep(freq / 1000)

def main():
    # Frequências em milissegundos
    freq_sensor_ava_mem = 1000
    freq_sensor_act_mem = 1000
    freq_sensor_cpu_use = 1000
    freq_init_msg = 5000

    # Identificadores dos sensores
    machine_id = "ezequiel"
    id_sensor_ava_mem = "available_memory"
    id_sensor_act_mem = "active_memory"
    id_sensor_cpu_use = "cpu_usage"

    sensors = [
        {"sensor_id": id_sensor_ava_mem, "data_type": "double", "data_interval": freq_sensor_ava_mem},
        {"sensor_id": id_sensor_act_mem, "data_type": "double", "data_interval": freq_sensor_act_mem},
        {"sensor_id": id_sensor_cpu_use, "data_type": "double", "data_interval": freq_sensor_cpu_use}
    ]

    # Configuração do cliente MQTT
    client = mqtt.Client()
    client.connect(BROKER_ADDRESS)
    client.loop_start()

    # Threads para leitura e publicação
    threading.Thread(target=publish_initial_message, args=(client, machine_id, freq_init_msg, sensors)).start()
    threading.Thread(target=read_and_publish, args=(client, machine_id, id_sensor_ava_mem, freq_sensor_ava_mem, get_available_memory)).start()
    threading.Thread(target=read_and_publish, args=(client, machine_id, id_sensor_act_mem, freq_sensor_act_mem, get_active_memory)).start()
    threading.Thread(target=read_and_publish, args=(client, machine_id, id_sensor_cpu_use, freq_sensor_cpu_use, calculate_cpu_usage)).start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
