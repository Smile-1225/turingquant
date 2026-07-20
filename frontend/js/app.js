/**
 * 图灵量化 - 主应用控制器 v2.0 Professional Terminal
 */
const App = {
    auth: null,
    router: null,

    async init() {
        this.auth = new AuthManager();
        this.router = new Router();
        this.registerRoutes();
        await this.router.loadModuleVisibility();
        this.updateConnectionStatus();
        setInterval(() => this.updateConnectionStatus(), 30000);
        console.log('🚀 图灵量化 · 智能投资决策终端 v2.0');
    },

    registerRoutes() {
        this.router.register('dashboard', {
            minRole: 99,
            init: DashboardModule.init.bind(DashboardModule),
        });

        this.router.register('timing', {
            minRole: 3,
            init: TimingModule.init.bind(TimingModule),
        });

        this.router.register('review', {
            minRole: 3,
            init: ReviewModule.init.bind(ReviewModule),
        });

        this.router.register('industry-review', {
            minRole: 3,
            init: () => {
                document.getElementById('page-industry-review').style.display = 'flex';
                document.getElementById('page-industry-review').style.flexDirection = 'column';
                document.getElementById('page-industry-review').style.gap = '14px';
                ReviewModule.init().then(() => ReviewModule.loadIndustry());
            },
        });

        this.router.register('signals', {
            minRole: 3,
            init: SignalsModule.init.bind(SignalsModule),
        });

        this.router.register('strategies', {
            minRole: 4,
            init: StrategyModule.init.bind(StrategyModule),
        });

        this.router.register('quant-strategy', { minRole: 3, init: () => {} });

        this.router.register('future', { minRole: 99, init: () => {} });

        this.router.register('admin', {
            minRole: 2,
            init: AdminModule.init.bind(AdminModule),
        });
    },

    async updateConnectionStatus() {
        try {
            const res = await fetch(API.BASE_URL + '/api/health');
            const data = await res.json();
            const dot = document.getElementById('statusDot');
            const text = document.getElementById('statusText');
            if (data.status === 'ok') {
                dot.classList.remove('offline');
                text.textContent = '在线';
            } else {
                dot.classList.add('offline');
                text.textContent = '异常';
            }
        } catch (e) {
            document.getElementById('statusDot').classList.add('offline');
            document.getElementById('statusText').textContent = '离线';
        }
    },
};

document.addEventListener('DOMContentLoaded', () => App.init());
