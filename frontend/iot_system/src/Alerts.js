import React, { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";


const WeatherAlertsTable = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch data from the API
    const fetchData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/weather_alerts"); // Replace with the correct API endpoint
        setAlerts(response.data);
      } catch (err) {
        setError("Failed to fetch alerts.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="p-4">
      <h2 className="title-table">Alertas</h2>
      <table className="table-auto w-full border-collapse border border-gray-300">
        <thead>
          <tr className="bg-gray-100">
            <th className="border border-gray-300 px-4 py-2">Alerta a População</th>
            <th className="border border-gray-300 px-4 py-2">Ultima Atualização</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert) => (
            <tr key={alert.id}>
            <td className="border border-gray-300 px-4 py-2 text-green-500" style={{ color:'green' }}>{alert.issue}</td>
              <td className="border border-gray-300 px-4 py-2">{new Date(alert.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default WeatherAlertsTable;
