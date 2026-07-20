# -*- coding: utf-8 -*-
"""
Render 生产环境入口
"""
import sys
import os

# 确保 backend 在 Python 路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
