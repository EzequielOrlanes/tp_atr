import paho.mqtt.client as mqtt
import time

# Configuração
BROKER_ADDRESS = "localhost"
CLIENT_ID = "ExampleClient"

def main():
    # Inicializa o cliente MQTT
    client = mqtt.Client(CLIENT_ID)

    # Conecta ao broker
    client.connect(BROKER_ADDRESS)
    client.loop_start()

    # Publica uma mensagem
    topic = "test/topic"
    message = "Hello, MQTT!"
    client.publish(topic, message, qos=1)
    print(f"[INFO] Published message to {topic}: {message}")

    # Aguarda antes de desconectar
    time.sleep(2)

    # Desconecta
    client.loop_stop()
    client.disconnect()
    print("[INFO] Disconnected from broker")

if __name__ == "__main__":
    main()
