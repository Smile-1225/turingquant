/**
 * 图灵量化 - API请求封装
 */
const API = {
    // 后端地址 - 自动使用当前域名，生产/本地自适应
    BASE_URL: window.location.origin,

    // 获取存储的Token
    getToken() {
        return localStorage.getItem('tq_token') || '';
    },

    // 设置Token
    setToken(token) {
        localStorage.setItem('tq_token', token);
    },

    // 清除Token
    clearToken() {
        localStorage.removeItem('tq_token');
    },

    // 通用请求
    async request(method, endpoint, data = null, auth = true) {
        const url = `${this.BASE_URL}${endpoint}`;
        const headers = { 'Content-Type': 'application/json' };

        if (auth && this.getToken()) {
            headers['Authorization'] = `Bearer ${this.getToken()}`;
        }

        const options = { method, headers };
        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            const result = await response.json();

            if (!response.ok) {
                if (response.status === 401) {
                    // Token过期，触发登出
                    App.auth.logout();
                    Utils.toast('登录已过期，请重新登录', 'warning');
                }
                throw new Error(result.message || '请求失败');
            }

            return result;
        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                Utils.toast('网络连接失败，请检查后端服务', 'error');
            }
            throw error;
        }
    },

    get(endpoint, auth = true) { return this.request('GET', endpoint, null, auth); },
    post(endpoint, data, auth = true) { return this.request('POST', endpoint, data, auth); },
    put(endpoint, data, auth = true) { return this.request('PUT', endpoint, data, auth); },
    del(endpoint, auth = true) { return this.request('DELETE', endpoint, null, auth); },

    // === 认证接口 ===
    auth: {
        register(data) { return API.post('/api/auth/register', data, false); },
        login(data) { return API.post('/api/auth/login', data, false); },
        getProfile() { return API.get('/api/auth/profile'); },
        updateProfile(data) { return API.put('/api/auth/profile', data); },
        changePassword(data) { return API.post('/api/auth/change-password', data); },
    },

    // === 公共接口 ===
    public: {
        getModules() { return API.get('/api/public/modules', false); },
        getIndices() { return API.get('/api/public/indices', false); },
    },

    // === 业务接口 ===
    getDashboard() { return API.get('/api/dashboard', false); },
    getStrategies() { return API.get('/api/strategies', false); },
    getStrategyDetail(id) { return API.get(`/api/strategies/${id}`, false); },

    timing: {
        analyze(data) { return API.post('/api/timing/analyze', data); },
    },

    review: {
        getLimitUp(params = {}) {
            const qs = new URLSearchParams(params).toString();
            return API.get(`/api/review/limit-up?${qs}`);
        },
        getIndustry(params = {}) {
            const qs = new URLSearchParams(params).toString();
            return API.get(`/api/review/industry?${qs}`);
        },
    },

    signals: {
        getList(params = {}) {
            const qs = new URLSearchParams(params).toString();
            return API.get(`/api/signals?${qs}`);
        },
        getLatest() { return API.get('/api/signals/latest'); },
    },

    // === 管理后台接口 ===
    admin: {
        getUsers(params = {}) {
            const qs = new URLSearchParams(params).toString();
            return API.get(`/api/admin/users?${qs}`);
        },
        createUser(data) { return API.post('/api/admin/users', data); },
        updateUser(id, data) { return API.put(`/api/admin/users/${id}`, data); },
        deleteUser(id) { return API.del(`/api/admin/users/${id}`); },
        getModules() { return API.get('/api/admin/modules'); },
        updateModule(id, data) { return API.put(`/api/admin/modules/${id}`, data); },
        getStats() { return API.get('/api/admin/stats'); },
        getRoles() { return API.get('/api/admin/roles'); },
    },
};
