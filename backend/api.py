# -*- coding: utf-8 -*-
"""
RESTful API 蓝图 - 主要业务接口
"""
import json
import random
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import db
from models import (
    User, ModuleVisibility, Strategy, SignalRecord,
    LimitUpRecord, IndustryReview
)
from auth import token_required
from config import INDEX_LIST

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ==================== 公开接口 ====================

@api_bp.route('/public/modules', methods=['GET'])
def get_public_modules():
    """获取公开的模块可见性配置（前端初始化用）"""
    modules = ModuleVisibility.query.all()
    return jsonify({
        'code': 200,
        'data': [m.to_dict() for m in modules]
    })


@api_bp.route('/public/indices', methods=['GET'])
def get_public_indices():
    """获取指数列表"""
    return jsonify({
        'code': 200,
        'data': INDEX_LIST
    })


# ==================== 择时模块 ====================

@api_bp.route('/timing/analyze', methods=['POST'])
@token_required
def timing_analyze(current_user):
    """
    择时分析
    接收股票代码和周期参数，返回MACD信号分析结果
    """
    data = request.get_json() or {}
    stock_code = data.get('stock_code', 'sh000001')
    periods = data.get('periods', ['day', '60min', '30min'])

    # 模拟MACD分析结果（实际应调用Trade_Signal.py的逻辑）
    results = []
    for period in periods:
        macd_val = round(random.uniform(-0.5, 0.8), 3)
        signal = 'buy' if macd_val > 0.2 else ('sell' if macd_val < -0.2 else 'hold')
        results.append({
            'period': period,
            'macd': macd_val,
            'dif': round(macd_val * random.uniform(0.8, 1.2), 3),
            'dea': round(macd_val * random.uniform(0.6, 1.0), 3),
            'signal': signal,
            'signal_text': {'buy': '看多 ↑', 'sell': '看空 ↓', 'hold': '观望 →'}[signal],
            'confidence': round(random.uniform(60, 95), 1),
            'kline_data': _generate_kline_data(period, 60),
        })

    return jsonify({
        'code': 200,
        'data': {
            'stock_code': stock_code,
            'results': results,
            'summary': {
                'buy_signals': sum(1 for r in results if r['signal'] == 'buy'),
                'sell_signals': sum(1 for r in results if r['signal'] == 'sell'),
                'hold_signals': sum(1 for r in results if r['signal'] == 'hold'),
            },
            'analyzed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
    })


def _generate_kline_data(period, count):
    """生成模拟K线数据"""
    import random
    random.seed(hash(period) % 10000)

    base = random.uniform(10, 100)
    data = []
    for i in range(count):
        open_p = base * (1 + random.uniform(-0.03, 0.03))
        close_p = open_p * (1 + random.uniform(-0.02, 0.02))
        high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.01))
        low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.01))
        data.append([
            f'2024-{((i//22)+1):02d}-{((i%22)+1):02d}',
            round(open_p, 2), round(close_p, 2),
            round(low_p, 2), round(high_p, 2),
            random.randint(10000, 1000000)
        ])
        base = close_p
    return data


# ==================== 复盘功能 ====================

