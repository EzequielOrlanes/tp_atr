# data_processor.py
import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime
import threading
import sqlite3
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
# Constantes
BROKER_ADDRESS = "localhost"
QOS = 1
DB_NAME = "weather_data.db"

# Limites para alertas
TEMPERATURE_HIGH = 35.0
TEMPERATURE_LOW = 5.0
HUMIDITY_LOW = 20.0
TEMPERATURE_IDEAL_MAX = 28.0
TEMPERATURE_IDEAL_MIN = 20.0

# Variáveis de controle
time_last_message = None
INACTIVITY_THRESHOLD = 30 # Segundos

# Configuração do banco de dados
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT,
            value REAL,
            timestamp TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue TEXT,
            value REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_database(table, data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if table == "weather":
        cursor.execute("""
            INSERT INTO weather (sensor_id, value, timestamp)
            VALUES (?, ?, ?)
        """, (data["sensor_id"], data["value"], data["timestamp"]))
    elif table == "alerts":
        cursor.execute("""
            INSERT INTO alerts (issue, value, timestamp)
            VALUES (?, ?, ?)
        """, (data["issue"], data["value"], data["timestamp"]))
    conn.commit()
    conn.close()

def delete_old_records(conn, table):
    cursor = conn.cursor()
    # Calcular o timestamp limite (2 horas atrás)
    two_hours_ago = datetime.utcnow() - timedelta(hours=2)
    timestamp_limit = two_hours_ago.strftime("%Y-%m-%d %H:%M:%S")  # Formato padrão para SQLite
    # Excluir registros antigos
    query = f"DELETE FROM {table} WHERE timestamp < ?"
    cursor.execute(query, (timestamp_limit,))
    conn.commit()

def post_alert(client, alert_message):
    try:
        client.publish("/alerts", json.dumps(alert_message), qos=QOS)
        print(f"[ALERT] Published: {alert_message}")
        save_to_database("alerts", alert_message)
    except Exception as e:
        print(f"Erro ao publicar alerta: {e}")

# Callback para mensagens MQTT
def on_message(client, userdata, msg):
    global time_last_message
    payload = json.loads(msg.payload.decode('utf-8'))
    topic_parts = msg.topic.split('/')
    machine_id, sensor_id = topic_parts[2], topic_parts[3]
    timestamp, value = payload["timestamp"], payload["value"]

    # Atualiza o tempo da última mensagem recebida
    time_last_message = time.time()
    
    # Salva os dados no banco de dados
    save_to_database("weather", {"sensor_id": sensor_id, "value": value, "timestamp": timestamp})
    print(f"sensor_id: {sensor_id}, value: {value}, timestamp: {timestamp}")
    #Temperatura Ideal
    if sensor_id == "temperature":
        if value < TEMPERATURE_IDEAL_MAX or value > TEMPERATURE_IDEAL_MIN:
            alert_message = {
                "sensor": sensor_id,
                "issue": "Temperatura e Umidade em níveis saudáveis a sua saúde.",
                "value": value,
                "timestamp": timestamp
            }
            post_alert(client, alert_message)
             
    # Detecta outliers de temperatura e umidade
    if sensor_id == "temperature":
        if value > TEMPERATURE_HIGH or value < TEMPERATURE_LOW:
            alert_message = {
                "sensor": sensor_id,
                "issue": "[PERIGO] Temperatura acima do limite considerado saudável pela OMS.",
                "value": value,
                "timestamp": timestamp
            }
            post_alert(client, alert_message)
    elif sensor_id == "humidity":
        if value < HUMIDITY_LOW:
            alert_message = {
                "sensor": sensor_id,
                "issue": "[PERIGO] Umidade abaixo do teor considerado saudável pela OMS.",
                "value": value,
                "timestamp": timestamp
            }
            post_alert(client, alert_message)

def check_inactivity(client):
    global time_last_message
    while True:
        if time_last_message:
            elapsed_time = time.time() - time_last_message
            if elapsed_time > INACTIVITY_THRESHOLD:
                alert_message = {
                    "issue": "[PERIGO] Inatividade detectada, os dados não estou atualizados e não são confiaveis",
                    "elapsed_time": elapsed_time
                }
                post_alert(client, alert_message)
        time.sleep(5)

def main():
    # Configura o banco de dados
    setup_database()
    # Criar cliente MQTT com protocolo MQTTv5
    client = mqtt.Client(protocol=mqtt.MQTTv5)
    # Configurar callback para mensagens
    client.message_callback_add("/sensors/#", on_message)
    # Conectar ao broker
    client.connect(BROKER_ADDRESS)
    # Inscrever-se em tópicos
    client.subscribe("/sensors/#", qos=QOS)
    # Iniciar thread para detectar inatividade
    threading.Thread(target=check_inactivity, args=(client,), daemon=True).start()
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
