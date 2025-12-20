// src/services/mockApi.js
// WEEK 1: Utiliser ces données
// WEEK 2: Remplacer par api.js avec vrais appels

// Génère des métriques temporelles
const generateMetrics = (points = 50, base = 40, variance = 30) => {
  return Array.from({ length: points }, (_, i) => ({
    time: new Date(Date.now() - (points - i) * 60000).toISOString(),
    value: Math.max(0, Math.min(100, base + (Math.random() - 0.5) * variance))
  }));
};

// Données mock des serveurs
export const mockServers = [
  {
    id: "srv_1",
    name: "Web Server 1",
    ip: "192.168.1.100",
    status: "online",
    cpu: 45.2,
    ram: 67.8,
    last_seen: new Date(Date.now() - 30000).toISOString()
  },
  {
    id: "srv_2",
    name: "Database Server",
    ip: "192.168.1.101",
    status: "warning",
    cpu: 78.5,
    ram: 82.1,
    last_seen: new Date(Date.now() - 45000).toISOString()
  },
  {
    id: "srv_3",
    name: "API Gateway",
    ip: "192.168.1.102",
    status: "online",
    cpu: 32.1,
    ram: 54.3,
    last_seen: new Date(Date.now() - 20000).toISOString()
  },
  {
    id: "srv_4",
    name: "Cache Server",
    ip: "192.168.1.103",
    status: "critical",
    cpu: 92.7,
    ram: 95.4,
    last_seen: new Date(Date.now() - 120000).toISOString()
  }
];

// Métriques détaillées pour un serveur
export const mockMetrics = {
  cpu: generateMetrics(50, 45, 40),
  ram: generateMetrics(50, 65, 30),
  disk_io: generateMetrics(50, 30, 25),
  network: generateMetrics(50, 50, 35)
};

// Anomalies détectées
// Anomalies détectées
export const mockAnomalies = [
  {
    id: "anom_1",
    server_id: "srv_2",
    server_name: "Database Server",  // ← Ajoutez ceci
    timestamp: new Date(Date.now() - 300000).toISOString(),
    type: "cpu_spike",
    severity: "high",
    explanation: "CPU usage increased by 45% in 2 minutes. Likely caused by backup process consuming excessive resources."
  },
  {
    id: "anom_2",
    server_id: "srv_4",
    server_name: "Cache Server",  // ← Ajoutez ceci
    timestamp: new Date(Date.now() - 180000).toISOString(),
    type: "memory_leak",
    severity: "critical",
    explanation: "RAM usage growing steadily at 2% per minute. Possible memory leak in application process."
  },
  {
    id: "anom_3",
    server_id: "srv_1",
    server_name: "Web Server 1",  // ← Ajoutez ceci
    timestamp: new Date(Date.now() - 600000).toISOString(),
    type: "network_anomaly",
    severity: "medium",
    explanation: "Unusual network traffic pattern detected. 3x normal bandwidth usage observed."
  }
];

// Prédictions futures
export const mockPredictions = {
  server_id: "srv_1",
  created_at: new Date().toISOString(),
  forecast: Array.from({ length: 30 }, (_, i) => ({
    time: new Date(Date.now() + i * 60000).toISOString(),
    predicted_value: 45 + Math.sin(i / 5) * 15,
    lower_bound: 35 + Math.sin(i / 5) * 15,
    upper_bound: 55 + Math.sin(i / 5) * 15
  }))
};

// Statistiques dashboard
export const mockDashboardStats = {
  total_servers: 4,
  online_servers: 2,
  warning_servers: 1,
  critical_servers: 1,
  total_anomalies_today: 3,
  avg_cpu_usage: 62.1,
  avg_ram_usage: 74.9
};

// Mock API delay pour simuler réseau
const delay = (ms = 500) => new Promise(resolve => setTimeout(resolve, ms));

// Mock API Functions
export const mockApi = {
  // Authentication
  login: async (email, password) => {
    await delay();
    if (email && password) {
      return {
        token: "mock_jwt_token_" + Date.now(),
        user: {
          id: "user_1",
          email: email,
          name: "Demo User"
        }
      };
    }
    throw new Error("Invalid credentials");
  },

  register: async (email, password, name) => {
    await delay();
    return {
      token: "mock_jwt_token_" + Date.now(),
      user: {
        id: "user_" + Date.now(),
        email: email,
        name: name
      }
    };
  },

  getCurrentUser: async () => {
    await delay(200);
    return {
      id: "user_1",
      email: "demo@smartops.com",
      name: "Demo User"
    };
  },

  // Servers
  getServers: async () => {
    await delay();
    return mockServers;
  },

  getServerById: async (id) => {
    await delay();
    const server = mockServers.find(s => s.id === id);
    if (!server) throw new Error("Server not found");
    return server;
  },

  addServer: async (name, ip) => {
    await delay();
    return {
      id: "srv_" + Date.now(),
      name,
      ip,
      status: "online",
      cpu: 0,
      ram: 0,
      last_seen: new Date().toISOString()
    };
  },

  deleteServer: async (id) => {
    await delay();
    return { success: true };
  },

  // Metrics
  getMetrics: async (serverId, from, to) => {
    await delay();
    return mockMetrics;
  },

  // Anomalies
  getAnomalies: async (serverId) => {
    await delay();
    return mockAnomalies.filter(a => !serverId || a.server_id === serverId);
  },

  // Predictions
  getPredictions: async (serverId) => {
    await delay();
    return mockPredictions;
  },

  // Dashboard stats
  getDashboardStats: async () => {
    await delay(300);
    return mockDashboardStats;
  }
};

export default mockApi;