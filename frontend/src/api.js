import axios from 'axios';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    if (err.response?.status === 401) {
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        try {
          const { data } = await axios.post(`${API_BASE}/auth/refresh`, { refresh_token: refresh });
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          err.config.headers.Authorization = `Bearer ${data.access_token}`;
          return api(err.config);
        } catch (e) {
          localStorage.clear();
          window.location.href = '/login';
        }
      } else {
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    return Promise.reject(err);
  }
);

export const authApi = {
  register: (d) => api.post('/auth/register', d),
  login: (d) => api.post('/auth/login', d),
  me: () => api.get('/auth/me'),
};

export const recipesApi = {
  list: (p) => api.get('/recipes', { params: p }),
  get: (id) => api.get(`/recipes/${id}`),
  searchByIngredients: (ids, p) => api.post('/recipes/search-by-ingredients', { ingredient_ids: ids }, { params: p }),
};

export const myRecipesApi = {
  list: (p) => api.get('/my-recipes', { params: p }),
  create: (d) => api.post('/my-recipes', d),
  get: (id) => api.get(`/my-recipes/${id}`),
  update: (id, d) => api.put(`/my-recipes/${id}`, d),
  delete: (id) => api.delete(`/my-recipes/${id}`),
};

export const ingredientsApi = {
  list: () => api.get('/ingredients'),
  create: (d) => api.post('/ingredients', d),
};

export default api;