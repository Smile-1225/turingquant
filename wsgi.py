# -*- coding: utf-8 -*-
"""
Render 生产环境入口 - 使用 --preload 模式，worker fork 前初始化
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_app
from backend.database import seed_if_empty

app = create_app()

# 用 --preload 时这里只会执行一次，安全地初始化种子数据
with app.app_context():
    seed_if_empty(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
