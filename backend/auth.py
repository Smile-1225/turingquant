# -*- coding: utf-8 -*-
"""
认证蓝图 - 登录、注册、权限管理
"""
import re
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from database import db, bcrypt
from models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def create_token(user_id, role):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 1)),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')


def token_required(f):
    """JWT验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')

        if auth_header.startswith('Bearer '):
            token = auth_header[7:]

        if not token:
            return jsonify({'code': 401, 'message': '请先登录'}), 401

        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user or not current_user.is_active:
                return jsonify({'code': 401, 'message': '用户不存在或已被禁用'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'code': 401, 'message': '登录已过期，请重新登录'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'code': 401, 'message': '无效的认证令牌'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def role_required(min_role):
    """角色权限装饰器"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(current_user, *args, **kwargs):
            if current_user.role > min_role:
                return jsonify({'code': 403, 'message': '权限不足'}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请提供注册信息'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    phone = data.get('phone', '').strip()

    # 验证必填字段
    if not username or not password or not phone:
        return jsonify({'code': 400, 'message': '用户名、密码和手机号为必填项'}), 400

    # 验证用户名长度
    if len(username) < 2 or len(username) > 50:
        return jsonify({'code': 400, 'message': '用户名长度为2-50个字符'}), 400

    # 验证密码长度
    if len(password) < 6:
        return jsonify({'code': 400, 'message': '密码长度至少6位'}), 400

    # 验证手机号格式（中国大陆手机号）
    if not re.match(r'^1[3-9]\d{9}$', phone):
        return jsonify({'code': 400, 'message': '请输入正确的11位手机号'}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': '用户名已被注册'}), 400

    # 检查手机号是否已存在
    if User.query.filter_by(phone=phone).first():
        return jsonify({'code': 400, 'message': '手机号已被注册'}), 400

    # 创建用户（默认C端客户）
    user = User(
        username=username,
        phone=phone,
        nickname=username,
        role=4
    )
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()

        token = create_token(user.id, user.role)

        return jsonify({
            'code': 200,
            'message': '注册成功',
            'data': {
                'token': token,
                'user': user.to_public_dict()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'注册失败: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录 - 支持用户名或手机号登录"""
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请提供登录信息'}), 400

    login_id = data.get('username', '').strip()  # 可以是用户名或手机号
    password = data.get('password', '').strip()

    if not login_id or not password:
        return jsonify({'code': 400, 'message': '请输入账号和密码'}), 400

    # 支持用户名或手机号登录
    user = User.query.filter(
        (User.username == login_id) | (User.phone == login_id)
    ).first()

    if not user:
        return jsonify({'code': 400, 'message': '账号或密码错误'}), 400

    if not user.check_password(password):
        return jsonify({'code': 400, 'message': '账号或密码错误'}), 400

    if not user.is_active:
        return jsonify({'code': 403, 'message': '账号已被禁用，请联系管理员'}), 403

    # 更新最后登录时间
    user.last_login = datetime.now()
    db.session.commit()

    token = create_token(user.id, user.role)

    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'token': token,
            'user': user.to_public_dict()
        }
    })


@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """获取当前用户信息"""
    return jsonify({
        'code': 200,
        'data': current_user.to_dict()
    })


@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """更新用户资料"""
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请提供更新信息'}), 400

    if 'nickname' in data:
        current_user.nickname = data['nickname'][:50]
    if 'email' in data:
        current_user.email = data['email'][:100]

    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '更新成功', 'data': current_user.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """修改密码"""
    data = request.get_json()
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return jsonify({'code': 400, 'message': '请提供旧密码和新密码'}), 400

    if not current_user.check_password(old_password):
        return jsonify({'code': 400, 'message': '旧密码错误'}), 400

    if len(new_password) < 6:
        return jsonify({'code': 400, 'message': '新密码长度至少6位'}), 400

    current_user.set_password(new_password)
    db.session.commit()

    return jsonify({'code': 200, 'message': '密码修改成功'})


@auth_bp.route('/visitor-check', methods=['GET'])
def visitor_check():
    """游客检查 - 返回是否需要弹出注册提示"""
    return jsonify({
        'code': 200,
        'message': '欢迎访问图灵量化投资决策系统',
        'data': {
            'is_visitor': True,
            'reminder_interval': 600  # 10分钟 = 600秒
        }
    })
