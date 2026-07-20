/**
 * 策略模块 - Professional Layout
 */
const StrategyModule = {
    navChart: null,

    async init() {
        await this.loadStrategies();
        document.getElementById('btnRefreshStrategies')?.addEventListener('click', () => this.loadStrategies());
    },

    async loadStrategies() {
        try {
            const res = await API.getStrategies();
            if (res.code === 200) this.renderStrategies(res.data);
        } catch (e) { Utils.toast('加载策略失败', 'error'); }
    },

    renderStrategies(strategies) {
        const container = document.getElementById('strategyCards');
        if (!container) return;

        if (!strategies || strategies.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="es-icon">⌬</div><div class="es-text">暂无策略数据</div></div>';
            return;
        }

        container.innerHTML = strategies.map((s, i) => `
            <div class="strategy-card-pro">
                <div class="sc-rank">0${i+1}</div>
                <div class="sc-name">${s.name}</div>
                <span class="sc-cat purple">${s.category || '策略'}</span>
                <div class="sc-desc">${s.description || ''}</div>
                <div class="sc-metrics">
                    <div class="sc-metric">
                        <div class="sv" style="color:${s.annual_return>=0?'var(--green)':'var(--red)'}">${Utils.formatPercent(s.annual_return,1)}</div>
                        <div class="sl">年化收益</div>
                    </div>
                    <div class="sc-metric">
                        <div class="sv" style="color:var(--red)">${Utils.formatPercent(s.max_drawdown,1)}</div>
                        <div class="sl">最大回撤</div>
                    </div>
                    <div class="sc-metric">
                        <div class="sv" style="color:var(--cyan)">${Utils.formatNumber(s.sharpe_ratio,2)}</div>
                        <div class="sl">夏普比率</div>
                    </div>
                    <div class="sc-metric">
                        <div class="sv" style="color:var(--amber)">${Utils.formatPercent(s.win_rate,1)}</div>
                        <div class="sl">胜率</div>
                    </div>
                </div>
            </div>
        `).join('');

        this.renderNavChart(strategies);
    },

    renderNavChart(strategies) {
        const dom = document.getElementById('strategyNavChart');
        if (!dom || typeof echarts === 'undefined') return;
        if (this.navChart) this.navChart.dispose();
        this.navChart = echarts.init(dom, 'dark');

        const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#f0444f', '#06b6d4'];
        const series = strategies.filter(s => s.performance_json).map((s, i) => {
            let perf;
            try { perf = JSON.parse(s.performance_json); } catch (e) { return null; }
            return { name: s.name, type: 'line', smooth: true, data: perf.nav, symbol: 'none', lineStyle: { width: 2, color: colors[i%colors.length] }, itemStyle: { color: colors[i%colors.length] } };
        }).filter(Boolean);

        // Add benchmark
        if (strategies.length > 0 && strategies[0].performance_json) {
            let perf;
            try { perf = JSON.parse(strategies[0].performance_json); } catch (e) { perf = null; }
            if (perf && perf.benchmark_nav) {
                series.push({ name: '沪深300基准', type: 'line', data: perf.benchmark_nav, symbol: 'none', lineStyle: { type: 'dashed', color: '#5e6878', width: 1.5 }, itemStyle: { color: '#5e6878' } });
            }
        }

        let dates = [];
        if (strategies.length > 0 && strategies[0].performance_json) {
            try { dates = JSON.parse(strategies[0].performance_json).dates; } catch (e) {}
        }

        this.navChart.setOption({
            backgroundColor: 'transparent',
            tooltip: { trigger: 'axis' },
            legend: { data: series.map(s => s.name), bottom: 0, textStyle: { color: '#949db0', fontSize: 10 }, icon: 'roundRect' },
            grid: { left: '6%', right: '4%', top: '5%', bottom: '40px' },
            xAxis: { type: 'category', data: dates, axisLabel: { fontSize: 9, color: '#5e6878' }, axisLine: { lineStyle: { color: '#1a2030' } }, axisTick: { show: false } },
            yAxis: { type: 'value', scale: true, splitLine: { lineStyle: { color: '#1a2030' } }, axisLabel: { fontSize: 9, color: '#5e6878' } },
            series
        });

        const ro = new ResizeObserver(() => this.navChart?.resize());
        ro.observe(dom);
    }
};
