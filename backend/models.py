# -*- coding: utf-8 -*-
"""
数据模型定义
"""
from datetime import datetime
from database import db, bcrypt


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False, index=True)
    nickname = db.Column(db.String(50))
    email = db.Column(db.String(100))
    role = db.Column(db.Integer, nullable=False, default=4)  # 1=超级管理员 2=普通管理员 3=B端 4=C端
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'phone': self.phone,
            'nickname': self.nickname,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None,
        }

    def to_public_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname or self.username,
            'role': self.role,
            'phone': self.phone[:3] + '****' + self.phone[-4:] if self.phone else '',
        }


class ModuleVisibility(db.Model):
    """模块可见性配置"""
    __tablename__ = 'module_visibility'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module_key = db.Column(db.String(50), unique=True, nullable=False)
    module_name = db.Column(db.String(100), nullable=False)
    min_role = db.Column(db.Integer, nullable=False, default=4)  # 最小可见角色
    is_enabled = db.Column(db.Boolean, default=True)  # 全局启用
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'module_key': self.module_key,
            'module_name': self.module_name,
            'min_role': self.min_role,
            'is_enabled': self.is_enabled,
        }


class Strategy(db.Model):
    """策略记录"""
    __tablename__ = 'strategies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # 策略分类
    annual_return = db.Column(db.Float)  # 年化收益率(%)
    max_drawdown = db.Column(db.Float)  # 最大回撤(%)
    sharpe_ratio = db.Column(db.Float)  # 夏普比率
    win_rate = db.Column(db.Float)  # 胜率(%)
    performance_json = db.Column(db.Text)  # 净值曲线JSON
    parameters_json = db.Column(db.Text)  # 策略参数JSON
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)

    creator = db.relationship('User', backref='strategies')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'annual_return': self.annual_return,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'win_rate': self.win_rate,
            'performance_json': self.performance_json,
            'parameters_json': self.parameters_json,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'sort_order': self.sort_order,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None,
        }


class SignalRecord(db.Model):
    """买卖点信号记录"""
    __tablename__ = 'signal_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stock_code = db.Column(db.String(20), nullable=False)
    stock_name = db.Column(db.String(50))
    period = db.Column(db.String(20))  # 30min / 60min / day / week
    signal_type = db.Column(db.String(30))  # buy / sell / hold
    signal_name = db.Column(db.String(50))  # MACD金叉 / 均线突破 / 拐点信号
    price = db.Column(db.Float)
    confidence = db.Column(db.Float)  # 置信度
    signal_time = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'period': self.period,
            'signal_type': self.signal_type,
            'signal_name': self.signal_name,
            'price': self.price,
            'confidence': self.confidence,
            'signal_time': self.signal_time.strftime('%Y-%m-%d %H:%M') if self.signal_time else None,
            'description': self.description,
        }


class LimitUpRecord(db.Model):
    """涨停板记录"""
    __tablename__ = 'limit_up_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trade_date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    stock_code = db.Column(db.String(20), nullable=False)
    stock_name = db.Column(db.String(50))
    consecutive_days = db.Column(db.Integer, default=1)  # 连板数
    first_limit_time = db.Column(db.String(10))  # 首次涨停时间
    last_limit_time = db.Column(db.String(10))  # 最后涨停时间
    open_times = db.Column(db.Integer, default=0)  # 开板次数
    limit_reason = db.Column(db.String(200))  # 涨停原因
    turnover_rate = db.Column(db.Float)  # 换手率
    limit_amount = db.Column(db.Float)  # 封单额(万元)
    market_cap = db.Column(db.Float)  # 流通市值(亿元)
    sector = db.Column(db.String(50))  # 所属板块
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'trade_date': self.trade_date,
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'consecutive_days': self.consecutive_days,
            'first_limit_time': self.first_limit_time,
            'last_limit_time': self.last_limit_time,
            'open_times': self.open_times,
            'limit_reason': self.limit_reason,
            'turnover_rate': self.turnover_rate,
            'limit_amount': self.limit_amount,
            'market_cap': self.market_cap,
            'sector': self.sector,
        }


class IndustryReview(db.Model):
    """行业复盘数据"""
    __tablename__ = 'industry_reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trade_date = db.Column(db.String(10), nullable=False)
    industry_code = db.Column(db.String(20))
    industry_name = db.Column(db.String(50), nullable=False)
    industry_level = db.Column(db.Integer, default=1)  # 1=一级 2=二级
    change_pct = db.Column(db.Float)  # 涨跌幅(%)
    volume = db.Column(db.Float)  # 成交量(万手)
    amount = db.Column(db.Float)  # 成交额(亿元)
    turnover_rate = db.Column(db.Float)  # 换手率(%)
    strength_index = db.Column(db.Float)  # 强弱指数
    leading_stock = db.Column(db.String(200))  # 领涨股
    fund_flow = db.Column(db.Float)  # 资金净流入(亿元)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'trade_date': self.trade_date,
            'industry_code': self.industry_code,
            'industry_name': self.industry_name,
            'industry_level': self.industry_level,
            'change_pct': self.change_pct,
            'volume': self.volume,
            'amount': self.amount,
            'turnover_rate': self.turnover_rate,
            'strength_index': self.strength_index,
            'leading_stock': self.leading_stock,
            'fund_flow': self.fund_flow,
        }
