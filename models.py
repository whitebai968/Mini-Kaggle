from flask_sqlalchemy import SQLAlchemy # flask 自带的操作数据库的工具，无需写增删改
from flask_login import UserMixin # flask的login插件，继承可以有get_id 和 is_authenticated等方法
from datetime import datetime

#初始化数据库工具
db = SQLAlchemy()


class User(UserMixin, db.Model): #继承UserMixin和db.Model
    # 用户信息需要存储的东西，包含登陆信息以及拥有的数据表
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    full_name = db.Column(db.String(150))
    # 用于将user与所拥有的数据表关联，后续user.datasets 就可以获取表
    datasets = db.relationship('DatasetMetadata', backref='owner', lazy=True)


class DatasetMetadata(db.Model):
    # 数据表在后端存储的信息
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(200))
    table_name = db.Column(db.String(100), unique=True, nullable=False)
    
    # 用于存储用户上传的原始文件名
    original_filename = db.Column(db.String(200)) 
    #数据内容基础信息
    row_count = db.Column(db.Integer)
    column_count = db.Column(db.Integer)
    column_types = db.Column(db.Text)
    #创建时间和Foreign key
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property #可以让一个函数以属性的形式被访问，如DatasetMetadata.owner_id 不需要加()
    def owner_id(self):
        return self.user_id