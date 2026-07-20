# -*- coding: utf-8 -*-
"""
图灵量化投资网站 - Flask主应用 (统一部署版)
同时服务前端静态文件和后端API
"""
import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from config import SECRET_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from config import JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRES, UPLOAD_FOLDER
from database import init_db

# 前端静态文件目录
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')


def create_app():
    """创建Flask应用工厂"""
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

    # 基础配置
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_TOKEN_EXPIRES
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # 上传目录
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # CORS支持
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # 初始化数据库
    init_db(app)

    # 注册蓝图
    from auth import auth_bp
    from admin import admin_bp
    from api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # ===== 前端静态文件路由 =====
    @app.route('/')
    def index():
        return send_from_directory(FRONTEND_DIR, 'index.html')

    @app.route('/css/<path:filename>')
    def serve_css(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), filename)

    @app.route('/js/<path:filename>')
    def serve_js(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), filename)

    @app.route('/js/modules/<path:filename>')
    def serve_js_modules(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'js', 'modules'), filename)

    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'assets'), filename)

    # 健康检查
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'app': '图灵量化投资决策系统', 'version': '2.0.0'}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
