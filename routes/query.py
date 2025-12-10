from flask import Blueprint, render_template, request
from flask_login import login_required
from models import db
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv
from models import DatasetMetadata


load_dotenv()
API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL")
MODEL_NAME = os.getenv("LLM_MODEL_NAME")

query_bp = Blueprint('query', __name__)


def get_ai_auto_sql(user_question, all_datasets):
    """
    具体逻辑：
    1. 接收所有表的元数据
    2. 让 AI 决定查哪张表
    3. 生成 SQL
    """
    if not API_KEY:
        raise ValueError("API Key missing!")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    # 构建全库图谱，把所有表的信息拼成一个长字符串告诉LLM
    schema_context = "Database Schema:\n"
    for ds in all_datasets:
        schema_context += f"""
            - Table Name: {ds.table_name}
              Description: {ds.description}
              Columns: {ds.column_types}
            """

    # 构建prompt
    prompt = f"""
        You are an intelligent Data Analyst. 
        Here is the schema of all available tables in the database:
        {schema_context}

        User Question: "{user_question}"

        Your Task:
        1. Analyze the user's question and the descriptions of the tables.
        2. Identify the SINGLE most relevant table.
        3. Write a SQL query for SQLite to answer the question using that table.

        Rules:
        1. Return ONLY the SQL string. No markdown, no explanations.
        2. Do not end with a semicolon.
        3. If the question cannot be answered by any table, return 'SELECT "No relevant data found"'
        """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful SQL assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0 # 让ai纯理性
        )
        sql = response.choices[0].message.content.strip()
        # 清洗可能存在的 Markdown 格式
        sql = sql.replace('```sql', '').replace('```', '').strip()
        return sql
    except Exception as e:
        raise Exception(f"LLM Error: {str(e)}")


@query_bp.route('/query', methods=['GET', 'POST'])
@login_required
def sql_query():
    query_result = None
    error = None
    generated_sql = None
    #获取所有数据集构建数据表图谱
    datasets = DatasetMetadata.query.all()
    if request.method == 'POST':
        user_input = request.form.get('sql_query')
        # 2. 获取模式
        mode = request.form.get('mode')
        # 3. 获取格式
        fmt = request.form.get('format')

        try:
            final_sql = ""
            if mode == 'ai':
                # AI 模式：把 user_input 当作自然语言问题
                if not datasets:
                    raise ValueError("No datasets available.")
                final_sql = get_ai_auto_sql(user_input, datasets)
                generated_sql = final_sql
            else:
                # SQL 模式：把 user_input 当作 SQL 代码
                final_sql = user_input

            # === 执行 ===
            df = pd.read_sql(final_sql, db.engine)

            if fmt == 'json':
                query_result = df.to_json(orient='records', indent=2)
            else:
                query_result = df.to_csv(index=False)

        except Exception as e:
            error = str(e)

    return render_template(
        'dataset-query.html',
        query_result=query_result,
        error=error,
        generated_sql=generated_sql,  # <--- 新增这行
        datasets=datasets
    )