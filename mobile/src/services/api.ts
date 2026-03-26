import axios from 'axios';
import { API_URL } from '@env';

export const api = axios.create({
  baseURL: API_URL || 'http://192.168.1.100:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth token
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
    }
    return Promise.reject(error);
  }
);

// API Service Functions
export const authAPI = {
  login: (email: string, password: string) => 
    api.post('/auth/login', { username: email, password }),
  register: (data: any) => 
    api.post('/auth/register', data),
  getMe: () => 
    api.get('/auth/me'),
};

export const voucherAPI = {
  list: (params?: any) => 
    api.get('/vouchers', { params }),
  get: (id: string) => 
    api.get(`/vouchers/${id}`),
  create: (data: any) => 
    api.post('/vouchers', data),
  update: (id: string, data: any) => 
    api.put(`/vouchers/${id}`, data),
  delete: (id: string) => 
    api.delete(`/vouchers/${id}`),
};

export const reconciliationAPI = {
  upload: (partyId: string, file: any) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/reconciliation/upload/${partyId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  get: (id: string) => 
    api.get(`/reconciliation/${id}`),
  confirm: (id: string, matchIds: string[]) => 
    api.post(`/reconciliation/${id}/confirm`, { match_ids: matchIds }),
  certificate: (id: string) => 
    api.get(`/reconciliation/${id}/certificate`),
};

export const voiceAPI = {
  entry: (audio: any) => {
    const formData = new FormData();
    formData.append('audio', audio);
    return api.post('/voice/entry', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const invoiceAPI = {
  scan: (image: any) => {
    const formData = new FormData();
    formData.append('file', image);
    return api.post('/invoice/scan', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const messageAPI = {
  parse: (message: string, source: string) => 
    api.post('/messages/parse/sms', { message, source }),
};

export const partyAPI = {
  list: () => 
    api.get('/parties'),
  get: (id: string) => 
    api.get(`/parties/${id}`),
  ledger: (id: string, params?: any) => 
    api.get(`/parties/${id}/ledger`, { params }),
};

export const reportAPI = {
  trialBalance: (params?: any) => 
    api.get('/reports/trial-balance', { params }),
  profitLoss: (params?: any) => 
    api.get('/reports/profit-loss', { params }),
  balanceSheet: (params?: any) => 
    api.get('/reports/balance-sheet', { params }),
  outstanding: (params?: any) => 
    api.get('/reports/outstanding', { params }),
};

export const complianceAPI = {
  calendar: () => 
    api.get('/compliance/calendar'),
  gst2b: (params?: any) => 
    api.get('/compliance/gst-2b', { params }),
  tds: (params?: any) => 
    api.get('/compliance/tds', { params }),
};

export const taxMindAPI = {
  chat: (message: string, context?: any) => 
    api.post('/ai/chat', { message, context }),
};

export const connectorAPI = {
  status: (companyId: string) => 
    api.get(`/connector/status/${companyId}`),
  sync: (companyId: string) => 
    api.post(`/connector/sync/${companyId}`),
};
