import { useEffect, useState } from "react";
import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import WeatherGraph from './Graph.js';
import WeatherAlertsTable from "./Alerts.js"
import logo from "./BH.png"; // Caminho para a imagem local


function WeatherData() {
  const [weatherData, setWeatherData] = useState([]);

  // Função para buscar dados da API
  const fetchWeatherData = () => {
    fetch("http://127.0.0.1:5000/weather") // URL do backend
      .then((response) => response.json())
      .then((data) => setWeatherData(data))
      .catch((error) => console.error("Erro ao buscar dados:", error));
  };

  useEffect(() => {
    fetchWeatherData(); // Busca inicial dos dados
    // Configura o intervalo para atualizar a cada 3 minutos (180.000ms)
    const intervalId = setInterval(() => {
      fetchWeatherData();
    }, 180000);
    // Limpa o intervalo quando o componente é desmontado
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="main">
      <div className="content-group">
         <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous"></link>
     <div className="head"> 
     <h1>Dados Meteorológicos BH </h1>
      <div className="logo">
         <img src={logo} alt="Logo" />
         </div>
     </div>
      <h2 className="title-table"> Temperatura e Umidade atual</h2>
      <div className="data-table" > 
      <table className="table table-hover table-sm">
        <thead>
          <tr>
            <th>Sensor </th>
            <th>Valores Lidos</th>
            <th>Momento de Lançamento</th>
          </tr>
        </thead>
        <tbody>
          {weatherData.map((item) => (
            <tr key={item.id}>
              <td>{item.sensor_id}</td>
              <td>{item.value}</td>
              <td>{new Date(item.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
         </div>
         <div className="graph">
          <WeatherGraph/>
         </div>
         </div>
         <div className="alerts-table"> <WeatherAlertsTable/></div>
         <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossOrigin="anonymous"></script>
    </div>
  );
}

export default WeatherData;
