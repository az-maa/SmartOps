// src/pages/Predictions.jsx
import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Loading from '../components/common/Loading';

// Week 1: Import mockApi
import { mockApi as api } from '../services/mockApi';
// Week 2: Uncomment this line and comment the line above
// import api from '../services/api';

const Predictions = () => {
  const [servers, setServers] = useState([]);
  const [selectedServer, setSelectedServer] = useState('');
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadServers = async () => {
      try {
        const data = await api.getServers();
        setServers(data);
        if (data.length > 0) {
          setSelectedServer(data[0].id);
        }
      } catch (error) {
        console.error('Error loading servers:', error);
      } finally {
        setLoading(false);
      }
    };

    loadServers();
  }, []);

  useEffect(() => {
    if (selectedServer) {
      loadPredictions();
    }
  }, [selectedServer]);

  const loadPredictions = async () => {
    try {
      const data = await api.getPredictions(selectedServer);
      setPredictions(data);
    } catch (error) {
      console.error('Error loading predictions:', error);
    }
  };

  if (loading) {
    return <Loading text="Loading predictions..." />;
  }

  const forecastData = predictions?.forecast?.map((item, index) => ({
    time: `${index} min`,
    predicted: parseFloat(item.predicted_value?.toFixed(1) || 0),
    upper: parseFloat(item.upper_bound?.toFixed(1) || 0),
    lower: parseFloat(item.lower_bound?.toFixed(1) || 0)
  })) || [];

  const selectedServerData = servers.find(s => s.id === selectedServer);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">CPU Predictions</h2>
          <p className="text-gray-600 mt-1">AI-powered forecasting for the next 30 minutes</p>
        </div>
        <select 
          value={selectedServer}
          onChange={(e) => setSelectedServer(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          {servers.map(server => (
            <option key={server.id} value={server.id}>
              {server.name}
            </option>
          ))}
        </select>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">30-Minute Forecast</h3>
          {selectedServerData && (
            <div className="text-sm text-gray-600">
              Current: <span className="font-bold">{selectedServerData.cpu?.toFixed(1)}%</span>
            </div>
          )}
        </div>

        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={forecastData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="time" 
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
              domain={[0, 100]}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#fff', 
                border: '1px solid #e5e7eb',
                borderRadius: '6px'
              }}
            />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="upper" 
              stackId="1" 
              stroke="#93c5fd" 
              fill="#dbeafe" 
              name="Upper Bound" 
            />
            <Area 
              type="monotone" 
              dataKey="predicted" 
              stackId="2" 
              stroke="#3b82f6" 
              fill="#60a5fa" 
              name="Predicted" 
            />
            <Area 
              type="monotone" 
              dataKey="lower" 
              stackId="3" 
              stroke="#1e40af" 
              fill="#3b82f6" 
              name="Lower Bound" 
            />
          </AreaChart>
        </ResponsiveContainer>
        
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2">
            📊 AI Analysis
          </h4>
          <p className="text-sm text-gray-700">
            Based on historical patterns, CPU usage is expected to remain stable with slight variations. 
            Peak usage predicted around minute 15-20. The confidence interval shows possible range of values.
            No critical anomalies forecasted for the next 30 minutes.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Predictions;