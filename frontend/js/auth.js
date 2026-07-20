/**
 * 认证模块 - Professional Terminal
 */
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.isLoggedIn = false;
        this.visitorStartTime = null;
        this.popupInterval = null;
        this.init();
    }

    init() {
        const savedToken = API.getToken();
        const savedUser = localStorage.getItem('tq_user');
        if (savedToken && savedUser) {
            try {
                this.currentUser = JSON.parse(savedUser);
                this.isLoggedIn = true;
                this.updateUI();
            } catch (e) { this.clearAuth(); }
        }
        if (!this.isLoggedIn) this.startVisitorTimer();
        this.bindEvents();
    }

    bindEvents() {
        document.getElementById('userMenuBtn')?.addEventListener('click', (e) => {
            e.stopPropagation();
            document.getElementById('userDropdown').classList.toggle('show');
        });
        document.addEventListener('click', () => {
            document.getElementById('userDropdown').classList.remove('show');
        });
        document.getElementById('modalClose')?.addEventListener('click', () => this.closeModal());
        document.getElementById('modalOverlay')?.addEventListener('click', (e) => {
            if (e.target === e.currentTarget) this.closeModal();
        });

        // Login/Register tab switching
        document.querySelectorAll('#authModal .tab').forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.dataset.tab;
                document.querySelectorAll('#authModal .tab').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById('tab-login').style.display = tab === 'login' ? 'block' : 'none';
                document.getElementById('tab-register').style.display = tab === 'register' ? 'block' : 'none';
            });
        });

        document.getElementById('loginForm')?.addEventListener('submit', (e) => { e.preventDefault(); this.handleLogin(); });
        document.getElementById('registerForm')?.addEventListener('submit', (e) => { e.preventDefault(); this.handleRegister(); });
        document.getElementById('btnLogout')?.addEventListener('click', () => this.logout());
    }

    startVisitorTimer() {
        this.visitorStartTime = Date.now();
        this.popupInterval = setInterval(() => {
            const elapsed = (Date.now() - this.visitorStartTime) / 1000;
            if (elapsed >= 600 && !this.isLoggedIn) {
                this.showRegisterReminder();
                this.visitorStartTime = Date.now();
            }
        }, 30000);
    }

    stopVisitorTimer() {
        if (this.popupInterval) { clearInterval(this.popupInterval); this.popupInterval = null; }
    }

    showRegisterReminder() {
        const visits = parseInt(localStorage.getItem('tq_visit_count') || '0') + 1;
        localStorage.setItem('tq_visit_count', visits.toString());
        const msg = document.getElementById('reminderMessage');
        if (msg) msg.textContent = visits <= 1 ? '欢迎访问图灵量化投资决策终端！' : `您已访问 ${visits} 次，注册即可解锁专业量化分析功能`;
        document.getElementById('reminderOverlay').classList.add('show');
    }

    async handleLogin() {
        const username = document.getElementById('loginUsername').value.trim();
        const password = document.getElementById('loginPassword').value.trim();
        if (!username || !password) { Utils.toast('请输入账号和密码', 'warning'); return; }
        try {
            const btn = document.getElementById('loginSubmitBtn');
            btn.disabled = true; btn.textContent = '登录中...';
            const res = await API.auth.login({ username, password });
            if (res.code === 200) {
                this.setAuth(res.data.token, res.data.user);
                Utils.toast('登录成功', 'success');
                this.closeModal();
                this.stopVisitorTimer();
            }
        } catch (e) { Utils.toast(e.message || '登录失败', 'error'); }
        finally {
            const btn = document.getElementById('loginSubmitBtn');
            btn.disabled = false; btn.textContent = '登 录';
        }
    }

    async handleRegister() {
        const username = document.getElementById('regUsername').value.trim();
        const password = document.getElementById('regPassword').value.trim();
        const phone = document.getElementById('regPhone').value.trim();
        if (!username || !password || !phone) { Utils.toast('请填写所有必填字段', 'warning'); return; }
        if (username.length < 2) { Utils.toast('用户名至少2个字符', 'warning'); return; }
        if (password.length < 6) { Utils.toast('密码至少6位', 'warning'); return; }
        if (!/^1[3-9]\d{9}$/.test(phone)) { Utils.toast('请输入正确的11位手机号', 'warning'); return; }
        try {
            const btn = document.getElementById('registerSubmitBtn');
            btn.disabled = true; btn.textContent = '注册中...';
            const res = await API.auth.register({ username, password, phone });
            if (res.code === 200) {
                this.setAuth(res.data.token, res.data.user);
                Utils.toast('注册成功！欢迎加入图灵量化', 'success');
                this.closeModal();
                this.stopVisitorTimer();
                localStorage.removeItem('tq_visit_count');
            }
        } catch (e) { Utils.toast(e.message || '注册失败', 'error'); }
        finally {
            const btn = document.getElementById('registerSubmitBtn');
            btn.disabled = false; btn.textContent = '注 册';
        }
    }

    setAuth(token, user) {
        API.setToken(token);
        localStorage.setItem('tq_user', JSON.stringify(user));
        this.currentUser = user;
        this.isLoggedIn = true;
        this.updateUI();
        if (App.router) App.router.refresh();
    }

    clearAuth() {
        API.clearToken();
        localStorage.removeItem('tq_user');
        this.currentUser = null;
        this.isLoggedIn = false;
        this.updateUI();
        if (App.router) App.router.refresh();
    }

    logout() {
        document.getElementById('userDropdown').classList.remove('show');
        this.clearAuth();
        this.startVisitorTimer();
        Utils.toast('已退出登录', 'info');
        App.router.navigate('dashboard');
    }

    updateUI() {
        const nameEl = document.getElementById('headerUserName');
        const roleEl = document.getElementById('dropdownUserRole');
        const nameDrop = document.getElementById('dropdownUserName');
        const avatar = document.getElementById('headerAvatar');

        if (this.isLoggedIn && this.currentUser) {
            nameEl.textContent = this.currentUser.nickname || this.currentUser.username;
            roleEl.textContent = Utils.getRoleName(this.currentUser.role);
            nameDrop.textContent = this.currentUser.nickname || this.currentUser.username;

            if (avatar) {
                avatar.textContent = (this.currentUser.nickname || this.currentUser.username)[0].toUpperCase();
                avatar.className = 'avatar';
                if (this.currentUser.role <= 2) avatar.classList.add('admin');
                else if (this.currentUser.role === 3) avatar.classList.add('biz');
            }

            document.getElementById('userLoginPrompt').style.display = 'none';
            document.getElementById('userInfoDisplay').style.display = 'block';

            // Admin menu item
            const adminItem = document.getElementById('menuItemAdmin');
            const sideAdminItem = document.getElementById('sideAdminItem');
            if (adminItem) adminItem.style.display = this.currentUser.role <= 2 ? 'flex' : 'none';
            if (sideAdminItem) sideAdminItem.style.display = this.currentUser.role <= 2 ? 'flex' : 'none';
        } else {
            document.getElementById('userLoginPrompt').style.display = 'block';
            document.getElementById('userInfoDisplay').style.display = 'none';
            const adminItem = document.getElementById('menuItemAdmin');
            const sideAdminItem = document.getElementById('sideAdminItem');
            if (adminItem) adminItem.style.display = 'none';
            if (sideAdminItem) sideAdminItem.style.display = 'none';
        }
    }

    canAccess(minRole) {
        if (!this.isLoggedIn) return minRole === 99 || minRole === 0;
        return this.currentUser && this.currentUser.role <= minRole;
    }

    getUserRole() { return this.currentUser ? this.currentUser.role : 99; }

    showLoginModal() {
        document.querySelectorAll('#authModal .tab').forEach(b => b.classList.remove('active'));
        document.querySelector('#authModal .tab[data-tab="login"]').classList.add('active');
        document.getElementById('tab-login').style.display = 'block';
        document.getElementById('tab-register').style.display = 'none';
        document.getElementById('modalOverlay').classList.add('show');
    }

    showRegisterModal() {
        document.querySelectorAll('#authModal .tab').forEach(b => b.classList.remove('active'));
        document.querySelector('#authModal .tab[data-tab="register"]').classList.add('active');
        document.getElementById('tab-login').style.display = 'none';
        document.getElementById('tab-register').style.display = 'block';
        document.getElementById('modalOverlay').classList.add('show');
    }

    closeModal() {
        document.getElementById('modalOverlay').classList.remove('show');
        document.getElementById('loginForm').reset();
        document.getElementById('registerForm').reset();
    }

    closeReminder() {
        document.getElementById('reminderOverlay').classList.remove('show');
    }
}
