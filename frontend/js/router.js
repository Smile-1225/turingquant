/**
 * Hash路由管理 - Professional Terminal
 */
class Router {
    constructor() {
        this.routes = {};
        this.currentRoute = null;
        this.moduleVisibility = [];
        this.init();
    }

    init() {
        window.addEventListener('hashchange', () => this.handleRoute());
        window.addEventListener('load', () => this.handleRoute());
    }

    register(path, config) { this.routes[path] = config; }

    navigate(path) { window.location.hash = '#' + path; }

    refresh() { this.handleRoute(); }

    async handleRoute() {
        const hash = window.location.hash.slice(1) || 'dashboard';
        const route = this.routes[hash];
        if (!route) { this.navigate('dashboard'); return; }
        this.currentRoute = hash;

        // Check access
        if (!App.auth.canAccess(route.minRole)) {
            Utils.toast('此功能需要登录或更高权限', 'warning');
            if (!App.auth.isLoggedIn) App.auth.showLoginModal();
            return;
        }

        // Update sidepanel active state
        document.querySelectorAll('.sidepanel-item').forEach(item => {
            item.classList.toggle('active', item.dataset.route === hash);
        });

        // Show/hide page sections
        document.querySelectorAll('.workspace > section').forEach(s => {
            const id = s.id;
            if (id === 'page-' + hash) {
                s.style.display = 'flex';
                s.style.flexDirection = 'column';
                s.style.gap = '14px';
            } else {
                s.style.display = 'none';
            }
        });

        // Special case for dashboard (no flex column)
        const dashboardSection = document.getElementById('page-dashboard');
        if (dashboardSection) {
            dashboardSection.style.display = hash === 'dashboard' ? 'contents' : 'none';
        }

        // Execute init
        if (route.init && typeof route.init === 'function') {
            try { await route.init(); } catch (e) { console.error('Route init error:', e); }
        }
    }

    async loadModuleVisibility() {
        try {
            const res = await API.public.getModules();
            if (res.code === 200) {
                this.moduleVisibility = res.data;
                this.applyModuleVisibility();
            }
        } catch (e) { console.error('Load modules failed:', e); }
    }

    applyModuleVisibility() {
        // 所有模块始终显示在侧栏中（管理员可在后台全局禁用）
        // 权限检查在点击时触发，游客会看到登录提示
        this.moduleVisibility.forEach(mod => {
            const navItem = document.querySelector(`.sidepanel-item[data-module="${mod.module_key}"]`);
            if (navItem) navItem.style.display = mod.is_enabled ? 'flex' : 'none';
        });
    }

    isModuleVisible(moduleKey) {
        const mod = this.moduleVisibility.find(m => m.module_key === moduleKey);
        if (!mod) return true;
        return mod.is_enabled;
    }
}
