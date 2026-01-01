import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000',
  timeout: 20000
});

api.interceptors.response.use(
  (res) => res,
  (err) => Promise.reject(err)
);



