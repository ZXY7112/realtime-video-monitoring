from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask import jsonify  
from flask_sqlalchemy import SQLAlchemy 
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():

    # 解决 "OMP: Error #15" 警告
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    
    app = Flask(__name__)
    CORS(app)  # 启用跨域支持
    swagger = Swagger(app) # 初始化 Flasgger
    
    app.config.from_object('app.config.Config')

    db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)

    # 定义上传目录路径
    UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    print(f"上传目录: {UPLOADS_DIR}")
    
    # 注册蓝图
    from app.routes.api import api_bp
    from app.routes.video import video_bp
    from app.routes.config import config_bp
    from app.routes.face import face_bp
    from app.routes.auth import auth_bp 
    # 在蓝图导入部分添加
    from app.routes.main import main_bp  # 添加这行

    # 在蓝图注册部分添加
    app.register_blueprint(main_bp)  # 添加这行

    app.register_blueprint(api_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(face_bp)
    app.register_blueprint(auth_bp)
    
    add_jwt_handlers(jwt)
    
    # 添加全局错误处理
    add_error_handlers(app)
    with app.app_context():
        try:
            # 使用SQLAlchemy 2.0+的正确语法
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT 1"))
                print("✅ MySQL数据库连接成功")
        except Exception as e:
            print(f"❌ MySQL数据库连接失败: {e}")
            # 打印详细的错误堆栈信息，便于调试
            import traceback
            print(traceback.format_exc())



    return app 

def add_jwt_handlers(jwt):
    """添加JWT错误处理"""
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "error": "无效的令牌",
            "message": str(error)
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "error": "缺少授权令牌",
            "message": "请求需要有效的JWT令牌"
        }), 401
        
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "令牌已过期",
            "message": "请重新登录获取新令牌"
        }), 401

def add_error_handlers(app):
    """添加全局错误处理"""
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "error": "资源未找到",
            "message": str(error)
        }), 404
        
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "服务器内部错误",
            "message": "请稍后再试或联系管理员"
        }), 500