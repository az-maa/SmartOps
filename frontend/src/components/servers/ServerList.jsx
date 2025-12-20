// src/components/servers/ServerList.jsx
import React from 'react';
import ServerCard from './ServerCard';
import Loading from '../common/Loading';

const ServerList = ({ servers, loading, onDelete }) => {
  if (loading) {
    return <Loading text="Loading servers..." />;
  }

  if (!servers || servers.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-12 text-center">
        <p className="text-gray-500 text-lg">No servers found</p>
        <p className="text-gray-400 text-sm mt-2">Add your first server to get started</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {servers.map((server) => (
        <ServerCard 
          key={server.id} 
          server={server} 
          onDelete={onDelete}
        />
      ))}
    </div>
  );
};

export default ServerList;