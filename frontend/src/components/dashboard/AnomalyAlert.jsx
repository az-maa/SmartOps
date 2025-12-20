// src/components/dashboard/AnomalyAlert.jsx
import React from 'react';
import { AlertCircle, AlertTriangle, Info } from 'lucide-react';

const AnomalyAlert = ({ anomaly }) => {
  const severityConfig = {
    critical: {
      icon: AlertCircle,
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      textColor: 'text-red-800',
      iconColor: 'text-red-600'
    },
    high: {
      icon: AlertTriangle,
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      textColor: 'text-orange-800',
      iconColor: 'text-orange-600'
    },
    medium: {
      icon: AlertTriangle,
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      textColor: 'text-yellow-800',
      iconColor: 'text-yellow-600'
    },
    low: {
      icon: Info,
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-800',
      iconColor: 'text-blue-600'
    }
  };

  const config = severityConfig[anomaly.severity] || severityConfig.low;
  const Icon = config.icon;

  return (
    <div className={`flex items-start gap-3 p-4 rounded-lg border ${config.bgColor} ${config.borderColor}`}>
      <Icon className={`w-5 h-5 ${config.iconColor} flex-shrink-0 mt-0.5`} />
      <div className="flex-1">
        <div className="flex items-center justify-between mb-1">
          <p className={`font-medium text-sm ${config.textColor}`}>
            {anomaly.server_name || 'Unknown Server'}
          </p>
          <span className="text-xs text-gray-500">
            {new Date(anomaly.timestamp).toLocaleTimeString()}
          </span>
        </div>
        <p className="text-sm text-gray-700">
          {anomaly.explanation}
        </p>
        <div className="mt-2 flex items-center gap-2">
          <span className="text-xs px-2 py-1 bg-white rounded-full font-medium">
            {anomaly.type.replace('_', ' ')}
          </span>
          <span className={`text-xs px-2 py-1 rounded-full font-medium ${config.bgColor} ${config.textColor}`}>
            {anomaly.severity}
          </span>
        </div>
      </div>
    </div>
  );
};

export default AnomalyAlert;