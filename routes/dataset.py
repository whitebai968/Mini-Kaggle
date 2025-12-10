import os
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from models import db, DatasetMetadata
from werkzeug.utils import secure_filename
from sqlalchemy import text

dataset_bp = Blueprint('dataset', __name__)
ALLOWED_EXTENSIONS = {'csv', 'txt'}

# 目前只允许 .csv 或 .txt 结尾的文件
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@dataset_bp.route('/')
@login_required # 只有登录用户才能看
def dashboard():
    # 获取所有数据集用于展示
    all_datasets = DatasetMetadata.query.all()
    return render_template('datasets.html', datasets=all_datasets)


@dataset_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        table_name = request.form.get('table_name')
        file = request.files.get('file')
        
        original_filename = file.filename if file else None 

        # 检查表名是否存在且不为空
        if not table_name:
            flash('Table name is required.', 'error-message')
            return redirect(url_for('dataset.create'))
        
        # 检查表名是否已存在于元数据中
        if DatasetMetadata.query.filter_by(table_name=table_name).first():
            flash(f'Table name "{table_name}" already exists. Please choose another name.', 'error-message')
            return redirect(url_for('dataset.create'))

        # 检查文件是否合格
        if file and allowed_file(file.filename):
            try:
                # 1. 保存文件到上传目录
                filename = secure_filename(f"{current_user.id}_{file.filename}")
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # 2. 读取文件并处理列名
                df = pd.read_csv(file_path, skipinitialspace=True)

                # 如果方案 A 只有 1 列，尝试用“空格”作为分隔符
                if df.shape[1] == 1:
                    try:
                        df_space = pd.read_csv(file_path, sep=r'\s+')
                        if df_space.shape[1] > 1:
                            df = df_space
                    except Exception:
                        pass # 保持原来的 df

                # 清洗列名
                df.columns = df.columns.str.replace('"', '').str.strip()

                # 3. 计算元数据
                row_count, col_count = df.shape

                def friendly_type(dtype):
                    d_str = str(dtype)
                    if 'int' in d_str: return 'int'
                    if 'float' in d_str: return 'float'
                    if 'object' in d_str: return 'str'
                    if 'bool' in d_str: return 'bool'
                    return d_str

                column_types = ", ".join([f"{col} ({friendly_type(dtype)})" for col, dtype in df.dtypes.items()])

                # 4. 导入数据到 SQLite 动态表
                # df.to_sql 直接把 DataFrame 里的数据倒进数据库，生成一张叫 table_name 的新表
                # if_exists='replace': 如果表存在就覆盖
                # index=False: 不把 pandas 的索引列存进去
                df.to_sql(table_name, con=db.engine, index=False, if_exists='fail')

                # 5. 保存数据集元数据
                new_dataset = DatasetMetadata(
                    name=name, description=description, table_name=table_name,
                    file_path=file_path, row_count=row_count, column_count=col_count,
                    column_types=column_types, owner=current_user,
                    original_filename=original_filename # 保存原始文件名
                )
                db.session.add(new_dataset)
                db.session.commit()
                
                flash('Dataset created successfully!', 'notification-message')
                return redirect(url_for('dataset.dashboard'))
                
            except Exception as e:
                # 文件处理或数据库插入失败
                flash(f'Error processing file or saving dataset: {e}', 'error-message')
                # 失败后重定向回创建页
                return redirect(url_for('dataset.create')) 
        
        # 文件不存在或文件类型不允许的情况
        flash('Invalid file or file type. Only CSV/TXT allowed.', 'error-message') 
        return redirect(url_for('dataset.create')) 

    return render_template('dataset-create.html')


@dataset_bp.route('/edit/<int:dataset_id>', methods=['GET', 'POST'])
@login_required
def edit(dataset_id):
    dataset = db.session.get(DatasetMetadata, dataset_id)
    # 如果当前登录的人(id) 不是这个数据的主人(owner_id)
    if not dataset or dataset.owner_id != current_user.id:
        # 统一找不到数据集或权限不足的类别
        flash('Dataset not found or you do not have permission to edit.', 'error-message') 
        return redirect(url_for('dataset.dashboard'))

    if request.method == 'POST':
        action = request.form.get('action') # 看用户点的是 save 还是 delete 按钮

        if action == 'delete':
            try:
                # ... 保持删除操作不变 ...
                db.session.commit()
                # 统一删除成功的类别
                flash('Dataset deleted.', 'notification-message') 
                return redirect(url_for('dataset.dashboard'))
            except Exception as e:
                # 统一删除失败的类别
                flash(f'Error deleting: {e}', 'error-message')
                # 删除失败，重定向回编辑页面，让用户重试或查看错误
                return redirect(url_for('dataset.edit', dataset_id=dataset_id)) 

        elif action == 'save':
            dataset.name = request.form.get('name')
            dataset.description = request.form.get('description')
            db.session.commit()
            # 统一保存成功的类别
            flash('Dataset updated.', 'notification-message') 
            return redirect(url_for('dataset.dashboard'))

    return render_template('dataset-edit.html', dataset=dataset)


@dataset_bp.route('/download/<int:dataset_id>')
@login_required
def download(dataset_id):
    dataset = DatasetMetadata.query.get_or_404(dataset_id)
    return send_file(dataset.file_path, as_attachment=True) # 告诉浏览器“这是一个附件，请弹窗让用户保存