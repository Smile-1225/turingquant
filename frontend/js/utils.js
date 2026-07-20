/**
 * 图灵量化 - 工具函数
 */
const Utils = {
    // Toast通知
    toast(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; setTimeout(() => toast.remove(), 300); }, duration);
    },

    // 显示加载
    showLoading(containerId) {
        const el = document.getElementById(containerId);
        if (el) el.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';
    },

    // 显示空状态
    showEmpty(containerId, message = '暂无数据') {
        const el = document.getElementById(containerId);
        if (el) el.innerHTML = `<div class="empty-state"><div class="empty-icon">📊</div><p>${message}</p></div>`;
    },

    // 格式化数字
    formatNumber(num, decimals = 2) {
        if (num === null || num === undefined) return '--';
        return Number(num).toLocaleString('zh-CN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
    },

    // 格式化百分比
    formatPercent(num, decimals = 2) {
        if (num === null || num === undefined) return '--';
        const val = Number(num);
        const sign = val > 0 ? '+' : '';
        return `${sign}${val.toFixed(decimals)}%`;
    },

    // 格式化金额
    formatAmount(num) {
        if (num === null || num === undefined) return '--';
        const v = Number(num);
        if (v >= 1e8) return (v / 1e8).toFixed(2) + '亿';
        if (v >= 1e4) return (v / 1e4).toFixed(2) + '万';
        return v.toFixed(2);
    },

    // 格式化日期
    formatDate(dateStr) {
        if (!dateStr) return '--';
        const d = new Date(dateStr);
        return d.toLocaleDateString('zh-CN');
    },

    formatDateTime(dateStr) {
        if (!dateStr) return '--';
        const d = new Date(dateStr);
        return d.toLocaleString('zh-CN');
    },

    // 信号类型样式
    getSignalClass(signalType) {
        const map = { 'buy': 'signal-buy', 'sell': 'signal-sell', 'hold': 'signal-hold' };
        return map[signalType] || '';
    },

    getSignalText(signalType) {
        const map = { 'buy': '买入 ↑', 'sell': '卖出 ↓', 'hold': '观望 →' };
        return map[signalType] || signalType;
    },

    // 角色名称
    getRoleName(role) {
        const names = { 1: '超级管理员', 2: '普通管理员', 3: 'B端客户', 4: 'C端客户' };
        return names[role] || '未知';
    },

    getRoleTag(role) {
        const tags = { 1: 'tag-purple', 2: 'tag-blue', 3: 'tag-cyan', 4: 'tag-green' };
        return tags[role] || 'tag-green';
    },

    // Debounce
    debounce(fn, delay = 300) {
        let timer;
        return function(...args) { clearTimeout(timer); timer = setTimeout(() => fn.apply(this, args), delay); };
    },

    // 时间
    timeAgo(dateStr) {
        const now = new Date();
        const d = new Date(dateStr);
        const diff = Math.floor((now - d) / 1000);
        if (diff < 60) return '刚刚';
        if (diff < 3600) return Math.floor(diff / 60) + '分钟前';
        if (diff < 86400) return Math.floor(diff / 3600) + '小时前';
        return Math.floor(diff / 86400) + '天前';
    },

    // Escape HTML
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};
