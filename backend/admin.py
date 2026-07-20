# -*- coding: utf-8 -*-
"""
管理员后台蓝图
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import db
from models import User, ModuleVisibility, Strategy
from auth import token_required, role_required
from config import ROLES

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ==================== 用户管理 ====================

@admin_bp.route('/users', methods=['GET'])
@role_required(2)
def get_users(current_user):
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')

    query = User.query
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.phone.contains(search)) |
            (User.nickname.contains(search))
        )

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'code': 200,
        'data': {
            'users': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
        }
    })


@admin_bp.route('/users', methods=['POST'])
@role_required(2)
def create_user(current_user):
    """管理员创建用户"""
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请提供用户信息'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '123456').strip()
    phone = data.get('phone', '').strip()
    role = data.get('role', 4)

    if not username or not phone:
        return jsonify({'code': 400, 'message': '用户名和手机号为必填项'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400

    if User.query.filter_by(phone=phone).first():
        return jsonify({'code': 400, 'message': '手机号已存在'}), 400

    if role not in ROLES:
        return jsonify({'code': 400, 'message': '无效的角色'}), 400

    # 超级管理员只能由超级管理员创建
    if role == 1 and current_user.role != 1:
        return jsonify({'code': 403, 'message': '只有超级管理员才能创建超级管理员账号'}), 403

    user = User(
        username=username,
        phone=phone,
        nickname=data.get('nickname', username),
        email=data.get('email', ''),
        role=role,
        is_active=True,
        created_at=datetime.now(),
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({'code': 200, 'message': '用户创建成功', 'data': user.to_dict()})


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@role_required(2)
def update_user(current_user, user_id):
    """更新用户信息"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请提供更新信息'}), 400

    # 不能修改自己的角色
    if user.id == current_user.id and 'role' in data:
        return jsonify({'code': 400, 'message': '不能修改自己的角色'}), 400

    # 超级管理员保护
    if user.role == 1 and current_user.role != 1:
        return jsonify({'code': 403, 'message': '只有超级管理员才能修改超级管理员信息'}), 403

    if 'username' in data:
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user_id:
            return jsonify({'code': 400, 'message': '用户名已被占用'}), 400
        user.username = data['username']

    if 'phone' in data:
        existing = User.query.filter_by(phone=data['phone']).first()
        if existing and existing.id != user_id:
            return jsonify({'code': 400, 'message': '手机号已被占用'}), 400
        user.phone = data['phone']

    if 'nickname' in data:
        user.nickname = data['nickname']
    if 'email' in data:
        user.email = data['email']
    if 'role' in data:
        if data['role'] not in ROLES:
            return jsonify({'code': 400, 'message': '无效的角色'}), 400
        # 超级管理员只能由超级管理员设置
        if data['role'] == 1 and current_user.role != 1:
            return jsonify({'code': 403, 'message': '只有超级管理员才能设置超级管理员角色'}), 403
        user.role = data['role']
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'password' in data and data['password']:
        user.set_password(data['password'])

    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': user.to_dict()})


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@role_required(2)
def delete_user(current_user, user_id):
    """删除用户"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    if user.id == current_user.id:
        return jsonify({'code': 400, 'message': '不能删除自己的账号'}), 400

    if user.role == 1:
        return jsonify({'code': 403, 'message': '不能删除超级管理员'}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({'code': 200, 'message': '用户已删除'})


# ==================== 模块可见性管理 ====================

@admin_bp.route('/modules', methods=['GET'])
@role_required(2)
def get_modules(current_user):
    """获取模块可见性配置"""
    modules = ModuleVisibility.query.all()
    return jsonify({
        'code': 200,
        'data': [m.to_dict() for m in modules]
    })


@admin_bp.route('/modules/<int:module_id>', methods=['PUT'])
@role_required(2)
def update_module(current_user, module_id):
    """更新模块可见性"""
    module = ModuleVisibility.query.get(module_id)
    if not module:
        return jsonify({'code': 404, 'message': '模块不存在'}), 404

    data = request.get_json()
    if 'min_role' in data:
        if data['min_role'] not in ROLES:
            return jsonify({'code': 400, 'message': '无效的角色级别'}), 400
        module.min_role = data['min_role']
    if 'is_enabled' in data:
        module.is_enabled = data['is_enabled']

    module.updated_at = datetime.now()
    db.session.commit()

    return jsonify({'code': 200, 'message': '更新成功', 'data': module.to_dict()})


# ==================== 数据统计 ====================

@admin_bp.route('/stats', methods=['GET'])
@role_required(2)
def get_stats(current_user):
    """获取后台统计数据"""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_strategies = Strategy.query.count()
    roles_count = {}
    for role_id, role_name in ROLES.items():
        roles_count[role_name] = User.query.filter_by(role=role_id).count()

    return jsonify({
        'code': 200,
        'data': {
            'total_users': total_users,
            'active_users': active_users,
            'total_strategies': total_strategies,
            'roles_count': roles_count,
        }
    })


# ==================== 角色列表 ====================

@admin_bp.route('/roles', methods=['GET'])
@token_required
def get_roles(current_user):
    """获取角色列表"""
    return jsonify({
        'code': 200,
        'data': [{'id': k, 'name': v} for k, v in ROLES.items()]
    })
