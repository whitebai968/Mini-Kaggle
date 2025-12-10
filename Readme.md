# Dataset House 开发全流程记录 (Development Process)

本项目是一个基于 Flask 的全栈 Web 应用，旨在提供 CSV 等格式的数据集的管理、上传、分析和 SQL 查询功能。以下是该项目的从零构建流程及核心代码实现。

---

```text
Mini-Kaggle/
├── app.py                  # 应用入口 (Flask App Initialization)
├── models.py               # 数据库模型 (User, DatasetMetadata)
├── requirements.txt        # Python 依赖列表
├── instance/               # 实例文件夹 (不上传到 Git)
│   └── database.db         # SQLite 数据库文件
├── static/                 # 静态资源
│   ├── css/
│   │   └── style.css       # 全局样式表
│   └── images/
│       └── logo.png        # 项目 Logo
├── templates/              # HTML 模板 (Jinja2)
│   ├── base.html           # 基础布局 (可选)
│   ├── Login.html          # 登录页
│   ├── register.html       # 注册页
│   ├── datasets.html       # 数据集列表 (Dashboard)
│   ├── dataset-create.html # 上传/创建页
│   ├── dataset-edit.html   # 编辑/删除页
│   ├── dataset-query.html  # SQL 查询页
│   └── messages.html       # 闪现消息组件
├── uploads/                # 用户上传的文件存储目录
└── routes/                 # 业务逻辑 (Blueprints)
    ├── auth.py             # 认证模块 (登录/注册)
    ├── dataset.py          # 数据集核心逻辑 (CRUD)
    └── query.py            # SQL 查询逻辑
```

---

## 第一阶段：地基与环境 (Infrastructure & Data)

### 1. `requirements.txt`
- **动作**：首先定义项目需要哪些工具（Flask, Pandas, SQLAlchemy）。
- **理由**：没有这些包，一行代码都运行不起来。

### 2. `models.py`
- **动作**：设计数据库结构 (`User` 和 `DatasetMetadata`)。
- **理由**：这是整个项目的“灵魂”。如果你不知道用户长什么样、数据集包含哪些字段（行数、表名、路径），你就无法编写注册逻辑或上传逻辑。

### 3. `app.py` 
- **动作**：初始化 Flask 应用，配置数据库连接 (`sqlite:///database.db`)，设置 `UPLOAD_FOLDER`。
- **理由**：这是“启动器”。写完这个，就可以运行 `python app.py` 来生成 `instance/database.db` 数据库文件，测试环境是否通畅。

---

## 第二阶段：用户认证模块 (Authentication Module)

### 4. `routes/auth.py`
- **动作**：编写 `/login` 和 `/register` 的后端逻辑。
- **理由**：任何功能（上传、查询）都需要 `current_user`。没有用户系统，后面的功能无法测试。

### 5. `templates/register.html` 和 `templates/Login.html`
- **动作**：编写表单前端。
- **理由**：配合 `auth.py` 进行联调。
    > *测试点：注册一个用户，查看数据库是否真的生成了记录。*

---

## 第三阶段：核心业务 - 数据集管理 (Core Feature - Dataset)

### 6. `routes/dataset.py` (上传与列表部分)
- **动作**：编写 `create` (上传) 和 `dashboard` (列表) 的逻辑。
- **理由**：这是最难的部分，也是项目的核心价值。需要处理流程：文件上传 -> Pandas 读取 -> 存入 SQLite -> 写入 `DatasetMetadata` 表。

### 7. `templates/dataset-create.html` 和 `templates/datasets.html`
- **动作**：编写上传页面和展示列表。
- **理由**：联调上传功能。
    > *测试点：上传一个 CSV，看列表页能不能显示出 Rows, Columns 等推断信息。*

### 8. `routes/dataset.py` (编辑与下载部分) + `templates/dataset-edit.html`
- **动作**：补充 `edit` (修改/删除) 和 `download` 路由。
- **理由**：这是对核心功能的完善（CRUD 中的 Update 和 Delete）。

---

## 第四阶段：高级功能 - 查询控制台 (Advanced Feature - Query)

### 9. `routes/query.py`
- **动作**：编写接收 SQL -> Pandas 执行 -> 返回 JSON/CSV 的逻辑。
- **理由**：这是一个独立的功能模块，依赖于“已有数据集表”存在，所以放在数据上传功能之后写。

### 10. `templates/dataset-query.html`
- **动作**：编写 SQL 输入框和结果展示区域。
- **理由**：测试输入 `SELECT * FROM ...` 是否能正确看到结果。

---

## 第五阶段：UI 优化与收尾 (UI Polish & Cleanup)

### 11. `templates/messages.html`
- **动作**：提取所有 `flash` 消息到一个独立文件。
- **理由**：代码复用。这时候回头把所有模板里的 `get_flashed_messages` 替换成这个 include。

### 12. `static/css/style.css`
- **动作**：为之前的纯 HTML 页面添加样式。
- **理由**：虽然在开发 HTML 时会写一些简单的 style，但最终的统一视觉风格（颜色、间距、布局）通常是最后调整的，以确保所有页面风格一致。