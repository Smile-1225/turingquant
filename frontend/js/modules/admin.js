/**
 * 管理后台 - Professional Admin Panel
 */
const AdminModule = {
    usersPage: 1, roles: {},

    async init() {
        if (!App.auth.isLoggedIn || App.auth.getUserRole() > 2) {
            Utils.toast('权限不足', 'error'); App.router.navigate('dashboard'); return;
        }
        await Promise.all([this.loadStats(), this.loadUsers(), this.loadModules(), this.loadRoles()]);
        this.bindEvents();
    },

    bindEvents() {
        document.getElementById('adminUserSearch')?.addEventListener('input', Utils.debounce(() => { this.usersPage = 1; this.loadUsers(); }, 400));
        document.getElementById('btnAdminAddUser')?.addEventListener('click', () => this.showAddUserModal());
        document.getElementById('btnAddUserSubmit')?.addEventListener('click', () => this.createUser());
        document.getElementById('adminAddUserClose')?.addEventListener('click', () => this.closeAddUserModal());
        document.getElementById('adminAddUserOverlay')?.addEventListener('click', e => { if (e.target === e.currentTarget) this.closeAddUserModal(); });
    },

    switchTab(tab, btn) {
        document.querySelectorAll('#page-admin .tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('adminTabUsers').style.display = tab === 'users' ? 'flex' : 'none';
        document.getElementById('adminTabModules').style.display = tab === 'modules' ? 'flex' : 'none';
        if (tab === 'modules') this.loadModules();
    },

    async loadStats() {
        try {
            const res = await API.admin.getStats();
            if (res.code === 200) {
                document.getElementById('adminTotalUsers').textContent = res.data.total_users;
                document.getElementById('adminActiveUsers').textContent = res.data.active_users;
                document.getElementById('adminTotalStrategies').textContent = res.data.total_strategies;
            }
        } catch (e) { /* silent */ }
    },

    async loadUsers() {
        try {
            const res = await API.admin.getUsers({ page: this.usersPage, per_page: 15, search: document.getElementById('adminUserSearch')?.value || '' });
            if (res.code === 200) this.renderUsers(res.data);
        } catch (e) { Utils.toast('加载用户失败', 'error'); }
    },

    renderUsers(data) {
        const tbody = document.getElementById('adminUsersTableBody');
        if (!data.users || data.users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8"><div class="empty-state"><div class="es-text">暂无用户</div></div></td></tr>';
            return;
        }
        tbody.innerHTML = data.users.map(u => `
            <tr>
                <td class="mono">${u.id}</td><td>${Utils.escapeHtml(u.username)}</td><td>${u.phone}</td><td>${u.nickname||'--'}</td>
                <td><span class="tag ${Utils.getRoleTag(u.role)}">${Utils.getRoleName(u.role)}</span></td>
                <td><span class="tag ${u.is_active?'tag-green':'tag-red'}">${u.is_active?'正常':'禁用'}</span></td>
                <td style="font-size:10px;">${u.created_at||'--'}</td>
                <td>
                    <button class="btn btn-sm btn-ghost" onclick="AdminModule.editUser(${u.id})">✏️</button>
                    <button class="btn btn-sm btn-ghost" onclick="AdminModule.deleteUser(${u.id})" ${u.role===1?'disabled':''} style="color:var(--red);">🗑</button>
                </td>
            </tr>
        `).join('');
        const pc = document.getElementById('adminUsersPagination');
        if (data.pages <= 1) { pc.innerHTML = ''; return; }
        pc.innerHTML = `<button class="pager-btn" ${data.current_page<=1?'disabled':''} onclick="AdminModule.usersPage=${data.current_page-1};AdminModule.loadUsers()">‹ 上一页</button>
            <span class="pager-info">${data.current_page} / ${data.pages}</span>
            <button class="pager-btn" ${data.current_page>=data.pages?'disabled':''} onclick="AdminModule.usersPage=${data.current_page+1};AdminModule.loadUsers()">下一页 ›</button>`;
    },

    editUser(userId) {
        const newRole = prompt('设置新角色:\n1=超级管理员  2=普通管理员  3=B端客户  4=C端客户');
        if (!newRole || !['1','2','3','4'].includes(newRole)) return;
        API.admin.updateUser(userId, { role: parseInt(newRole) })
            .then(() => { Utils.toast('更新成功', 'success'); this.loadUsers(); })
            .catch(e => Utils.toast('更新失败: ' + e.message, 'error'));
    },

    async deleteUser(userId) {
        if (!confirm('确定删除该用户？')) return;
        try { await API.admin.deleteUser(userId); Utils.toast('已删除', 'success'); this.loadUsers(); this.loadStats(); }
        catch (e) { Utils.toast('删除失败: ' + e.message, 'error'); }
    },

    showAddUserModal() { document.getElementById('adminAddUserOverlay').classList.add('show'); },
    closeAddUserModal() { document.getElementById('adminAddUserOverlay').classList.remove('show'); document.getElementById('adminAddUserForm').reset(); },

    async createUser() {
        const u = document.getElementById('newUsername').value.trim();
        const p = document.getElementById('newPassword').value.trim();
        const ph = document.getElementById('newPhone').value.trim();
        const r = parseInt(document.getElementById('newRole').value);
        if (!u || !p || !ph) { Utils.toast('请填写所有必填字段', 'warning'); return; }
        try { await API.admin.createUser({ username: u, password: p, phone: ph, role: r }); Utils.toast('创建成功', 'success'); this.closeAddUserModal(); this.loadUsers(); this.loadStats(); }
        catch (e) { Utils.toast('创建失败: ' + e.message, 'error'); }
    },

    async loadRoles() {
        try { const res = await API.admin.getRoles(); if (res.code === 200) { this.roles = {}; res.data.forEach(r => { this.roles[r.id] = r.name; }); } }
        catch (e) { /* silent */ }
    },

    async loadModules() {
        try {
            const res = await API.admin.getModules();
            if (res.code === 200) {
                document.getElementById('adminModulesList').innerHTML = res.data.map(m => `
                    <tr>
                        <td class="mono">${m.module_key}</td><td>${m.module_name}</td>
                        <td>
                            <select onchange="AdminModule._updateRole(${m.id},this.value)" class="pt-select" style="width:130px;">
                                <option value="1" ${m.min_role===1?'selected':''}>超级管理员</option>
                                <option value="2" ${m.min_role===2?'selected':''}>普通管理员</option>
                                <option value="3" ${m.min_role===3?'selected':''}>B端客户</option>
                                <option value="4" ${m.min_role===4?'selected':''}>C端客户</option>
                            </select>
                        </td>
                        <td>
                            <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-size:11px;">
                                <input type="checkbox" ${m.is_enabled?'checked':''} onchange="AdminModule._toggle(${m.id},this.checked)">
                                <span class="tag ${m.is_enabled?'tag-green':'tag-red'}">${m.is_enabled?'启用':'禁用'}</span>
                            </label>
                        </td>
                    </tr>
                `).join('');
            }
        } catch (e) { Utils.toast('加载模块配置失败', 'error'); }
    },

    async _updateRole(id, role) {
        try { await API.admin.updateModule(id, { min_role: parseInt(role) }); Utils.toast('已更新', 'success'); }
        catch (e) { Utils.toast('更新失败', 'error'); }
    },

    async _toggle(id, enabled) {
        try { await API.admin.updateModule(id, { is_enabled: enabled }); Utils.toast(enabled ? '模块已启用' : '模块已禁用', 'success'); this.loadModules(); }
        catch (e) { Utils.toast('更新失败', 'error'); }
    },
};
