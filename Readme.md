# Dataset House 开发全流程记录 (Development Process)

This project is a full-stack Web application built with Flask, designed to provide dataset management, uploading, analysis, and SQL querying functionalities for CSV and similar formats. Below is the full development process and core implementation from scratch.
---

```text
Mini-Kaggle/
├── app.py                  # Application entry point (Flask initialization)
├── models.py               # Database models (User, DatasetMetadata)
├── requirements.txt        # Python dependency list
├── instance/               # Instance folder (not uploaded to Git)
│   └── database.db         # SQLite database file
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css       # Global stylesheet
│   └── images/
│       └── logo.png        # Project logo
├── templates/              # HTML templates (Jinja2)
│   ├── base.html           # Base layout (optional)
│   ├── Login.html          # Login page
│   ├── register.html       # Registration page
│   ├── datasets.html       # Dataset dashboard/list
│   ├── dataset-create.html # Dataset upload/create page
│   ├── dataset-edit.html   # Dataset edit/delete page
│   ├── dataset-query.html  # SQL query page
│   └── messages.html       # Flash message component
├── uploads/                # Directory for user-uploaded files
└── routes/                 # Business logic (Blueprints)
    ├── auth.py             # Authentication module (login/register)
    ├── dataset.py          # Dataset core logic (CRUD)
    └── query.py            # SQL query logic

```

## Quick Start

Follow these steps to set up and run the project locally.

### 1. Install Dependencies
Make sure you have Python installed. Run the following command to install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Change the config
Change .env file
```bash
LLM_API_KEY=""
LLM_BASE_URL=""
LLM_MODEL_NAME=""


SECRET_KEY="" # can be None
```

### 3. Run the Application

```bash
cd Your-Project-Folder
python app.py

```


---

## Phase 1: Infrastructure & Environment (Infrastructure & Data)

### 1. `requirements.txt`
- **Action**: First define which tools the project needs (Flask, Pandas, SQLAlchemy).
- **Reason**: Without these packages, not a single line of code can run.

### 2. `models.py`
- **Action**: Design the database structure (`User` and `DatasetMetadata`).
- **Reason**: This is the “core” of the entire project. If you don't know what the user model looks like or what fields a dataset contains (row count, table name, file path), you cannot write registration or upload logic.

### 3. `app.py`
- **Action**: Initialize the Flask application, configure the database connection (`sqlite:///database.db`), and set `UPLOAD_FOLDER`.
- **Reason**: This is the “launcher.” After writing this file, you can run `python app.py` to generate the `instance/database.db` database file and verify the environment works correctly.



## Phase 2: Authentication Module (Authentication Module)

### 4. `routes/auth.py`
- **Action**: Implement the backend logic for `/login` and `/register`.
- **Reason**: All features (upload, query) require `current_user`. Without a user system, later features cannot be tested.

### 5. `templates/register.html` and `templates/Login.html`
- **Action**: Build the frontend form pages.
- **Reason**: Used together with `auth.py` for integration testing.
    > *Test point: Register a user and check whether a record is actually created in the database.*



## Phase 3: Core Feature - Dataset Management (Core Feature - Dataset)

### 6. `routes/dataset.py` (Upload and List)
- **Action**: Implement the logic for `create` (upload) and `dashboard` (list).
- **Reason**: This is the most challenging part and the core value of the project. It must handle the workflow: file upload -> read with Pandas -> store into SQLite -> write into the `DatasetMetadata` table.

### 7. `templates/dataset-create.html` and `templates/datasets.html`
- **Action**: Build the upload page and the dataset list page.
- **Reason**: Used to test and integrate the upload functionality.
    > *Test point: Upload a CSV and check whether the list page displays inferred information such as Rows and Columns.*

### 8. `routes/dataset.py` (Edit and Download) + `templates/dataset-edit.html`
- **Action**: Add the `edit` (update/delete) and `download` routes.
- **Reason**: This completes the core functionality (Update and Delete in CRUD).




## Phase 4: Advanced Feature - Query Console (Advanced Feature - Query)

### 9. `routes/query.py`
- **Action**: Implement the logic to receive SQL -> execute via Pandas -> return JSON/CSV.
- **Reason**: This is an independent feature module, and it depends on dataset tables already existing, so it is implemented after the upload functionality.

### 10. `templates/dataset-query.html`
- **Action**: Build the SQL input box and the result display area.
- **Reason**: Used to test whether entering `SELECT * FROM ...` correctly displays the query results.


## Phase 5: UI Polish & Cleanup (UI Polish & Cleanup)

### 11. `templates/messages.html`
- **Action**: Extract all `flash` messages into a separate file.
- **Reason**: For code reuse. At this stage, replace all `get_flashed_messages` in templates with this include.

### 12. `static/css/style.css`
- **Action**: Add styling to the previously plain HTML pages.
- **Reason**: Although simple styles may have been written during HTML development, the final unified visual design (colors, spacing, layout) is typically adjusted at the end to ensure consistency across all pages.
