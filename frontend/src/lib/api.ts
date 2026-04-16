import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
});

export const onboardBusiness = async (data: any) => {
  const res = await api.post('/onboarding', data);
  return res.data;
};

export const getProjects = async () => {
  const res = await api.get('/projects');
  return res.data;
};

export const getProject = async (id: str) => {
  const res = await api.get(`/projects/${id}`);
  return res.data;
};

export const generateCreatives = async (projectId: string, file: File | null) => {
  const formData = new FormData();
  if (file) {
    formData.append('file', file);
  }
  const res = await api.post(`/projects/${projectId}/generate`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return res.data;
};

export const getCreatives = async (projectId: string) => {
  const res = await api.get(`/projects/${projectId}/creatives`);
  return res.data;
};
