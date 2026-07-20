/**
 * 买卖点信号模块 - Professional Table
 */
const SignalsModule = {
    currentPage: 1,
    async init() {
        await this.loadSignals();
        document.getElementById('btnRefreshSignals')?.addEventListener('click', () => this.loadSignals());
        document.getElementById('signalPeriodFilter')?.addEventListener('change', () => this.loadSignals());
        document.getElementById('signalTypeFilter')?.addEventListener('change', () => this.loadSignals());
        document.getElementById('signalStockFilter')?.addEventListener('input', Utils.debounce(() => this.loadSignals(), 400));
    },
    async loadSignals(page = 1) {
        const period = document.getElementById('signalPeriodFilter')?.value || '';
        const signalType = document.getElementById('signalTypeFilter')?.value || '';
        const stockCode = document.getElementById('signalStockFilter')?.value?.trim() || '';
        const tbody = document.getElementById('signalsTableBody');
        tbody.innerHTML = '<tr><td colspan="8"><div class="spinner-wrap"><div class="spinner"></div></div></td></tr>';
        try {
            const res = await API.signals.getList({ page, per_page: 20, period, signal_type: signalType, stock_code: stockCode });
            if (res.code === 200) this.renderSignals(res.data);
        } catch (e) { Utils.toast('加载失败', 'error'); }
    },
    renderSignals(data) {
        const tbody = document.getElementById('signalsTableBody');
        if (!data.signals || data.signals.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8"><div class="empty-state"><div class="es-icon">↯</div><div class="es-text">暂无匹配信号</div></div></td></tr>';
            return;
        }
        tbody.innerHTML = data.signals.map(s => `
            <tr>
                <td class="mono">${s.stock_code}</td>
                <td>${s.stock_name||'--'}</td>
                <td><span class="tag tag-outline">${s.period||'--'}</span></td>
                <td><span class="signal-pill ${s.signal_type}">${Utils.getSignalText(s.signal_type)}</span></td>
                <td>${s.signal_name||'--'}</td>
                <td class="num">${s.price?Utils.formatNumber(s.price,2):'--'}</td>
                <td class="num">${s.confidence?Utils.formatNumber(s.confidence,1)+'%':'--'}</td>
                <td style="font-size:10px;color:var(--text-tertiary);">${Utils.timeAgo(s.signal_time)}</td>
            </tr>
        `).join('');
        const pc = document.getElementById('signalsPagination');
        if (!pc || data.pages <= 1) { if (pc) pc.innerHTML = ''; return; }
        let h = `<button class="pager-btn" ${data.current_page<=1?'disabled':''} onclick="SignalsModule.loadSignals(${data.current_page-1})">‹ 上一页</button>`;
        h += `<span class="pager-info">${data.current_page} / ${data.pages}</span>`;
        h += `<button class="pager-btn" ${data.current_page>=data.pages?'disabled':''} onclick="SignalsModule.loadSignals(${data.current_page+1})">下一页 ›</button>`;
        pc.innerHTML = h;
    }
};
