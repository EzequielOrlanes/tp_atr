from flask import Flask, jsonify, send_file
from flask_cors import CORS
import sqlite3
import matplotlib.pyplot as plt
import io

app = Flask(__name__)
CORS(app)  # Adicione esta linha para permitir todas as origens

DB_NAME = "weather_data.db"


@app.route('/weather_alerts', methods=['GET'])
def get_weather_alerts():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, issue, value, timestamp FROM alerts ORDER BY timestamp DESC LIMIT 1")
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
            return jsonify({"error": str(e)}), 500
    data = [
            {"id": row[0], "issue": row[1], "value": row[2], "timestamp": row[3]}
            for row in rows
        ]
    print((data))
    return jsonify(data)
        
@app.route('/weather', methods=['GET'])
def get_weather_data():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, sensor_id, value, timestamp FROM weather ORDER BY timestamp DESC LIMIT 2")
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    data = [
        {"id": row[0], "sensor_id": row[1], "value": row[2], "timestamp": row[3]}
        for row in rows
    ]
    print((data))
    return jsonify(data)

@app.route('/weather_graph', methods=['GET'])
def get_weather_data_to_graph():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Selecionando os dados para o gráfico de temperatura
    cursor.execute("SELECT timestamp, value FROM weather WHERE sensor_id = 'temperature' ORDER BY timestamp DESC LIMIT 16")
    temp_rows = cursor.fetchall()
    # Selecionando os dados para o gráfico de umidade
    cursor.execute("SELECT timestamp, value FROM weather WHERE sensor_id = 'humidity' ORDER BY timestamp DESC LIMIT 16")
    humidity_rows = cursor.fetchall()
    conn.close()
    # Organizando os dados para exibição
    temperature_data = [
        {"timestamp": row[0], "value": row[1]} for row in temp_rows
    ]
    humidity_data = [
        {"timestamp": row[0], "value": row[1]} for row in humidity_rows
    ]
    
    # Gerando os gráficos e retornando as imagens
    return generate_graphs(temperature_data, humidity_data)

def generate_graphs(temp_data, humidity_data):
    # Preparando os dados para o gráfico de temperatura
    temp_timestamps = [entry['timestamp'] for entry in temp_data]
    temp_values = [entry['value'] for entry in temp_data]
    
    # Preparando os dados para o gráfico de umidade
    humidity_timestamps = [entry['timestamp'] for entry in humidity_data]
    humidity_values = [entry['value'] for entry in humidity_data]
    
    # Criando o gráfico de temperatura
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

    # Gráfico de temperatura
    ax1.plot( temp_values, marker='o', linestyle='-', color='r')
    ax1.set_title("Sensor de Temperatura")
    ax1.set_xlabel("Pontos de Coleta")
    ax1.set_ylabel("Temperatura (°C)")
    ax1.tick_params(axis='x', rotation=45)
    # Gráfico de umidade
    ax2.plot(humidity_values, marker='o', linestyle='-', color='b')
    ax2.set_title("Sensor de Umidade")
    ax2.set_xlabel("Pontos de Coleta")
    ax2.set_ylabel("Umidade (%)")
    ax2.tick_params(axis='x', rotation=45)
    # Ajustando o layout
    plt.tight_layout()
    # Salvando a imagem em um objeto de memória
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    
    # Retorna a imagem diretamente
    return send_file(img, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)