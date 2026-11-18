import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000',
  timeout: 20000
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('fcommerce_token');

  if (token && !config.headers?.Authorization) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('fcommerce_token');
      localStorage.removeItem('fcommerce_user');
      localStorage.removeItem('seller_id');
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

export default api;