@api_bp.route('/review/limit-up', methods=['GET'])
@token_required
def review_limit_up(current_user):
    """涨停板复盘"""
    trade_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)
    sector = request.args.get('sector', '')

    query = LimitUpRecord.query.filter_by(trade_date=trade_date)
    if sector:
        query = query.filter_by(sector=sector)

    pagination = query.order_by(
        LimitUpRecord.consecutive_days.desc(),
        LimitUpRecord.limit_amount.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    # 统计
    all_records = LimitUpRecord.query.filter_by(trade_date=trade_date).all()
    sectors_stat = {}
    for r in all_records:
        if r.sector not in sectors_stat:
            sectors_stat[r.sector] = 0
        sectors_stat[r.sector] += 1

    consecutive_stat = {f'{i}连板': 0 for i in range(1, 8)}
    for r in all_records:
        key = f'{min(r.consecutive_days, 7)}连板'
        consecutive_stat[key] = consecutive_stat.get(key, 0) + 1

    return jsonify({
        'code': 200,
        'data': {
            'records': [r.to_dict() for r in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'statistics': {
                'total_count': len(all_records),
                'by_sector': sectors_stat,
                'by_consecutive': consecutive_stat,
            }
        }
    })


@api_bp.route('/review/industry', methods=['GET'])
@token_required
def review_industry(current_user):
    """行业复盘"""
    trade_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    sort_by = request.args.get('sort_by', 'change_pct')
    sort_order = request.args.get('sort_order', 'desc')
    level = request.args.get('level', 2, type=int)

    # 白名单验证排序字段
    allowed_sort = ['change_pct', 'volume', 'amount', 'turnover_rate', 'strength_index', 'fund_flow']
    if sort_by not in allowed_sort:
        sort_by = 'change_pct'

    sort_column = getattr(IndustryReview, sort_by)
    if sort_order == 'asc':
        sort_column = sort_column.asc()
    else:
        sort_column = sort_column.desc()

    records = IndustryReview.query.filter_by(
        trade_date=trade_date, industry_level=level
    ).order_by(sort_column).all()

    # 统计
    changes = [r.change_pct for r in records]
    avg_change = sum(changes) / len(changes) if changes else 0
    up_count = sum(1 for c in changes if c > 0)
    down_count = sum(1 for c in changes if c < 0)

    return jsonify({
        'code': 200,
        'data': {
            'records': [r.to_dict() for r in records],
            'statistics': {
                'avg_change': round(avg_change, 2),
                'up_count': up_count,
                'down_count': down_count,
                'total_count': len(records),
                'top_gainer': records[0].to_dict() if records and records[0].change_pct > 0 else None,
                'top_loser': records[-1].to_dict() if records and records[-1].change_pct < 0 else None,
            }
        }
    })


# ==================== 买卖点信号 ====================

@api_bp.route('/signals', methods=['GET'])
@token_required
def get_signals(current_user):
    """获取买卖点信号列表"""
    stock_code = request.args.get('stock_code', '')
    period = request.args.get('period', '')
    signal_type = request.args.get('signal_type', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = SignalRecord.query
    if stock_code:
        query = query.filter(SignalRecord.stock_code.contains(stock_code))
    if period:
        query = query.filter_by(period=period)
    if signal_type:
        query = query.filter_by(signal_type=signal_type)

    pagination = query.order_by(SignalRecord.signal_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'code': 200,
        'data': {
            'signals': [s.to_dict() for s in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
        }
    })


@api_bp.route('/signals/latest', methods=['GET'])
@token_required
def get_latest_signals(current_user):
    """获取最新买卖点信号（仪表盘用）"""
    signals = SignalRecord.query.order_by(
        SignalRecord.signal_time.desc()
    ).limit(10).all()

    # 统计
    buy_count = SignalRecord.query.filter_by(signal_type='buy').count()
    sell_count = SignalRecord.query.filter_by(signal_type='sell').count()

    return jsonify({
        'code': 200,
        'data': {
            'signals': [s.to_dict() for s in signals],
            'stats': {
                'buy_count': buy_count,
                'sell_count': sell_count,
                'total_count': buy_count + sell_count,
            }
        }
    })


# ==================== 策略展示 ====================

@api_bp.route('/strategies', methods=['GET'])
def get_strategies():
    """获取策略列表（策略业绩展示区）"""
    is_public = request.args.get('is_public', 'true')
    query = Strategy.query.filter_by(is_active=True)

    if is_public == 'true':
        query = query.filter_by(is_public=True)

    strategies = query.order_by(Strategy.sort_order.asc()).all()
    return jsonify({
        'code': 200,
        'data': [s.to_dict() for s in strategies]
    })


@api_bp.route('/strategies/<int:strategy_id>', methods=['GET'])
def get_strategy_detail(strategy_id):
    """获取策略详情"""
    strategy = Strategy.query.get(strategy_id)
    if not strategy:
        return jsonify({'code': 404, 'message': '策略不存在'}), 404

    return jsonify({
        'code': 200,
        'data': strategy.to_dict()
    })


# ==================== 仪表盘 ====================

@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """获取仪表盘概览数据"""
    strategy_count = Strategy.query.filter_by(is_active=True, is_public=True).count()
    signal_count = SignalRecord.query.count()
    today_limit_up = LimitUpRecord.query.filter_by(
        trade_date=datetime.now().strftime('%Y-%m-%d')
    ).count()

    # 模拟实时指数数据
    indices = []
    for idx in INDEX_LIST:
        price = round(random.uniform(1500, 5000), 2)
        change = round(random.uniform(-3, 3), 2)
        indices.append({
            'code': idx['code'],
            'name': idx['name'],
            'price': price,
            'change': change,
            'change_pct': round(change * random.uniform(0.05, 0.15), 2),
        })

    # 最新信号
    latest_signals = SignalRecord.query.order_by(
        SignalRecord.signal_time.desc()
    ).limit(5).all()

    # 最佳策略
    top_strategies = Strategy.query.filter_by(is_active=True, is_public=True).order_by(
        Strategy.annual_return.desc()
    ).limit(3).all()

    return jsonify({
        'code': 200,
        'data': {
            'indices': indices,
            'stats': {
                'strategy_count': strategy_count,
                'signal_count': signal_count,
                'today_limit_up': today_limit_up,
                'market_sentiment': random.choice(['乐观', '中性', '谨慎']),
            },
            'latest_signals': [s.to_dict() for s in latest_signals],
            'top_strategies': [s.to_dict() for s in top_strategies],
        }
    })
