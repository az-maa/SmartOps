// src/utils/constants.js

/**
 * Server status constants
 */
export const SERVER_STATUS = {
  ONLINE: 'online',
  WARNING: 'warning',
  CRITICAL: 'critical',
  OFFLINE: 'offline'
};

/**
 * Anomaly severity levels
 */
export const ANOMALY_SEVERITY = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low'
};

/**
 * Anomaly types
 */
export const ANOMALY_TYPES = {
  CPU_SPIKE: 'cpu_spike',
  MEMORY_LEAK: 'memory_leak',
  DISK_FULL: 'disk_full',
  NETWORK_ANOMALY: 'network_anomaly',
  PROCESS_CRASH: 'process_crash'
};

/**
 * Refresh intervals (in milliseconds)
 */
export const REFRESH_INTERVALS = {
  DASHBOARD: 30000,  // 30 seconds
  SERVERS: 30000,    // 30 seconds
  METRICS: 60000,    // 1 minute
  ANOMALIES: 45000   // 45 seconds
};

/**
 * Chart colors
 */
export const CHART_COLORS = {
  CPU: '#3b82f6',      // Blue
  RAM: '#10b981',      // Green
  DISK: '#f59e0b',     // Amber
  NETWORK: '#8b5cf6',  // Purple
  PREDICTION: '#3b82f6'
};

/**
 * Status colors (TailwindCSS)
 */
export const STATUS_COLORS = {
  online: {
    bg: 'bg-green-100',
    text: 'text-green-800',
    border: 'border-green-200'
  },
  warning: {
    bg: 'bg-yellow-100',
    text: 'text-yellow-800',
    border: 'border-yellow-200'
  },
  critical: {
    bg: 'bg-red-100',
    text: 'text-red-800',
    border: 'border-red-200'
  },
  offline: {
    bg: 'bg-gray-100',
    text: 'text-gray-800',
    border: 'border-gray-200'
  }
};

/**
 * Severity colors (TailwindCSS)
 */
export const SEVERITY_COLORS = {
  critical: {
    bg: 'bg-red-50',
    text: 'text-red-800',
    border: 'border-red-200',
    badge: 'bg-red-100 text-red-800'
  },
  high: {
    bg: 'bg-orange-50',
    text: 'text-orange-800',
    border: 'border-orange-200',
    badge: 'bg-orange-100 text-orange-800'
  },
  medium: {
    bg: 'bg-yellow-50',
    text: 'text-yellow-800',
    border: 'border-yellow-200',
    badge: 'bg-yellow-100 text-yellow-800'
  },
  low: {
    bg: 'bg-blue-50',
    text: 'text-blue-800',
    border: 'border-blue-200',
    badge: 'bg-blue-100 text-blue-800'
  }
};

/**
 * API endpoints (for reference)
 */
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    ME: '/api/auth/me'
  },
  SERVERS: {
    LIST: '/api/servers',
    DETAIL: '/api/servers/:id',
    CREATE: '/api/servers',
    DELETE: '/api/servers/:id'
  },
  METRICS: {
    GET: '/api/metrics/:serverId'
  },
  ANOMALIES: {
    LIST: '/api/anomalies',
    BY_SERVER: '/api/anomalies/:serverId'
  },
  PREDICTIONS: {
    GET: '/api/predictions/:serverId'
  }
};

/**
 * Validation patterns
 */
export const VALIDATION = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  IP_ADDRESS: /^(\d{1,3}\.){3}\d{1,3}$/,
  PASSWORD_MIN_LENGTH: 6
};

/**
 * Pagination defaults
 */
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  PAGE_SIZE_OPTIONS: [10, 25, 50, 100]
};

/**
 * Local storage keys
 */
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'token',
  USER_DATA: 'user',
  THEME: 'theme'
};