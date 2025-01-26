
# sensor_monitor.py
import paho.mqtt.client as mqtt
import threading
import time
import json
from datetime import datetime
import requests

# Constantes
BROKER_ADDRESS = "localhost"
QOS = 1

# Configurações da API de tempo
API_KEY = "9fd640733f7c425e87b225654250201"  # Substitua pela sua chave da Weather API
BASE_URL = "http://api.weatherapi.com/v1/current.json"
CITY = "Belo Horizonte"

# Função para buscar dados da API de tempo
def fetch_weather_data(city):
    params = {
        "key": API_KEY,
        "q": city,
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature_c": data["current"]["temp_c"],
            "humidity": data["current"]["humidity"],
            "last_updated": data["current"]["last_updated"]
        }
    else:
        print(f"Erro ao buscar dados: {response.status_code}")
        return None

# Publicação inicial dos sensores
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

# Leitura e publicação de dados meteorológicos
def read_and_publish_weather(client, machine_id, freq):
    while True:
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        weather_data = fetch_weather_data(CITY)
        if weather_data:
            temperature_message = {
                "timestamp": now,
                "value": weather_data["temperature_c"]
            }
            humidity_message = {
                "timestamp": now,
                "value": weather_data["humidity"]
            }
            client.publish(f"/sensors/{machine_id}/temperature", json.dumps(temperature_message), qos=QOS)
            client.publish(f"/sensors/{machine_id}/humidity", json.dumps(humidity_message), qos=QOS)
            print(f"[INFO] Published temperature and humidity: {temperature_message}, {humidity_message}")
        time.sleep(freq / 1000)

def main():
    # Frequência em milissegundos
    freq_weather_data = 10000  # 10 segundos
    freq_init_msg = 5000  # 5 segundos

    # Identificadores dos sensores
    machine_id = "weather_station"
    sensors = [
        {"sensor_id": "temperature", "data_type": "double", "data_interval": freq_weather_data},
        {"sensor_id": "humidity", "data_type": "double", "data_interval": freq_weather_data}
    ]

    # Configuração do cliente MQTT
    client = mqtt.Client()
    client.connect(BROKER_ADDRESS)
    client.loop_start()

    # Threads para publicação
    threading.Thread(target=publish_initial_message, args=(client, machine_id, freq_init_msg, sensors)).start()
    threading.Thread(target=read_and_publish_weather, args=(client, machine_id, freq_weather_data)).start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
