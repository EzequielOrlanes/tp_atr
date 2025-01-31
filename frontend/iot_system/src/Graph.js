import React, { useEffect, useState } from 'react';
import axios from 'axios';
<th className="border border-gray-300 px-4 py-2">Alerta a População</th>


function WeatherGraph() {
  const [imageUrl, setImageUrl] = useState(null);
  useEffect(() => {
    // Função para buscar o gráfico do backend
    const fetchWeatherGraph = async () => {
      try {
        // Fazendo a requisição para o backend Flask
        const response = await axios.get('http://localhost:5000/weather_graph', { responseType: 'blob' });
        // Cria uma URL temporária para o blob da imagem
        const imageObjectURL = URL.createObjectURL(response.data);
        // Atualiza o estado com a URL da imagem
        setImageUrl(imageObjectURL);
      } catch (error) {
        console.error('Erro ao carregar o gráfico:', error);
      }
    };
    // Chama a função assim que o componente for montado
    fetchWeatherGraph();
  }, []);

  return (
    <div>
      <h2 className='title-table'>Gráfico de Clima</h2>
      {imageUrl ? (
        <img src={imageUrl} alt="Gráfico de Clima" width="600vw" height="600vh" />
      ) : (
        <p> Carregando gráfico... </p>
      )}
    </div>
  );
}

export default WeatherGraph;
