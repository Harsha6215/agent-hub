import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor — attach auth token when available
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("agent-hub-token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      sessionStorage.removeItem("agent-hub-token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
