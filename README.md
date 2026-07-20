# 图灵量化投资决策系统 v2.0

商务科技风格的量化投资网站，基于 Python Flask + Vanilla JS SPA 架构。

## 项目结构

```
webapp/
├── backend/                    # Flask 后端
│   ├── app.py                  # 主应用入口
│   ├── config.py               # 配置文件
│   ├── database.py             # 数据库初始化
│   ├── models.py               # SQLAlchemy 数据模型
│   ├── auth.py                 # 认证蓝图 (JWT)
│   ├── admin.py                # 管理后台蓝图
│   ├── api.py                  # 业务 API 蓝图
│   ├── seed.py                 # 种子数据
│   ├── run.py                  # 启动脚本
│   └── requirements.txt        # Python 依赖
└── frontend/                   # 前端 SPA
    ├── index.html              # 主页面
    ├── css/style.css           # 商务科技暗色主题
    └── js/
        ├── app.js              # 主应用控制器
        ├── auth.js             # 认证模块（登录/注册/游客弹窗）
        ├── router.js           # Hash 路由管理
        ├── api.js              # API 请求封装
        ├── utils.js            # 工具函数
        └── modules/
            ├── dashboard.js    # 系统首页仪表盘
            ├── timing.js       # 择时分析（K线图+MACD）
            ├── review.js       # 涨停板复盘 + 行业复盘
            ├── signals.js      # 多周期买卖点信号
            ├── strategy.js     # 策略业绩展示
            └── admin.js        # 管理后台（用户/模块管理）
```

## 快速启动

### 1. 安装依赖
```bash
cd webapp/backend
pip install -r requirements.txt
```

### 2. 启动后端
```bash
python run.py
# 后端运行在 http://localhost:5000
```

### 3. 打开前端
浏览器打开 `webapp/frontend/index.html`
或通过 Flask 静态文件服务访问 `http://localhost:5000`

## 默认账号

| 角色 | 用户名 | 密码 | 手机号 | 权限 |
|------|--------|------|--------|------|
| 超级管理员 | admin | admin123 | 13800000001 | 全部权限 + 后台管理 + 数据上传 |
| 普通管理员 | admin2 | admin123 | 13800000002 | 用户管理 + 模块配置 |
| B端客户 | bclient | bclient123 | 13800000003 | 全部量化功能（券商/基金同行） |
| C端客户 | cclient | cclient123 | 13800000004 | 基础功能 |

## 功能模块

### 1. 用户认证与权限
- 游客10分钟弹窗提醒注册
- 手机号必填注册
- 三级管理员权限体系
- JWT Token 认证

### 2. 择时分析
- MACD 拐点信号多周期分析
- ECharts K线图
- 支持指数和个股

### 3. 复盘功能
- 涨停板复盘（连板数/板块/封单统计）
- 行业复盘（涨跌排行/资金流向/强弱指数）

### 4. 买卖点信号
- 多周期信号展示（30min/60min/日线/周线）
- 信号筛选和搜索

### 5. 策略业绩展示
- 6大策略历史业绩
- 净值曲线对比图
- 夏普比率/最大回撤/胜率

### 6. 管理后台
- 用户CRUD管理
- 模块可见性配置（按角色隐藏）
- 系统数据统计

## 免费部署方案

### 后端 - Render (免费)
1. 注册 https://render.com
2. 创建 Web Service，连接 Git 仓库
3. Start Command: `cd webapp/backend && gunicorn app:create_app() -b 0.0.0.0:$PORT`
4. 获得免费域名如 `turingquant.onrender.com`

### 前端 - Vercel (免费)
1. 注册 https://vercel.com
2. 部署 `webapp/frontend` 目录
3. 修改 `js/api.js` 中 `BASE_URL` 为 Render 后端地址
4. 获得免费域名如 `turingquant.vercel.app`

### 免费域名绑定
- Freenom (dot.tk/.ml/.ga): 注册免费顶级域名
- 或将 Vercel 域名 CNAME 到自定义域名

## API 接口概览

| 端点 | 方法 | 说明 | 认证 |
|------|------|------|------|
| /api/health | GET | 健康检查 | 否 |
| /api/auth/register | POST | 用户注册 | 否 |
| /api/auth/login | POST | 用户登录 | 否 |
| /api/auth/profile | GET/PUT | 个人信息 | JWT |
| /api/dashboard | GET | 仪表盘数据 | 否 |
| /api/strategies | GET | 策略列表 | 否 |
| /api/timing/analyze | POST | 择时分析 | JWT |
| /api/review/limit-up | GET | 涨停板复盘 | JWT |
| /api/review/industry | GET | 行业复盘 | JWT |
| /api/signals | GET | 买卖点信号 | JWT |
| /api/admin/users | CRUD | 用户管理 | JWT+管理员 |
| /api/admin/modules | GET/PUT | 模块可见性 | JWT+管理员 |
