// Hardcode 127.0.0.1 to avoid strict IPv6 localhost mapping failures locally
// DEPLOYMENT NOTE: When deploying this React app (e.g., to Vercel/Netlify), 
// you must define VITE_API_URL in tracking pointing to your live backend domain 
// Example: VITE_API_URL=https://my-fastapi-backend.onrender.com
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
console.log("Using API_URL:", API_URL);

const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
};

const handleResponse = async (response, customErrorMsg) => {
    if (!response.ok) {
        let errData;
        try {
            errData = await response.json();
            console.error(`[API Error Response]: `, errData);
        } catch (e) {
            console.error(`[API Network/Format Error]: `, response.statusText);
        }
        throw new Error(errData?.detail || customErrorMsg || 'Unable to reach the server. Please try again later.');
    }
    const data = await response.json();
    console.log(`[API Success Response]: `, data);
    return data;
};

export const api = {
    async register(username, email, password) {
        console.log(`[API Request] POST /register`, { username, email });
        try {
            const response = await fetch(`${API_URL}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            return await handleResponse(response, 'Registration failed');
        } catch(e) { 
            console.error("[API Fail]", e); 
            if (e.message === 'Failed to fetch') throw new Error('Unable to contact backend server. Ensure FastAPI is running.');
            throw e; 
        }
    },

    async login(username, password) {
        console.log(`[API Request] POST /login`, { username });
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        try {
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData.toString()
            });
            const data = await handleResponse(response, 'Invalid credentials');
            localStorage.setItem('token', data.access_token);
            return data;
        } catch(e) { 
            console.error("[API Fail]", e); 
            if (e.message === 'Failed to fetch') throw new Error('Unable to contact backend server. Ensure FastAPI is running.');
            throw e; 
        }
    },

    async logout() {
        console.log("[API Call] logout");
        localStorage.removeItem('token');
    },

    async getCurrentUser() {
        if (!localStorage.getItem('token')) return null;
        console.log(`[API Request] GET /me`);
        try {
            const response = await fetch(`${API_URL}/me`, { headers: { ...getAuthHeaders() } });
            if (!response.ok) return null;
            const data = await response.json();
            console.log(`[API Success Response] GET /me`, data);
            return data;
        } catch(e) { console.error("[API Fail]", e); return null; }
    },

    async predict(file) {
        console.log(`[API Request] POST /predict`);
        const formData = new FormData();
        formData.append('file', file);
        try {
            const response = await fetch(`${API_URL}/predict`, {
                method: 'POST',
                headers: { ...getAuthHeaders() },
                body: formData,
            });
            return await handleResponse(response, 'Prediction failed. Please try again.');
        } catch(e) { console.error("[API Fail]", e); throw new Error('Prediction failed. Please try again.'); }
    },

    async explain(prediction, confidence) {
        console.log(`[API Request] POST /explain`, { prediction, confidence });
        try {
            const response = await fetch(`${API_URL}/explain`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prediction, confidence })
            });
            return await handleResponse(response, 'AI explanation failed.');
        } catch(e) { console.error("[API Fail]", e); throw new Error('AI explanation failed.'); }
    },

    async chat(message, context = null) {
        console.log(`[API Request] POST /chat`, { message, context });
        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, context })
            });
            return await handleResponse(response, 'Unable to reach the server. Please try again later.');
        } catch(e) { console.error("[API Fail]", e); throw new Error('Unable to reach the server. Please try again later.'); }
    },

    async saveHistory(prediction, confidence, explanation, image_data = null, cost_estimation = null, damage_percentage = null) {
        console.log(`[API Request] POST /history`);
        try {
            const response = await fetch(`${API_URL}/history`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
                body: JSON.stringify({ prediction, confidence, explanation, image_data, cost_estimation, damage_percentage })
            });
            return await handleResponse(response, 'Failed to save history');
        } catch(e) { console.error("[API Fail]", e); throw e; }
    },

    async getHistory() {
        console.log(`[API Request] GET /history`);
        try {
            const response = await fetch(`${API_URL}/history`, { headers: { ...getAuthHeaders() } });
            return await handleResponse(response, 'Failed to fetch history');
        } catch(e) { console.error("[API Fail]", e); throw e; }
    },

    async deleteHistory(id) {
        console.log(`[API Request] DELETE /history/${id}`);
        try {
            const response = await fetch(`${API_URL}/history/${id}`, {
                method: 'DELETE',
                headers: { ...getAuthHeaders() }
            });
            return await handleResponse(response, 'Failed to delete record');
        } catch(e) { console.error("[API Fail]", e); throw e; }
    },

    async deleteAllHistory() {
        console.log(`[API Request] DELETE /history`);
        try {
            const response = await fetch(`${API_URL}/history`, {
                method: 'DELETE',
                headers: { ...getAuthHeaders() }
            });
            return await handleResponse(response, 'Failed to delete all records');
        } catch(e) { console.error("[API Fail]", e); throw e; }
    },
    
    async generateReportUrl(prediction, confidence, explanation, image_data = null, estimated_cost = null, damage_percentage = null, recommendations = null) {
        console.log(`[API Request] POST /generate-report`);
        try {
            const response = await fetch(`${API_URL}/generate-report`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
                body: JSON.stringify({ prediction, confidence, explanation, image_data, estimated_cost, damage_percentage, recommendations })
            });
            if (!response.ok) {
                console.error("[API Error] PDF Generation Failed");
                throw new Error('PDF Generation Failed');
            }
            const blob = await response.blob();
            console.log("[API Success] Blob received:", blob.size);
            return window.URL.createObjectURL(blob);
        } catch(e) { console.error("[API Fail]", e); throw e; }
    }
};
