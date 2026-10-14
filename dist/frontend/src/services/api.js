import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'X-API-Key': import.meta.env.VITE_API_KEY,
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
  list: () => api.get('/relatorios'),
  get: (id) => api.get(`/relatorios/${id}`),
  downloadPdf: (id) =>
    api.get(`/relatorios/${id}/pdf`, { responseType: 'blob' }),
};

export const fechamentoAPI = {
  tarefasElegiveis: (cliente_id, mes, ano, projeto_id) => {
    const params = { cliente_id, mes, ano };
    if (projeto_id) params.projeto_id = projeto_id;
    return api.get('/fechamentos/tarefas-elegiveis', { params });
  },
  fechar: (data) => api.post('/fechamentos', data),
};

export const dadosBancariosAPI = {
  get: () => api.get('/dados-bancarios'),
  update: (data) => api.put('/dados-bancarios', data),
};

export const dashboardAPI = {
  get: () => api.get('/dashboard'),
};
