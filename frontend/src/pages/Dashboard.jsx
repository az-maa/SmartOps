// src/pages/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { Server, CheckCircle, AlertTriangle, XCircle, RefreshCw } from 'lucide-react';
import StatsCard from '../components/dashboard/StatsCard';
import MetricsChart from '../components/dashboard/MetricsChart';
import AnomalyAlert from '../components/dashboard/AnomalyAlert';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';

// Week 1: Import mockApi
import { mockApi as api } from '../services/mockApi';
// Week 2: Uncomment this line and comment the line above
// import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [cpuData, setCpuData] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadDashboardData = async () => {
    try {
      const [statsData, metricsData, anomaliesData] = await Promise.all([
        api.getDashboardStats(),
        api.getMetrics('srv_1'), // Get metrics for first server
        api.getAnomalies()
      ]);

      setStats(statsData);
      
      // Format CPU data for chart
      const formattedCpuData = metricsData.cpu.slice(-24).map((item, index) => ({
        time: `${index}:00`,
        value: item.value
      }));
      setCpuData(formattedCpuData);
      
      setAnomalies(anomaliesData.slice(0, 3)); // Show latest 3 anomalies
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboardData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      loadDashboardData();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    loadDashboardData();
  };

  if (loading) {
    return <Loading text="Loading dashboard..." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <Button 
          variant="secondary"
          onClick={handleRefresh}
          disabled={refreshing}
          loading={refreshing}
        >
          <RefreshCw className="w-4 h-4" />
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </Button>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard 
          title="Total Servers" 
          value={stats?.total_servers || 0}
          icon={Server}
          color="blue"
        />
        <StatsCard 
          title="Online" 
          value={stats?.online_servers || 0}
          icon={CheckCircle}
          color="green"
        />
        <StatsCard 
          title="Warnings" 
          value={stats?.warning_servers || 0}
          icon={AlertTriangle}
          color="yellow"
        />
        <StatsCard 
          title="Critical" 
          value={stats?.critical_servers || 0}
          icon={XCircle}
          color="red"
        />
      </div>
      
      {/* Charts and Anomalies */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MetricsChart 
          data={cpuData}
          title="CPU Usage (Last 24h)"
          dataKey="value"
          color="#3b82f6"
        />
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">Recent Anomalies</h3>
          {anomalies.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No anomalies detected</p>
            </div>
          ) : (
            <div className="space-y-3">
              {anomalies.map(anomaly => (
                <AnomalyAlert key={anomaly.id} anomaly={anomaly} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;