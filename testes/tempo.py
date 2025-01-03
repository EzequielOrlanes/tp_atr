import requests
import sqlite3
import plotly.express as px
from datetime import datetime

# Configurações da API e Banco de Dados
API_KEY = "9fd640733f7c425e87b225654250201"  # Substitua pela sua chave da Weather API
BASE_URL = "http://api.weatherapi.com/v1/current.json"
CITY = "São Paulo"
DB_NAME = "weather_data.db"

# Função para buscar dados da API
def fetch_weather_data(city):
    params = {
        "key": API_KEY,
        "q": city,
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "city": data["location"]["name"],
            "region": data["location"]["region"],
            "country": data["location"]["country"],
            "temperature_c": data["current"]["temp_c"],
            "humidity": data["current"]["humidity"],
            "wind_kph": data["current"]["wind_kph"],
            "last_updated": data["current"]["last_updated"]
        }
    else:
        print(f"Erro ao buscar dados: {response.status_code}")
        return None

# Função para configurar o banco de dados
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            region TEXT,
            country TEXT,
            temperature_c REAL,
            humidity INTEGER,
            wind_kph REAL,
            last_updated TEXT
        )
    """)
    conn.commit()
    conn.close()

# Função para salvar os dados no banco de dados
def save_to_database(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO weather (city, region, country, temperature_c, humidity, wind_kph, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (data["city"], data["region"], data["country"], data["temperature_c"], data["humidity"], data["wind_kph"], data["last_updated"]))
    conn.commit()
    conn.close()

# Função para visualizar os dados com Plotly
def visualize_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT city, temperature_c, humidity, wind_kph, last_updated FROM weather")
    rows = cursor.fetchall()
    conn.close()

    if rows:
        # Converte os dados para um DataFrame
        import pandas as pd
        df = pd.DataFrame(rows, columns=["City", "Temperature (C)", "Humidity", "Wind Speed (kph)", "Last Updated"])

        # Cria um gráfico interativo com Plotly
        fig = px.line(df, x="Last Updated", y="Temperature (C)", title="Temperature Over Time", markers=True)
        fig.show()
    else:
        print("Nenhum dado disponível para visualização.")

if __name__ == "__main__":
    setup_database()

    # Obtém dados da API e salva no banco
    weather_data = fetch_weather_data(CITY)
    if weather_data:
        save_to_database(weather_data)
        print(f"Dados salvos com sucesso: {weather_data}")

    # Visualiza os dados
    visualize_data()
