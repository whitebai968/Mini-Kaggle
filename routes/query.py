from flask import Blueprint, render_template, request
from flask_login import login_required
from models import db
import pandas as pd

query_bp = Blueprint('query', __name__)


@query_bp.route('/query', methods=['GET', 'POST'])
@login_required
def sql_query():
    query_result = None
    error = None

    if request.method == 'POST':
        # 修改: 前端 textarea name="sql_query"
        sql = request.form.get('sql_query')
        # 修改: 前端 radio name="format" (value="json" or "csv")
        fmt = request.form.get('format')

        try:
            # 使用 Pandas 执行 SQL
            df = pd.read_sql(sql, db.engine)

            if fmt == 'json':
                # orient='records': 变成 [{"col":"val"}, ...] 的格式，适合阅读
                # indent=2: 加缩进，让 JSON 漂亮点，不是挤成一团
                query_result = df.to_json(orient='records', indent=2)
            else:
                # 转成 CSV 字符串
                query_result = df.to_csv(index=False)

        except Exception as e:
            error = f"SQL Error: {str(e)}"

    return render_template('dataset-query.html', query_result=query_result, error=error)