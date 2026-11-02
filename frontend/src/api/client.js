import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token from localStorage to every outgoing request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('campushelp_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercept 401 Unauthorized errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token on authorization failure if not logging in
      if (!error.config.url.includes('/auth/login')) {
        localStorage.removeItem('campushelp_token');
        localStorage.removeItem('campushelp_user');
      }
    }
    return Promise.reject(error);
  }
);

// Auth Endpoints
export const authLogin = async (email, password) => {
  const response = await api.post('/auth/login', { email, password });
  return response.data;
};

export const authRegister = async (email, password, full_name, role = 'student') => {
  const response = await api.post('/auth/register', { email, password, full_name, role });
  return response.data;
};

export const getMe = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

// Chat Endpoints
export const sendChatMessage = async ({ message, conversation_id, department_filter, category_filter }) => {
  const response = await api.post('/chat', {
    message,
    conversation_id,
    department_filter,
    category_filter,
  });
  return response.data;
};

export const getConversations = async () => {
  const response = await api.get('/chat/conversations');
  return response.data;
};

export const getConversation = async (conversationId) => {
  const response = await api.get(`/chat/conversations/${conversationId}`);
  return response.data;
};

export const deleteConversation = async (conversationId) => {
  const response = await api.delete(`/chat/conversations/${conversationId}`);
  return response.data;
};

// Feedback Endpoints
export const submitFeedback = async (message_id, rating, feedback_text = '') => {
  const response = await api.post('/feedback', { message_id, rating, feedback_text });
  return response.data;
};

// Document Management Endpoints
export const uploadDocuments = async (formData) => {
  const response = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDocuments = async (params = {}) => {
  const response = await api.get('/documents', { params });
  return response.data;
};

export const deleteDocument = async (documentId) => {
  const response = await api.delete(`/documents/${documentId}`);
  return response.data;
};

export const reindexDocument = async (documentId) => {
  const response = await api.post(`/documents/${documentId}/reindex`);
  return response.data;
};

// Admin Monitoring Endpoints
export const getAdminAnalytics = async () => {
  const response = await api.get('/admin/analytics');
  return response.data;
};

export const getAdminLogs = async (limit = 50, offset = 0) => {
  const response = await api.get('/admin/logs', { params: { limit, offset } });
  return response.data;
};

// System Endpoints
export const checkSystemHealth = async () => {
  const response = await axios.get('/health');
  return response.data;
};

export const checkSystemReady = async () => {
  const response = await axios.get('/ready');
  return response.data;
};

export default api;
