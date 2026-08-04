import axios from "axios";

// Set VITE_API_URL in a .env file to point at your deployed Railway URL,
// e.g. VITE_API_URL=https://boutique-cloud-api-production.up.railway.app
// Falls back to localhost so `npm run dev` works against a locally-running
// backend with zero configuration.
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: API_URL });

// Every request automatically gets the logged-in shop's token attached, so
// individual page components never have to think about auth headers.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// If the token is missing/expired, the backend returns 401 - bounce back
// to login automatically rather than showing a confusing broken page.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("shop_name");
      localStorage.removeItem("currency");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);
