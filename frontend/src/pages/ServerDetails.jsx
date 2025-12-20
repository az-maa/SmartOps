// src/pages/ServerDetails.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Activity } from 'lucide-react';
import MetricsChart from '../components/dashboard/MetricsChart';
import AnomalyAlert from '../components/dashboard/AnomalyAlert';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';

// Week 1: Import mockApi
import { mockApi as api } from '../services/mockApi';
// Week 2: Uncomment this line and comment the line above
// import api from '../services/api';

const ServerDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [server, setServer] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadServerData = async () => {
      try {
        const [serverData, metricsData, anomaliesData] = await Promise.all([
          api.getServerById(id),
          api.getMetrics(id),
          api.getAnomalies(id)
        ]);

        setServer(serverData);
        setMetrics(metricsData);
        setAnomalies(anomaliesData);
      } catch (error) {
        console.error('Error loading server details:', error);
      } finally {
        setLoading(false);
      }
    };

    loadServerData();
  }, [id]);

  if (loading) {
    return <Loading text="Loading server details..." />;
  }

  if (!server) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Server not found</p>
        <Button className="mt-4" onClick={() => navigate('/servers')}>
          Back to Servers
        </Button>
      </div>
    );
  }

  const formatCpuData = metrics?.cpu.slice(-50).map((item, index) => ({
    time: new Date(item.time).toLocaleTimeString(),
    value: item.value
  })) || [];

  const formatRamData = metrics?.ram.slice(-50).map((item, index) => ({
    time: new Date(item.time).toLocaleTimeString(),
    value: item.value
  })) || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button 
          variant="secondary"
          onClick={() => navigate('/servers')}
        >
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{server.name}</h2>
          <p className="text-gray-600">{server.ip}</p>
        </div>
      </div>

      {/* Server Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <p className="text-sm text-gray-600 mb-1">Status</p>
          <p className="text-xl font-bold capitalize">{server.status}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <p className="text-sm text-gray-600 mb-1">CPU Usage</p>
          <p className="text-xl font-bold">{server.cpu?.toFixed(1)}%</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <p className="text-sm text-gray-600 mb-1">RAM Usage</p>
          <p className="text-xl font-bold">{server.ram?.toFixed(1)}%</p>
        </div>
      </div>

      {/* Metrics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MetricsChart 
          data={formatCpuData}
          title="CPU Usage (Last Hour)"
          dataKey="value"
          color="#3b82f6"
        />
        <MetricsChart 
          data={formatRamData}
          title="RAM Usage (Last Hour)"
          dataKey="value"
          color="#10b981"
        />
      </div>

      {/* Anomalies */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">
          <Activity className="w-5 h-5 inline mr-2" />
          Anomalies for this Server
        </h3>
        {anomalies.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No anomalies detected</p>
        ) : (
          <div className="space-y-3">
            {anomalies.map(anomaly => (
              <AnomalyAlert key={anomaly.id} anomaly={anomaly} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ServerDetails;