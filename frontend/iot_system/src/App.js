import { useEffect, useState } from "react";
import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import WeatherGraph from './Graph.js';

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function WeatherData() {
  const [weatherData, setWeatherData] = useState([]);
  useEffect(() => {
    fetch("http://127.0.0.1:5000/weather") // URL do backend
      .then((response) => response.json())
      .then((data) => setWeatherData(data))
      .catch((error) => console.error("Erro ao buscar dados:", error));
  }, []);

  return (
    <div className="main">
         <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous"></link>
    {/* <img id="logo" src="frontend\iot_system\public\BH.png" alt="The logo of app" ></img> */}
      <h1 className="title">Dados Meteorológicos BH </h1>
      <div className="data" > 
      <table className="table table-dark table-hover table-sm">
        <thead>
          <tr>
            <th>ID</th>
            <th>Sensor</th>
            <th>Valor</th>
            <th>Momento de Lançamento</th>
          </tr>
        </thead>
        <tbody>
          {weatherData.map((item) => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td>{item.sensor_id}</td>
              <td>{item.value}</td>
              <td>{item.timestamp}</td>
            </tr>
          ))}
        </tbody>
      </table>
         </div>
         <div className="graph">          <WeatherGraph/>
         </div>
         <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossOrigin="anonymous"></script>

    </div>
  );
}

export default WeatherData;
