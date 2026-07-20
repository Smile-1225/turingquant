# -*- coding: utf-8 -*-
"""
种子数据 - 初始化默认数据
"""
from datetime import datetime
from database import db
from models import User, ModuleVisibility, Strategy, SignalRecord, LimitUpRecord, IndustryReview
from config import MODULES, ROLES


def seed_users():
    """创建默认用户"""
    default_users = [
        {
            'username': 'admin',
            'password': 'admin123',
            'phone': '13800000001',
            'nickname': '超级管理员',
            'role': 1,
        },
        {
            'username': 'admin2',
            'password': 'admin123',
            'phone': '13800000002',
            'nickname': '普通管理员',
            'role': 2,
        },
        {
            'username': 'bclient',
            'password': 'bclient123',
            'phone': '13800000003',
            'nickname': '券商演示账号',
            'role': 3,
        },
        {
            'username': 'cclient',
            'password': 'cclient123',
            'phone': '13800000004',
            'nickname': '普通用户',
            'role': 4,
        },
    ]

    for u in default_users:
        if not User.query.filter_by(username=u['username']).first():
            user = User(
                username=u['username'],
                phone=u['phone'],
                nickname=u['nickname'],
                role=u['role'],
                is_active=True,
                created_at=datetime.now(),
            )
            user.set_password(u['password'])
            db.session.add(user)

    db.session.commit()
    print('[Seed] 默认用户创建完成')


def seed_modules():
    """初始化模块可见性配置"""
    for key, info in MODULES.items():
        if not ModuleVisibility.query.filter_by(module_key=key).first():
            module = ModuleVisibility(
                module_key=key,
                module_name=info['name'],
                min_role=info['default_min_role'],
                is_enabled=True,
            )
            db.session.add(module)

    db.session.commit()
    print('[Seed] 模块可见性配置完成')


def seed_strategies():
    """初始化演示策略数据"""
    demo_strategies = [
        {
            'name': '三星选股策略',
            'description': '综合基本面、技术面和资金面三维度精选优质标的，结合市场情绪进行动态调仓。适用于震荡市和趋势市。',
            'category': '选股策略',
            'annual_return': 32.5,
            'max_drawdown': -15.8,
            'sharpe_ratio': 1.85,
            'win_rate': 62.3,
            'performance_json': _generate_performance_data(32.5, -15.8),
            'parameters_json': '{"buy_method":"t_wap","sell_method":"base_sell","hold_plan":"W_0","select_count":5}',
            'sort_order': 1,
        },
        {
            'name': '保守策略选股',
            'description': '以低估值蓝筹股为核心，注重安全边际和持续分红能力。适合稳健型投资者，回撤控制优异。',
            'category': '选股策略',
            'annual_return': 18.7,
            'max_drawdown': -8.2,
            'sharpe_ratio': 2.12,
            'win_rate': 71.5,
            'performance_json': _generate_performance_data(18.7, -8.2),
            'parameters_json': '{"buy_method":"t_wap","sell_method":"base_sell","hold_plan":"W_0","select_count":5}',
            'sort_order': 2,
        },
        {
            'name': '稳健策略选股',
            'description': '基于多因子模型，在控制风险的前提下追求稳健收益。兼顾成长性与估值合理性。',
            'category': '选股策略',
            'annual_return': 25.3,
            'max_drawdown': -12.4,
            'sharpe_ratio': 1.96,
            'win_rate': 66.8,
            'performance_json': _generate_performance_data(25.3, -12.4),
            'parameters_json': '{"buy_method":"t_wap","sell_method":"base_sell","hold_plan":"W_0","select_count":5}',
            'sort_order': 3,
        },
        {
            'name': '积极策略选股',
            'description': '聚焦高成长性标的，捕捉市场趋势性机会。适合风险承受能力较强的投资者。',
            'category': '选股策略',
            'annual_return': 45.2,
            'max_drawdown': -22.6,
            'sharpe_ratio': 1.72,
            'win_rate': 58.4,
            'performance_json': _generate_performance_data(45.2, -22.6),
            'parameters_json': '{"buy_method":"t_wap","sell_method":"base_sell","hold_plan":"W_0","select_count":5}',
            'sort_order': 4,
        },
        {
            'name': '轮动策略选股',
            'description': '基于行业轮动和风格轮动模型，动态切换投资组合。利用A股市场结构性机会。',
            'category': '轮动策略',
            'annual_return': 38.9,
            'max_drawdown': -18.3,
            'sharpe_ratio': 1.91,
            'win_rate': 64.7,
            'performance_json': _generate_performance_data(38.9, -18.3),
            'parameters_json': '{"buy_method":"t_wap","sell_method":"base_sell","hold_plan":"W_0","select_count":5}',
            'sort_order': 5,
        },
        {
            'name': 'E策略选股',
            'description': '结合机器学习模型的量化选股策略，动态学习市场规律，自适应调整选股因子权重。',
            'category': 'AI策略',
            'annual_return': 52.8,
            'max_drawdown': -19.5,
            'sharpe_ratio': 2.28,
            'win_rate': 69.1,
            'performance_json': _generate_performance_data(52.8, -19.5),
            'parameters_json': '{"buy_method":"t_wap","sell_method":"base_sell","hold_plan":"W_0","select_count":5}',
            'sort_order': 6,
        },
    ]

    for s in demo_strategies:
        if not Strategy.query.filter_by(name=s['name']).first():
            strategy = Strategy(
                name=s['name'],
                description=s['description'],
                category=s['category'],
                annual_return=s['annual_return'],
                max_drawdown=s['max_drawdown'],
                sharpe_ratio=s['sharpe_ratio'],
                win_rate=s['win_rate'],
                performance_json=s['performance_json'],
                parameters_json=s['parameters_json'],
                is_active=True,
                is_public=True,
                sort_order=s['sort_order'],
                created_at=datetime.now(),
            )
            db.session.add(strategy)

    db.session.commit()
    print('[Seed] 演示策略数据创建完成')


