from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import db, User
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import re

# 'auth' 是蓝图的名字，以后在 HTML 里用 url_for('auth.login') 来引用
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # 用户填完表单点击了提交按钮就是post
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('fullname')
        error = None

        # 1. 密码验证
        if len(password) <= 6:
            error = 'Password must be longer than 6 characters.'
        elif not re.search(r'[a-zA-Z]', password) or not re.search(r'[0-9]', password):
            error = 'Password must include both letters and numbers.'

        # 2. 邮箱重复检查
        # 虽然前端 HTML 里有 JS 验证，但后端必须再验一次，防止黑客绕过前端直接发包。
        user = User.query.filter_by(email=email).first()
        if user:
            error = 'Email already exists.' # 即使邮箱重复，也通过 error 变量统一处理

        # 统一错误处理
        if error:
            # 使用 CSS 中定义的 'error-message' 类别
            flash(error, 'error-message') 
            return redirect(url_for('auth.register')) # 失败后重定向回注册页

        # 注册成功
        hashed_pw = generate_password_hash(password)
        new_user = User(email=email, full_name=full_name, password=hashed_pw)
        
        db.session.add(new_user)
        db.session.commit()

        # 使用 CSS 中定义的 'notification-message' 类别
        flash('Registration successful! Please login.', 'notification-message')
        return redirect(url_for('auth.login'))

    # 如果是 GET 请求（用户刚打开网址），直接显示注册页面
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            # 登录成功后，在跳转到的页面(datasets.html)显示通知
            flash('Login successful!', 'notification-message') 
            return redirect(url_for('dataset.dashboard'))
        else:
            # 登录失败后，使用 'error-message' 类别并在当前页显示
            flash('Invalid email or password', 'error-message')
            # 保持在登录页
            
    # 无论 GET 还是 POST 失败，都渲染 Login.html
    return render_template('Login.html') 


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    # 使用 CSS 中定义的 'notification-message' 类别
    flash('You have been logged out.', 'notification-message') 
    return redirect(url_for('auth.login'))