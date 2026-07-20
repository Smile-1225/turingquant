# -*- coding: utf-8 -*-
"""
图灵量化投资网站 - 配置文件
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Flask 配置
SECRET_KEY = 'turing-quant-secret-key-2024-change-in-production'
JWT_SECRET_KEY = 'turing-jwt-secret-key-2024'
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1小时
JWT_REFRESH_TOKEN_EXPIRES = 604800  # 7天

# 数据库配置
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "turing_quant.db")}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# CORS配置
CORS_ORIGINS = ['*']

# 服务器配置
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True

# 公司信息
COMPANY_NAME = '图灵量化'
APP_NAME = '智能投资决策系统'
FULL_APP_NAME = f'{COMPANY_NAME}{APP_NAME}'

# 上传文件配置
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 角色定义
ROLES = {
    1: '超级管理员',
    2: '普通管理员',
    3: 'B端客户（券商/基金）',
    4: 'C端客户',
}

# 模块定义
MODULES = {
    'dashboard': {'name': '系统首页', 'default_min_role': 4},
    'timing': {'name': '择时分析', 'default_min_role': 3},
    'review_ztb': {'name': '涨停板复盘', 'default_min_role': 3},
    'review_industry': {'name': '行业复盘', 'default_min_role': 3},
    'signals': {'name': '买卖点信号', 'default_min_role': 3},
    'strategy_performance': {'name': '策略业绩展示', 'default_min_role': 4},
    'strategy_quant': {'name': '量化策略', 'default_min_role': 3},
    'future': {'name': '更多功能', 'default_min_role': 4},
    'admin_users': {'name': '用户管理(后台)', 'default_min_role': 1},
    'admin_modules': {'name': '模块管理(后台)', 'default_min_role': 1},
}

# 指数代码列表
INDEX_LIST = [
    {'code': 'sh000001', 'name': '上证指数'},
    {'code': 'sh000016', 'name': '上证50'},
    {'code': 'sz399300', 'name': '沪深300'},
    {'code': 'sz399905', 'name': '中证500'},
    {'code': 'sz399006', 'name': '创业板指'},
    {'code': 'sh000688', 'name': '科创50'},
]

# 数据源配置
ZTB_DATA_SOURCE = 'eastmoney'  # 涨停板数据源: eastmoney / ths / sina
