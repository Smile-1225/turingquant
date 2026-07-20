/**
 * 复盘模块 - Professional Terminal Panels
 */
const ReviewModule = {
    currentZtbPage: 1,
    industryChart: null,

    async init() {
        await this.loadLimitUp();
        this.bindEvents();
    },

    bindEvents() {
        document.getElementById('btnRefreshZtb')?.addEventListener('click', () => this.loadLimitUp());
        document.getElementById('btnRefreshIndustry')?.addEventListener('click', () => this.loadIndustry());
        document.getElementById('industrySortBy')?.addEventListener('change', () => this.loadIndustry());
        document.getElementById('industryDate')?.addEventListener('change', () => this.loadIndustry());
    },

    async loadLimitUp(page = 1) {
        const sector = document.getElementById('ztbSectorFilter')?.value || '';
        const date = document.getElementById('ztbDate')?.value || new Date().toISOString().slice(0, 10);
        document.getElementById('ztbDate').value = date;

        try {
            const res = await API.review.getLimitUp({ page, per_page: 30, sector, date });
            if (res.code === 200) {
                this.renderLimitUp(res.data);
                this.currentZtbPage = res.data.current_page;
            }
        } catch (e) { Utils.toast('加载涨停板数据失败', 'error'); }
    },

    renderLimitUp(data) {
        document.getElementById('ztbTotalCount').textContent = data.statistics.total_count;
        document.getElementById('ztbTopSector').textContent = this._topSector(data.statistics.by_sector) || '--';
        document.getElementById('ztbMaxConsecutive').textContent = this._maxConsecutive(data.statistics.by_consecutive) || '--';

        const tbody = document.getElementById('ztbTableBody');
        if (!data.records || data.records.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9"><div class="empty-state"><div class="es-icon">⇧</div><div class="es-text">暂无涨停数据</div></div></td></tr>';
            return;
        }

        tbody.innerHTML = data.records.map(r => `
            <tr>
                <td class="mono">${r.stock_code}</td>
                <td>${r.stock_name}</td>
                <td><span class="tag ${r.consecutive_days>=3?'tag-red':(r.consecutive_days>=2?'tag-amber':'tag-blue')}">${r.consecutive_days}连板</span></td>
                <td>${r.first_limit_time||'--'}</td>
                <td>${r.open_times}</td>
                <td>${r.limit_reason||'--'}</td>
                <td class="num">${r.turnover_rate?Utils.formatPercent(r.turnover_rate,2):'--'}</td>
                <td class="num">${r.limit_amount?Utils.formatNumber(r.limit_amount/10000,1)+'万':'--'}</td>
                <td><span class="tag tag-outline">${r.sector||'--'}</span></td>
            </tr>
        `).join('');

        this._renderPagination('ztbPagination', data, (p) => this.loadLimitUp(p));
    },

    async loadIndustry() {
        const sortBy = document.getElementById('industrySortBy')?.value || 'change_pct';
        const date = document.getElementById('industryDate')?.value || new Date().toISOString().slice(0, 10);
        document.getElementById('industryDate').value = date;

        try {
            const res = await API.review.getIndustry({ sort_by: sortBy, date, level: 2 });
            if (res.code === 200) this.renderIndustry(res.data);
        } catch (e) { Utils.toast('加载行业数据失败', 'error'); }
    },

    renderIndustry(data) {
        const s = data.statistics;
        document.getElementById('indAvgChange').textContent = Utils.formatPercent(s.avg_change, 2);
        document.getElementById('indUpCount').textContent = s.up_count;
        document.getElementById('indDownCount').textContent = s.down_count;
        document.getElementById('indTotalCount').textContent = s.total_count;
        document.getElementById('indTopGainer').textContent = s.top_gainer ? `${s.top_gainer.industry_name} +${s.top_gainer.change_pct}%` : '--';
        document.getElementById('indTopLoser').textContent = s.top_loser ? `${s.top_loser.industry_name} ${s.top_loser.change_pct}%` : '--';

        const tbody = document.getElementById('industryTableBody');
        if (!data.records || data.records.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7"><div class="empty-state"><div class="es-icon">⊡</div><div class="es-text">暂无数据</div></div></td></tr>';
            return;
        }

        tbody.innerHTML = data.records.map(r => `
            <tr>
                <td>${r.industry_name}</td>
                <td class="${r.change_pct>=0?'up':'down'} num" style="font-weight:600;">${Utils.formatPercent(r.change_pct,2)}</td>
                <td class="num">${r.volume?Utils.formatNumber(r.volume,0):'--'}</td>
                <td class="num">${r.amount?Utils.formatNumber(r.amount,1)+'亿':'--'}</td>
                <td class="num">${r.turnover_rate?Utils.formatPercent(r.turnover_rate,2):'--'}</td>
                <td class="num">${r.strength_index?Utils.formatNumber(r.strength_index,1):'--'}</td>
                <td class="num ${r.fund_flow>=0?'up':'down'}">${r.fund_flow?Utils.formatNumber(r.fund_flow,1)+'亿':'--'}</td>
            </tr>
        `).join('');

        this._drawIndustryChart(data.records);
    },

    _drawIndustryChart(records) {
        const dom = document.getElementById('industryChart');
        if (!dom || typeof echarts === 'undefined') return;
        if (this.industryChart) this.industryChart.dispose();
        this.industryChart = echarts.init(dom);

        const combined = [...records.slice(-10), ...records.slice(0, 10).reverse()];
        this.industryChart.setOption({
            backgroundColor: 'transparent',
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            grid: { left: '3%', right: '5%', top: '3%', bottom: '3%', containLabel: true },
            xAxis: { type: 'value', axisLabel: { formatter: '{value}%', fontSize: 9, color: '#5e6878' }, splitLine: { lineStyle: { color: '#1a2030' } } },
            yAxis: { type: 'category', data: combined.map(r => r.industry_name), axisLabel: { fontSize: 10, color: '#949db0' }, axisLine: { show: false }, axisTick: { show: false } },
            series: [{ type: 'bar', data: combined.map(r => r.change_pct), itemStyle: { color: p => p.value >= 0 ? '#10b981' : '#f0444f', borderRadius: [0, 2, 2, 0] } }]
        });

        const ro = new ResizeObserver(() => this.industryChart?.resize());
        ro.observe(dom);
    },

    _topSector(bySector) {
        if (!bySector) return null;
        let top = null, max = 0;
        for (const [k, v] of Object.entries(bySector)) { if (v > max) { max = v; top = k; } }
        return top ? `${top} (${max}只)` : null;
    },

    _maxConsecutive(byCons) {
        if (!byCons) return null;
        for (let i = 7; i >= 1; i--) { if (byCons[`${i}连板`] > 0) return `${i}连板 (${byCons[`${i}连板`]}只)`; }
        return null;
    },

    _renderPagination(id, data, cb) {
        const c = document.getElementById(id);
        if (!c || data.pages <= 1) { if (c) c.innerHTML = ''; return; }
        let h = `<button class="pager-btn" ${data.current_page<=1?'disabled':''} onclick="ReviewModule.currentZtbPage=${data.current_page-1};ReviewModule.loadLimitUp(ReviewModule.currentZtbPage)">‹ 上一页</button>`;
        h += `<span class="pager-info">${data.current_page} / ${data.pages}</span>`;
        h += `<button class="pager-btn" ${data.current_page>=data.pages?'disabled':''} onclick="ReviewModule.currentZtbPage=${data.current_page+1};ReviewModule.loadLimitUp(ReviewModule.currentZtbPage)">下一页 ›</button>`;
        c.innerHTML = h;
    }
};
