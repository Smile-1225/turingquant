# -*- coding: utf-8 -*-
"""
数据库初始化
"""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def init_db(app):
    """初始化数据库"""
    db.init_app(app)
    bcrypt.init_app(app)

    # 必须在create_all之前导入所有模型
    from models import User, ModuleVisibility, Strategy, SignalRecord, LimitUpRecord, IndustryReview

    with app.app_context():
        db.create_all()
        # 导入并执行种子数据
        from seed import seed_all
        seed_all()
