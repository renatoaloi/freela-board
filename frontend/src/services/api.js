import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'X-API-Key': 'freela-secret-key-2024',
    'Content-Type': 'application/json',
  },
});

export default api;

export const clientesAPI = {
  list: () => api.get('/clientes'),
  get: (id) => api.get(`/clientes/${id}`),
  create: (data) => api.post('/clientes', data),
  update: (id, data) => api.put(`/clientes/${id}`, data),
  delete: (id) => api.delete(`/clientes/${id}`),
};

export const projetosAPI = {
  list: (cliente_id) => {
    const params = cliente_id ? { cliente_id } : {};
    return api.get('/projetos', { params });
  },
  get: (id) => api.get(`/projetos/${id}`),
  create: (data) => api.post('/projetos', data),
  update: (id, data) => api.put(`/projetos/${id}`, data),
  delete: (id) => api.delete(`/projetos/${id}`),
};

export const tarefasAPI = {
  list: (params = {}) => api.get('/tarefas', { params }),
  get: (id) => api.get(`/tarefas/${id}`),
  create: (data) => api.post('/tarefas', data),
  update: (id, data) => api.put(`/tarefas/${id}`, data),
  delete: (id) => api.delete(`/tarefas/${id}`),
};

export const apontamentosAPI = {
  listByTarefa: (tarefa_id) => api.get(`/apontamentos`, { params: { tarefa_id } }),
  create: (data) => api.post('/apontamentos', data),
  update: (id, data) => api.put(`/apontamentos/${id}`, data),
  delete: (id) => api.delete(`/apontamentos/${id}`),
};

export const uploadAPI = {
  upload: (tarefa_id, file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/upload/${tarefa_id}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress,
    });
  },
  download: (tarefa_id, filename) =>
    api.get(`/upload/${tarefa_id}/${filename}`, { responseType: 'blob' }),
  delete: (tarefa_id, filename) => api.delete(`/upload/${tarefa_id}/${filename}`),
};

export const relatoriosAPI = {
  generate: (cliente_id, mes, ano) =>
    api.get('/relatorios', { params: { cliente_id, mes, ano } }),
  generatePdf: (cliente_id, mes, ano) =>
    api.get('/relatorios/pdf', { params: { cliente_id, mes, ano }, responseType: 'blob' }),
};

export const dadosBancariosAPI = {
  get: () => api.get('/dados-bancarios'),
  update: (data) => api.put('/dados-bancarios', data),
};

export const dashboardAPI = {
  get: () => api.get('/dashboard'),
};
