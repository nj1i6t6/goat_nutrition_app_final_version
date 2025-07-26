// --- START OF FILE frontend/src/services/api.js ---

async function request(endpoint, options = {}) {
  try {
    const response = await fetch(endpoint, options)
    if (!response.ok) {
      let errorData;
      try { errorData = await response.json() } catch (e) { throw new Error(response.statusText || `伺服器錯誤: ${response.status}`) }
      throw new Error(errorData.message || errorData.error || `伺服器錯誤: ${response.status}`)
    }
    if (response.status === 204) { return { success: true } }
    return response.json()
  } catch (error) {
    console.error(`API 請求錯誤 ${endpoint}:`, error);
    throw error
  }
}

// --- Auth (認證) API ---
// 【修正】所有路徑都加上 /api/auth 前綴
export const checkAuthStatus = () => request('/api/auth/status')
export const login = (username, password) => request('/api/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, password }) })
export const register = (username, password) => request('/api/auth/register', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, password }) })
export const logout = () => request('/api/auth/logout', { method: 'POST' }); // 新增 logout API 調用

// --- Dashboard & AI API ---
export const getDashboardData = () => request('/api/dashboard_data');
export const getAgentTip = (apiKey) => request('/api/agent_tip', { headers: { 'X-Api-Key': apiKey } });
export const getRecommendation = (apiKey, data) => request('/api/recommendation', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...data, api_key: apiKey }) });
export const chatWithAgent = (apiKey, message, sessionId, earNumContext) => request('/api/chat_with_agent', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ api_key: apiKey, message, session_id: sessionId, ear_num_context: earNumContext }) });

// --- Event Options API ---
export const getEventOptions = () => request('/api/event_options');
export const addEventType = (name) => request('/api/event_types', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name }) });
export const deleteEventType = (optionId) => request(`/api/event_types/${optionId}`, { method: 'DELETE' });
export const addEventDescription = (typeId, description) => request('/api/event_descriptions', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ event_type_option_id: typeId, description: description }) });
export const deleteEventDescription = (optionId) => request(`/api/event_descriptions/${optionId}`, { method: 'DELETE' });

// --- Sheep & Event & History Management API ---
export const getAllSheep = () => request('/api/sheep');
export const getSheepDetails = (earNum) => request(`/api/sheep/${earNum}`);
export const addSheep = (data) => request('/api/sheep', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
export const updateSheep = (earNum, data) => request(`/api/sheep/${earNum}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
export const deleteSheep = (earNum) => request(`/api/sheep/${earNum}`, { method: 'DELETE' });
export const getSheepEvents = (earNum) => request(`/api/sheep/${earNum}/events`);
export const addSheepEvent = (earNum, data) => request(`/api/sheep/${earNum}/events`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
export const updateSheepEvent = (eventId, data) => request(`/api/events/${eventId}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
export const deleteSheepEvent = (eventId) => request(`/api/events/${eventId}`, { method: 'DELETE' });
export const getSheepHistory = (earNum) => request(`/api/sheep/${earNum}/history`);
export const deleteSheepHistory = (recordId) => request(`/api/history/${recordId}`, { method: 'DELETE' });

// --- Data Management API ---
export const analyzeExcel = (file) => { const formData = new FormData(); formData.append('file', file); return request('/api/data/analyze_excel', { method: 'POST', body: formData }); };
export const processImport = (file, isDefaultMode, mappingConfig) => { const formData = new FormData(); formData.append('file', file); formData.append('is_default_mode', isDefaultMode); if (!isDefaultMode) { formData.append('mapping_config', JSON.stringify(mappingConfig)); } return request('/api/data/process_import', { method: 'POST', body: formData }); };

// --- END OF FILE frontend/src/services/api.js ---