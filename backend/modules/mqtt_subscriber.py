import paho.mqtt.client as mqtt
import time

# Configuração
SERVER_ADDRESS = "localhost"
CLIENT_ID = "ExampleSubscriber"
TOPIC = "test/topic"

# Callback para mensagens recebidas
def on_message(client, userdata, msg):
    print(f"Mensagem recebida: {msg.payload.decode('utf-8')}")

def main():
    # Inicializa o cliente MQTT
    client = mqtt.Client(CLIENT_ID)

    # Configura o callback para mensagens
    client.on_message = on_message

    # Conecta ao broker
    client.connect(SERVER_ADDRESS)

    # Inscreve-se no tópico
    client.subscribe(TOPIC, qos=1)

    # Inicia o loop para aguardar mensagens
    client.loop_start()

    try:
        # Aguarda por mensagens por 60 segundos
        time.sleep(60)
    finally:
        # Para o loop e desconecta
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
