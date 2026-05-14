import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  register: async (email, username, password) => {
    const response = await api.post('/auth/register', { email, username, password });
    return response.data;
  },
  
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export const projectService = {
  getProjects: async () => {
    const response = await api.get('/projects');
    return response.data;
  },
  
  createProject: async (name, language, code = '', description = '') => {
    const response = await api.post('/projects', { name, language, code, description });
    return response.data;
  },
  
  getProject: async (projectId) => {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  },
  
  updateProject: async (projectId, data) => {
    const response = await api.put(`/projects/${projectId}`, data);
    return response.data;
  },
  
  deleteProject: async (projectId) => {
    const response = await api.delete(`/projects/${projectId}`);
    return response.data;
  },
};

export const executionService = {
  executeCode: async (language, code, input_data = '') => {
    const response = await api.post('/execute', { language, code, input_data });
    return response.data;
  },
  
  getHistory: async () => {
    const response = await api.get('/history');
    return response.data;
  },
};

export default api;
