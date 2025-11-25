import axios from 'axios';

// Create a configured axios instance (optional, but good practice)
export const api = axios.create({
  baseURL: '/api'
});

export const initAuthFromStorage = () => {
  const token = localStorage.getItem('token');
  if (token) {
    setAuthToken(token);
  }
};

export const setAuthToken = (token) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
    delete api.defaults.headers.common['Authorization'];
  }
};
