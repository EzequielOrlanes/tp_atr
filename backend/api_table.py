from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Adicione esta linha para permitir todas as origens

DB_NAME = "weather_data.db"

@app.route('/weather', methods=['GET'])
def get_weather_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, sensor_id, value, timestamp FROM weather ORDER BY timestamp DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()

    data = [
        {"id": row[0], "sensor_id": row[1], "value": row[2], "timestamp": row[3]}
        for row in rows
    ]
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
