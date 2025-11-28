import axios from 'axios';
import { mockDevices, mockStats, mockThreats, mockMLAlerts } from './mockData';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true';

const api = axios.create({
    baseURL: `${API_BASE_URL}/api/v1`,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Helper to simulate API delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Device API
export const deviceAPI = {
    getAll: async () => {
        if (DEMO_MODE) {
            await delay(500);
            return { data: { devices: mockDevices, total: mockDevices.length } };
        }
        return api.get('/devices');
    },
    getOne: async (mac) => {
        if (DEMO_MODE) {
            await delay(300);
            const device = mockDevices.find(d => d.mac === mac);
            return { data: device || {} };
        }
        return api.get(`/devices/${mac}`);
    },
    block: async (mac) => {
        if (DEMO_MODE) {
            await delay(300);
            return { data: { status: 'success', message: `Device ${mac} blocked (Demo Mode)` } };
        }
        return api.post(`/devices/${mac}/block`);
    },
    allow: async (mac) => {
        if (DEMO_MODE) {
            await delay(300);
            return { data: { status: 'success', message: `Device ${mac} allowed (Demo Mode)` } };
        }
        return api.post(`/devices/${mac}/allow`);
    },
};

// Network API
export const networkAPI = {
    getStats: async () => {
        if (DEMO_MODE) {
            await delay(500);
            return { data: mockStats };
        }
        return api.get('/network/stats');
    },
};

// Threats API
export const threatsAPI = {
    getRecent: async () => {
        if (DEMO_MODE) {
            await delay(500);
            return { data: { threats: mockThreats, total: mockThreats.length } };
        }
        return api.get('/threats/recent');
    },
};

// WebSocket connection
export const createWebSocket = (onMessage) => {
    if (DEMO_MODE) {
        console.log('Demo Mode: Simulating WebSocket connection');
        // Simulate occasional updates
        const interval = setInterval(() => {
            if (Math.random() > 0.7) {
                // Randomly update stats
                onMessage({
                    type: 'stats_update',
                    data: {
                        ...mockStats,
                        timestamp: new Date().toISOString(),
                        devices: {
                            ...mockStats.devices,
                            active: Math.floor(Math.random() * 15)
                        }
                    }
                });
            }
        }, 5000);

        return {
            close: () => clearInterval(interval)
        };
    }

    const ws = new WebSocket(`ws://localhost:8000/api/v1/ws`);

    ws.onopen = () => {
        console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            onMessage(data);
        } catch (error) {
            console.error('WebSocket message error:', error);
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected');
    };

    return ws;
};

export default api;
