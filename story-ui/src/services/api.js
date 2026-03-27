const API_BASE_URL = 'http://localhost:9001/api/v1';

export const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
};

export const login = async (username, password) => {
  const response = await fetch('http://localhost:9001/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  if (!response.ok) throw new Error('Invalid credentials');
  return response.json();
};

export const fetchProjects = async () => {
  const response = await fetch(`${API_BASE_URL}/story/projects`, {
    headers: getAuthHeaders()
  });
  if (!response.ok) throw new Error('Failed to fetch projects');
  return response.json();
};

export const generateStory = async (topic) => {
  const response = await fetch(`${API_BASE_URL}/story/generate-story`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ topic })
  });
  if (!response.ok) throw new Error('Story generation failed');
  return response.json();
};

export const generateScenes = async (story) => {
  const response = await fetch(`${API_BASE_URL}/story/generate-scenes`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ story })
  });
  if (!response.ok) throw new Error('Scene generation failed');
  return response.json();
};

export const saveDraft = async (topic, story, scenes) => {
  const response = await fetch(`${API_BASE_URL}/story/save-draft`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ topic, story, scenes })
  });
  if (!response.ok) throw new Error('Failed to save draft');
  return response.json();
};

export const publishProject = async (projectId) => {
  const response = await fetch(`${API_BASE_URL}/story/publish-project/${projectId}`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  if (!response.ok) throw new Error('Failed to publish');
  return response.json();
};
