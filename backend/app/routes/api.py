from flask import Blueprint, jsonify, request

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route("/status", methods=["GET"])
def api_status():
    """API状态检查端点
    ---
    tags:
      - 通用API
    responses:
      200:
        description: API 运行状态.
        schema:
          type: object
          properties:
            status:
              type: string
              example: running
            version:
              type: string
              example: 1.0.0
            message:
              type: string
              example: Video monitoring API is operational
    """
    return jsonify({
        "status": "running",
        "version": "1.0.0",
        "message": "Video monitoring API is operational"
    })

@api_bp.route("/test-alert", methods=["POST"])
def add_test_alert():
    """添加测试告警到内存"""
    from app.services.alerts import add_alert_memory
    data = request.get_json()
    message = data.get('message', '测试告警')
    add_alert_memory(message)
    return jsonify({"status": "success", "message": f"已添加告警: {message}"})

@api_bp.route("/alerts")
def get_alerts():
    """获取告警信息端点
    ---
    tags:
      - 通用API
    responses:
      200:
        description: 当前的警报列表.
        schema:
          type: object
          properties:
            alerts:
              type: array
              items:
                type: string
              description: 警报信息列表.
    """
    from app.services.alerts import get_alerts as get_memory_alerts
    try:
        # 获取内存中的告警信息
        memory_alerts = get_memory_alerts()
        return jsonify({"alerts": memory_alerts})
    except Exception as e:
        print(f"获取内存告警失败: {e}")
        return jsonify({"alerts": []})