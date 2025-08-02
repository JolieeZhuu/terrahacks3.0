import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export const authAPI = {
  login: () => api.get('/auth/login'),
  status: () => api.get('/auth/status'),
  logout: () => api.get('/auth/logout'),
};

export const emailAPI = {
  getEmails: (query = '', maxResults = 10) => 
    api.get(`/emails?query=${encodeURIComponent(query)}&max_results=${maxResults}`),
  getEmail: (messageId) => api.get(`/emails/${messageId}`),
};

export default api;