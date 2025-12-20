// src/components/servers/ServerCard.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Cpu, HardDrive, Clock, Trash2 } from 'lucide-react';
import Button from '../common/Button';

const ServerCard = ({ server, onDelete }) => {
  const navigate = useNavigate();

  const getStatusColor = (status) => {
    const colors = {
      online: 'bg-green-100 text-green-800',
      warning: 'bg-yellow-100 text-yellow-800',
      critical: 'bg-red-100 text-red-800',
      offline: 'bg-gray-100 text-gray-800'
    };
    return colors[status] || colors.offline;
  };

  const handleViewDetails = () => {
    navigate(`/servers/${server.id}`);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{server.name}</h3>
          <p className="text-sm text-gray-600">{server.ip}</p>
        </div>
        <span className={`px-2.5 py-1 text-sm font-medium rounded-full ${getStatusColor(server.status)}`}>
          {server.status}
        </span>
      </div>
      
      <div className="space-y-3 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">CPU</span>
          </div>
          <span className="font-semibold">{server.cpu?.toFixed(1) || 0}%</span>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">RAM</span>
          </div>
          <span className="font-semibold">{server.ram?.toFixed(1) || 0}%</span>
        </div>
        
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            <span>Last seen</span>
          </div>
          <span>{new Date(server.last_seen).toLocaleTimeString()}</span>
        </div>
      </div>
      
      <div className="pt-4 border-t flex gap-2">
        <Button 
          variant="secondary" 
          className="flex-1 text-sm"
          onClick={handleViewDetails}
        >
          View Details
        </Button>
        <Button 
          variant="danger" 
          onClick={() => onDelete(server.id)}
          className="text-sm"
        >
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
};

export default ServerCard;