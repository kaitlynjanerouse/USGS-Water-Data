import React, { useEffect, useState } from 'react';

function App() {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('https://usgs-water-anomaly-backend-a96b06d0f571.herokuapp.com/anomalies')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch');
        return res.json();
      })
      .then((data) => {
        console.log('Anomalies from backend:', data);
        setAnomalies(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading anomalies...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div style={{ padding: 20 }}>
      <h1>Water Level Anomalies</h1>
      {anomalies.length === 0 && <p>No anomalies found.</p>}
      <ul>
        {anomalies.map((a) => (
          <li key={a.site_id + a.timestamp}>
            <strong>{a.direction}</strong> at site <em>{a.site_name}</em> ({a.site_id}) on {a.timestamp}: {a.prev_value} → {a.curr_value}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;