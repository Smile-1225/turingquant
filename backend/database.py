# -*- coding: utf-8 -*-
"""
数据库初始化 - 生产环境安全版
"""
import time
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def init_db(app):
    """初始化数据库（幂等，多worker安全）"""
    db.init_app(app)
    bcrypt.init_app(app)

    # 必须在create_all之前导入所有模型
    from models import User, ModuleVisibility, Strategy, SignalRecord, LimitUpRecord, IndustryReview

    with app.app_context():
        # 只创建表（如果不存在），不做种子数据
        db.create_all()

    app.logger.info('[DB] 数据库表初始化完成')


def seed_if_empty(app):
    """仅在数据库为空时执行种子数据（只调用一次）"""
    from models import User

    with app.app_context():
        # 重试机制：应对 SQLite 并发锁
        for attempt in range(5):
            try:
                if User.query.first() is None:
                    from seed import seed_all
                    seed_all()
                    app.logger.info('[Seed] 种子数据初始化完成')
                else:
                    app.logger.info('[Seed] 数据库已有数据，跳过种子')
                return
            except Exception as e:
                if 'database is locked' in str(e) and attempt < 4:
                    time.sleep(1 + attempt * 0.5)
                    continue
                raise
