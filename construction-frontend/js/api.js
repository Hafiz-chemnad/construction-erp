// js/api.js

// This is the ONLY place you need to change the URL if you ever move your server!
const BASE_URL = "const BASE_URL = 'https://construction-backend.onrender.com';";

/**
 * A central function to handle all API requests.
 * It automatically handles converting data to JSON and catching errors.
 */
async function apiRequest(endpoint, method = 'GET', data = null) {
    const config = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        cache: 'no-store'
    };

    if (data) {
        config.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, config);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Something went wrong on the server.");
        }

        return result;
    } catch (error) {
        console.error("API Error:", error);
        alert(`Connection Error: ${error.message}`);
        return null; // Return null so the frontend knows it failed
    }
}

// Export the specific functions we need for the rest of the app to use
export const api = {
    // Panchayath API Calls
    getPanchayaths: () => apiRequest('/panchayaths'),
    addPanchayath: (name) => apiRequest('/panchayaths', 'POST', { name: name }),

    // Works API Calls
    getWorks: (panchayathId) => apiRequest(`/works/${panchayathId}`),
    addWork: (workData) => apiRequest('/works', 'POST', workData),
    // Inside js/api.js export const api = { ... }
    getWorkDetail: (id) => apiRequest(`/works/detail/${id}`),
    updateWorkStatus: (id, status) => apiRequest(`/works/${id}/status`, 'PATCH', { status: status }),
    // INITIALIZATION & AGREEMENT
    createAgreement: (data) => apiRequest('/agreements', 'POST', data),

    // DAILY LOGS (Labour, Materials, Diesel)
    getMaterialsByWork: (workId) => apiRequest(`/materials/${workId}`),
    addMaterial: (data) => apiRequest('/materials', 'POST', data),

    getDieselByWork: (workId) => apiRequest(`/diesel/${workId}`),
    addDiesel: (data) => apiRequest('/diesel', 'POST', data),

    // LABOUR MODULE
    getLabourers: (workId) => apiRequest(`/labourers/${workId}`),
    addLabourer: (data) => apiRequest('/labourers', 'POST', data),
    addLabourCash: (data) => apiRequest('/labour-cash', 'POST', data),
    getLabourCashByWork: (workId) => apiRequest(`/labour-cash/${workId}`),
    
    getAttendance: (workId) => apiRequest(`/attendance/${workId}`),
    markAttendance: (data) => apiRequest('/attendance', 'POST', data),
    // FINISH PROJECT
    finishWork: (id, data) => apiRequest(`/works/${id}/finish`, 'POST', data),
    // We will add the finishWork, addMaterial, etc. here later!
};