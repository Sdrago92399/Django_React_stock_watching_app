import axios from 'axios';

export const refreshToken = async () => {
  try {
    const refresh = localStorage.getItem('refreshToken');
    if (!refresh) return;
    const response = await axios.post('/api/auth/token/refresh/', { refresh });
    localStorage.setItem('accessToken', response.data.access);
    return response.data.access;
  } catch (error) {
    console.error('Failed to refresh token:', error);
    return null;
  }
};
