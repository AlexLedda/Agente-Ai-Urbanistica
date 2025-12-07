import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const api = axios.create({
    baseURL: API_URL,
});

export const loginUser = async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/token', formData, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    });
    return response.data;
};
