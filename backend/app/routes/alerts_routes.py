from flask import Blueprint, jsonify, request
from app.services.alerts import get_all_alerts, update_alert_status
from flasgger import swag_from

alerts_bp = Blueprint('alerts_bp', __name__, url_prefix='/api/alerts')

@alerts_bp.route('/', methods=['GET'])
@swag_from({
    'summary': '获取告警列表',
    'description': '支持分页和按状态过滤告警信息',
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'default': 1,
            'description': '页码'
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'default': 10,
            'description': '每页数量'
        },
        {
            'name': 'status',
            'in': 'query',
            'type': 'string',
            'description': '按状态过滤 (e.g., unprocessed, viewed, resolved)'
        }
    ],
    'responses': {
        200: {
            'description': '告警列表',
            'schema': {
                'type': 'object',
                'properties': {
                    'alerts': {'type': 'array', 'items': {'$ref': '#/definitions/Alert'}},
                    'total': {'type': 'integer'},
                    'pages': {'type': 'integer'},
                    'current_page': {'type': 'integer'}
                }
            }
        }
    }
})
def list_alerts():
    """获取告警列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', None, type=str)
    
    paginated_alerts = get_all_alerts(page=page, per_page=per_page, status=status)
    
    return jsonify({
        'alerts': [alert.to_dict() for alert in paginated_alerts.items],
        'total': paginated_alerts.total,
        'pages': paginated_alerts.pages,
        'current_page': paginated_alerts.page
    })

@alerts_bp.route('/<int:alert_id>/status', methods=['PATCH'])
@swag_from({
    'summary': '更新告警状态',
    'parameters': [
        {
            'name': 'alert_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'description': '新的状态 (e.g., viewed, resolved)'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': '更新成功', 'schema': {'$ref': '#/definitions/Alert'}},
        404: {'description': '告警未找到'},
        400: {'description': '请求无效'}
    }
})
def change_alert_status(alert_id):
    """更新告警状态"""
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Missing status in request body'}), 400
        
    new_status = data['status']
    alert = update_alert_status(alert_id, new_status)
    
    if alert:
        return jsonify(alert.to_dict())
    else:
        return jsonify({'error': 'Alert not found or update failed'}), 404

# 在 flasgger 中定义 Alert 模型，以便于 API 文档生成
def register_swag_definitions(swagger):
    if swagger.template is None:
        swagger.template = {'definitions': {}}
    if 'definitions' not in swagger.template:
        swagger.template['definitions'] = {}

    alert_definition = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "timestamp": {"type": "string", "format": "date-time"},
            "event_type": {"type": "string"},
            "details": {"type": "string"},
            "status": {"type": "string"},
            "video_path": {"type": "string"},
            "frame_snapshot_path": {"type": "string"}
        }
    }
    swagger.template['definitions']['Alert'] = alert_definition 