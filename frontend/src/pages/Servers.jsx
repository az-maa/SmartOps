// src/pages/Servers.jsx
import React, { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import ServerList from '../components/servers/ServerList';
import AddServerModal from '../components/servers/AddServerModal';
import Button from '../components/common/Button';

// Week 1: Import mockApi
import { mockApi as api } from '../services/mockApi';
// Week 2: Uncomment this line and comment the line above
// import api from '../services/api';

const Servers = () => {
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  const loadServers = async () => {
    try {
      const data = await api.getServers();
      setServers(data);
    } catch (error) {
      console.error('Error loading servers:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadServers();

    // Auto-refresh every 30 seconds
    const interval = setInterval(loadServers, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleAddServer = async (name, ip, apiKey) => {
    try {
      const newServer = await api.addServer(name, ip, apiKey);
      setServers([...servers, newServer]);
    } catch (error) {
      throw error;
    }
  };

  const handleDeleteServer = async (serverId) => {
    if (!window.confirm('Are you sure you want to delete this server?')) {
      return;
    }

    try {
      await api.deleteServer(serverId);
      setServers(servers.filter(s => s.id !== serverId));
    } catch (error) {
      console.error('Error deleting server:', error);
      alert('Failed to delete server');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Servers</h2>
          <p className="text-gray-600 mt-1">Manage your monitored servers</p>
        </div>
        <Button 
          variant="primary" 
          onClick={() => setShowAddModal(true)}
        >
          <Plus className="w-4 h-4" />
          Add Server
        </Button>
      </div>
      
      <ServerList 
        servers={servers}
        loading={loading}
        onDelete={handleDeleteServer}
      />

      <AddServerModal 
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onAdd={handleAddServer}
      />
    </div>
  );
};

export default Servers;