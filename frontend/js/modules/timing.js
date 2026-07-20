/**
 * 择时分析模块 - Professional Terminal
 */
const TimingModule = {
    chartInstance: null,
    analysisResults: [],

    async init() {
        await this.runAnalysis('sh000001');
        this.bindEvents();
    },

    bindEvents() {
        document.getElementById('btnTimingAnalyze')?.addEventListener('click', () => this.runAnalysis());
    },

    switchChartPeriod() {
        const period = document.getElementById('timingChartPeriod')?.value || 'day';
        const result = this.analysisResults.find(r => r.period === period) || this.analysisResults[0];
        if (result) this.renderChart(result);
    },

    async runAnalysis(stockCode) {
        const code = stockCode || document.getElementById('timingStockCode')?.value?.trim() || 'sh000001';
        const checkboxes = document.querySelectorAll('#timingPeriodCheckboxes input:checked');
        let periods = Array.from(checkboxes).map(cb => cb.value);
        if (periods.length === 0) periods = ['day', '60min', '30min'];

        document.getElementById('timingStatus').textContent = '分析中...';

        try {
            const res = await API.timing.analyze({ stock_code: code, periods });
            if (res.code === 200) {
                this.analysisResults = res.data.results;
                this.renderResults(res.data);
            }
        } catch (e) {
            Utils.toast('择时分析失败: ' + e.message, 'error');
            document.getElementById('timingStatus').textContent = '分析失败';
        }
    },

    renderResults(data) {
        document.getElementById('timingStockName').textContent = `标的: ${data.stock_code}`;
        document.getElementById('timingStatus').textContent = `分析时间: ${data.analyzed_at}`;

        const s = data.summary;
        document.getElementById('timingBuyCount').textContent = s.buy_signals;
        document.getElementById('timingSellCount').textContent = s.sell_signals;
        document.getElementById('timingHoldCount').textContent = s.hold_signals;

        const overall = s.buy_signals > s.sell_signals ? '偏多 ↑' : (s.sell_signals > s.buy_signals ? '偏空 ↓' : '中性 →');
        document.getElementById('timingOverall').textContent = overall;

        // Period detail cards
        const detailContainer = document.getElementById('timingDetailCards');
        detailContainer.innerHTML = data.results.map(r => {
            const cls = r.signal === 'buy' ? 'buy' : (r.signal === 'sell' ? 'sell' : 'hold');
            return `
            <div class="period-signal-card">
                <div class="ps-period">${r.period}</div>
                <div class="ps-signal" style="color:${cls==='buy'?'var(--green)':(cls==='sell'?'var(--red)':'var(--amber)')}">${r.signal_text}</div>
                <div class="ps-macd">MACD ${r.macd} | DIF ${r.dif}</div>
                <div class="ps-confidence">置信度 ${r.confidence}%</div>
            </div>`;
        }).join('');

        // Chart
        const firstResult = data.results.find(r => r.period === 'day') || data.results[0];
        if (firstResult) this.renderChart(firstResult);
    },

    renderChart(result) {
        const chartDom = document.getElementById('timingChart');
        if (!chartDom || typeof echarts === 'undefined') return;
        if (this.chartInstance) this.chartInstance.dispose();

        this.chartInstance = echarts.init(chartDom, 'dark');
        const dates = result.kline_data.map(d => d[0]);
        const kdata = result.kline_data.map(d => [d[1], d[2], d[3], d[4]]);
        const volumes = result.kline_data.map(d => d[5]);

        this.chartInstance.setOption({
            backgroundColor: 'transparent',
            tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
            grid: [
                { left: '8%', right: '2%', top: '3%', height: '55%' },
                { left: '8%', right: '2%', top: '68%', height: '22%' }
            ],
            xAxis: [
                { type: 'category', data: dates, gridIndex: 0, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#1a2030' } }, axisTick: { show: false } },
                { type: 'category', data: dates, gridIndex: 1, axisLabel: { rotate: 30, fontSize: 9, color: '#5e6878' }, axisLine: { lineStyle: { color: '#1a2030' } }, axisTick: { show: false } }
            ],
            yAxis: [
                { type: 'value', gridIndex: 0, scale: true, splitLine: { lineStyle: { color: '#1a2030' } }, axisLabel: { color: '#5e6878', fontSize: 10 } },
                { type: 'value', gridIndex: 1, splitLine: { show: false }, axisLabel: { color: '#5e6878', fontSize: 9 } }
            ],
            series: [
                {
                    name: 'K线', type: 'candlestick', data: kdata, xAxisIndex: 0, yAxisIndex: 0,
                    itemStyle: { color: '#f0444f', color0: '#10b981', borderColor: '#f0444f', borderColor0: '#10b981' }
                },
                {
                    name: '成交量', type: 'bar', data: volumes, xAxisIndex: 1, yAxisIndex: 1,
                    itemStyle: { color: params => kdata[params.dataIndex] ? (kdata[params.dataIndex][1] > kdata[params.dataIndex][0] ? 'rgba(240,68,79,.5)' : 'rgba(16,185,129,.5)') : 'rgba(94,104,120,.3)' }
                }
            ]
        });

        const ro = new ResizeObserver(() => this.chartInstance?.resize());
        ro.observe(chartDom);
    }
};