def seed_signals():
    """初始化演示信号数据"""
    import random
    random.seed(42)

    stocks = [
        ('sh000001', '上证指数'), ('sz399006', '创业板指'),
        ('sz399905', '中证500'), ('sh000688', '科创50'),
        ('sh600519', '贵州茅台'), ('sz000858', '五粮液'),
        ('sh601318', '中国平安'), ('sz300750', '宁德时代'),
    ]
    periods = ['30min', '60min', 'day', 'week']
    signal_types = ['buy', 'sell', 'hold']
    signal_names = {
        'buy': ['MACD金叉', '均线突破', '底部拐点', '放量突破'],
        'sell': ['MACD死叉', '均线跌破', '顶部拐点', '缩量回调'],
        'hold': ['趋势延续', '震荡整理'],
    }

    now = datetime.now()
    for i in range(20):
        stock = random.choice(stocks)
        s_type = random.choice(signal_types)
        s_name = random.choice(signal_names[s_type])

        signal = SignalRecord(
            stock_code=stock[0],
            stock_name=stock[1],
            period=random.choice(periods),
            signal_type=s_type,
            signal_name=s_name,
            price=round(random.uniform(10, 2000), 2),
            confidence=round(random.uniform(60, 95), 1),
            signal_time=now,
            description=f'{stock[1]}在{random.choice(periods)}周期出现{s_name}信号',
            created_at=now,
        )
        db.session.add(signal)

    db.session.commit()
    print('[Seed] 演示信号数据创建完成')


