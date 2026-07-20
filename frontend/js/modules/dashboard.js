/**
 * 仪表盘首页 - Professional Terminal Style
 */
const DashboardModule = {
    async init() {
        try {
            const res = await API.getDashboard();
            if (res.code === 200) this.render(res.data);
        } catch (e) {
            Utils.toast('加载仪表盘失败', 'error');
        }
    },

    render(data) {
        this.renderQuotes(data.indices);
        this.renderStats(data.stats);
        this.renderSignals(data.latest_signals);
        this.renderStrategies(data.top_strategies);
    },

    renderQuotes(indices) {
        const strip = document.getElementById('dashboardQuoteStrip');
        if (!strip || !indices) return;

        strip.innerHTML = indices.map(idx => {
            const up = idx.change >= 0;
            return `
            <div class="quote-item" onclick="App.router.navigate('timing')">
                <div class="q-name">${idx.name}</div>
                <div class="q-code mono">${idx.code}</div>
                <div class="q-price">${Utils.formatNumber(idx.price, 2)}</div>
                <div class="q-change ${up ? 'up' : 'down'}">${up ? '+' : ''}${Utils.formatNumber(idx.change, 2)} (${up ? '+' : ''}${Utils.formatPercent(idx.change_pct)})</div>
            </div>`;
        }).join('');
    },

    renderStats(stats) {
        document.getElementById('statStrategyCount').textContent = stats.strategy_count || 0;
        document.getElementById('statSignalCount').textContent = stats.signal_count || 0;
        document.getElementById('statLimitUp').textContent = stats.today_limit_up || 0;
        document.getElementById('statSentiment').textContent = stats.market_sentiment || '--';
    },

    renderSignals(signals) {
        const tbody = document.getElementById('dashboardSignalsTable');
        if (!signals || signals.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state"><div class="es-icon">↯</div><div class="es-text">暂无信号</div></div></td></tr>';
            return;
        }
        tbody.innerHTML = signals.map(s => `
            <tr>
                <td class="mono">${s.stock_code}</td>
                <td>${s.stock_name || '--'}</td>
                <td>${s.period || '--'}</td>
                <td><span class="signal-pill ${s.signal_type}">${Utils.getSignalText(s.signal_type)}</span></td>
                <td class="num">${s.price ? Utils.formatNumber(s.price, 2) : '--'}</td>
            </tr>
        `).join('');
    },

    renderStrategies(strategies) {
        const container = document.getElementById('dashboardStrategies');
        if (!strategies || strategies.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="es-icon">⌬</div><div class="es-text">暂无数据</div></div>';
            return;
        }
        container.innerHTML = strategies.map((s, i) => `
            <div class="strategy-card-pro" onclick="App.router.navigate('strategies')" style="margin-bottom:10px;">
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
    }
};
