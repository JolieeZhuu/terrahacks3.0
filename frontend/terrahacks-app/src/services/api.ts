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
  
  // New sending methods
  sendEmail: (emailData) => api.post('/emails/send', emailData),
  replyToEmail: (messageId, replyData) => api.post(`/emails/${messageId}/reply`, replyData),
  getDrafts: () => api.get('/drafts'),
  createDraft: (draftData) => api.post('/drafts', draftData),
};

export const speechAPI = {
  transcribe: (audioBlob, method = 'google') => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    
    return api.post(`/transcribe?method=${method}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  getAvailableMethods: () => api.get('/transcribe/methods')
};

export default api;