def seed_limit_up():
    """初始化涨停板演示数据"""
    import random
    random.seed(123)

    sectors = ['人工智能', '新能源汽车', '半导体', '光伏', '医药', '消费电子', '机器人', '低空经济']
    reasons = ['政策利好', '业绩大增', '订单中标', '技术创新', '重组预期', '涨价概念', '热点题材', '行业拐点']

    today = datetime.now().strftime('%Y-%m-%d')
    for i in range(30):
        code_suffix = str(600000 + i * 17).zfill(6)
        record = LimitUpRecord(
            trade_date=today,
            stock_code=f'sh{code_suffix}',
            stock_name=f'涨停股_{i+1}',
            consecutive_days=random.randint(1, 7),
            first_limit_time=f'09:{random.randint(30, 55):02d}',
            last_limit_time=f'{random.choice([10, 11, 13, 14])}:{random.randint(0, 59):02d}',
            open_times=random.randint(0, 3),
            limit_reason=random.choice(reasons),
            turnover_rate=round(random.uniform(1.5, 25.0), 2),
            limit_amount=round(random.uniform(500, 50000), 0),
            market_cap=round(random.uniform(10, 500), 1),
            sector=random.choice(sectors),
            created_at=datetime.now(),
        )
        db.session.add(record)

    db.session.commit()
    print('[Seed] 涨停板演示数据创建完成')


def seed_industry():
    """初始化行业复盘演示数据"""
    import random
    random.seed(456)

    industries = [
        ('半导体', '电子'), ('人工智能', '计算机'), ('新能源汽车', '汽车'),
        ('光伏设备', '电力设备'), ('创新药', '医药生物'), ('白酒', '食品饮料'),
        ('证券', '非银金融'), ('银行', '银行'), ('军工', '国防军工'),
        ('消费电子', '电子'), ('游戏', '传媒'), ('机器人', '机械设备'),
        ('低空经济', '交通运输'), ('数据要素', '计算机'), ('CXO', '医药生物'),
        ('电力', '公用事业'), ('煤炭', '采掘'), ('航运', '交通运输'),
        ('房地产', '房地产'), ('建筑材料', '建筑材料'),
    ]

    today = datetime.now().strftime('%Y-%m-%d')
    for i, (ind_name, ind_code) in enumerate(industries):
        change = round(random.uniform(-5, 8), 2)
        review = IndustryReview(
            trade_date=today,
            industry_code=ind_code,
            industry_name=ind_name,
            industry_level=2,
            change_pct=change,
            volume=round(random.uniform(100, 5000), 0),
            amount=round(random.uniform(50, 800), 1),
            turnover_rate=round(random.uniform(0.5, 12), 2),
            strength_index=round(50 + change * random.uniform(2, 5), 1),
            leading_stock=f'龙头股_{i+1}',
            fund_flow=round(random.uniform(-50, 100), 1),
            created_at=datetime.now(),
        )
        db.session.add(review)

    db.session.commit()
    print('[Seed] 行业复盘演示数据创建完成')


def _generate_performance_data(annual_return, max_drawdown):
    """生成模拟净值曲线JSON数据"""
    import json
    import random
    random.seed(int(annual_return * 100 + abs(max_drawdown) * 100))

    # 生成12个月的模拟净值数据
    months = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06',
              '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12']
    nav = 1.0
    data = {'dates': [], 'nav': [], 'benchmark_nav': []}

    monthly_return = (1 + annual_return / 100) ** (1/12) - 1
    benchmark_monthly = 0.005  # 基准月收益约6%年化

    b_nav = 1.0
    for i, month in enumerate(months):
        nav *= (1 + monthly_return + random.uniform(-0.03, 0.03))
        b_nav *= (1 + benchmark_monthly + random.uniform(-0.02, 0.02))
        data['dates'].append(month)
        data['nav'].append(round(nav, 4))
        data['benchmark_nav'].append(round(b_nav, 4))

    return json.dumps(data)


def seed_all():
    """执行所有种子数据初始化"""
    try:
        seed_users()
        seed_modules()
        seed_strategies()
        seed_signals()
        seed_limit_up()
        seed_industry()
        print('[Seed] 所有种子数据初始化完成')
    except Exception as e:
        db.session.rollback()
        print(f'[Seed] 种子数据初始化失败: {e}')
        raise
