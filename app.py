from flask import Flask, render_template
from models import db, User
from flask_login import LoginManager
import os


def create_app():
    app = Flask(__name__)
    # 用于给 Session 签名，不设这个无法登录。作业里随便写，生产环境要保密。作用是保护cookie不被篡改和伪造
    app.config['SECRET_KEY'] = 'dev-key-for-homework'
    # 告诉 SQLAlchemy 数据库文件存在哪
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['UPLOAD_FOLDER'] = 'uploads'  # 存放 CSV等上传文件等文件夹

    # 初始化插件
    db.init_app(app)

    login_manager = LoginManager()
    # 如果用户没登录就想访问受保护页面，就会踢到视图 'auth.login'
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader # 相当于将该函数传入flask_login中的类
    def load_user(id):
        return db.session.get(User, int(id))

    # 注册 路径Blueprints
    from routes.auth import auth_bp
    from routes.dataset import dataset_bp
    from routes.query import query_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dataset_bp)
    app.register_blueprint(query_bp)

    # 创建数据库和上传文件夹
    # app_context() 是 Flask 的上下文环境。只有在环境下，才能操作 db。
    with app.app_context():
        # 扫描所有继承了db.Model的类，并在数据库里创建对应的表。
        # 如果 database.db 不存在，它会自动创建。
        db.create_all()
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)