import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: `${API_BASE_URL}/api/v1`,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Device API
export const deviceAPI = {
    getAll: () => api.get('/devices'),
    getOne: (mac) => api.get(`/devices/${mac}`),
    block: (mac) => api.post(`/devices/${mac}/block`),
    allow: (mac) => api.post(`/devices/${mac}/allow`),
};

// Network API
export const networkAPI = {
    getStats: () => api.get('/network/stats'),
};

// Threats API
export const threatsAPI = {
    getRecent: () => api.get('/threats/recent'),
};

// WebSocket connection
export const createWebSocket = (onMessage) => {
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
